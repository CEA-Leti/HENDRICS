/*
 * Copyright (C) 2025 CEA - All Rights Reserved
 * 
 * This program is free software: you can redistribute it and/or modify it under
 * the terms of the GNU General Public License as published by the Free Software
 * Foundation, either version 3 of the License, or (at your option) any later
 * version.
 * 
 * This program is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR
 * A PARTICULAR PURPOSE. See the GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License along with
 * this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

int main(void){
    char outbuf[512];
    char buffer[512];
    char pass[16];

    
    char *password="hendrics";

    printf("Password: ");
    fgets(pass, sizeof(pass), stdin); 
    pass[strlen(pass)-1]='\0';
    if(strcmp(pass,password)){

        sprintf(buffer, "ERR Wrong pass : %400s",pass);
        sprintf(outbuf, buffer);
        printf("Invalid password: %s\n",pass);
    }
    else {
        printf("Welcome, how are you ?\n");
    }
}
