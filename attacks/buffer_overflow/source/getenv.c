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

/* Code to determine the address of the content of an environment variable in the stack. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]) {
    char *ptr;

    if(argc < 2) {
        printf("Usage: %s <Environment variable name> \n", argv[0]);
        exit(EXIT_FAILURE);
    }

    ptr = getenv(argv[1]) + strlen(argv[0]); 

    printf("The address of the content of the environment variable '%s' is: %p\n", argv[1], ptr);

    return EXIT_SUCCESS;
}

