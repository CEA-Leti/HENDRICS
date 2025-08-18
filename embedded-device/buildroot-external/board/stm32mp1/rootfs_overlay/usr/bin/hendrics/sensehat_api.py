# Copyright (C) 2025 CEA - All Rights Reserved
# 
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import numpy as np

from logger_settings import setup_logger 

logger = setup_logger()

# Predefined matrices representing numbers from 0 to 9 on a 3x5 grid.
mat_0 = np.array([
[1,1,1],
[1,0,1],
[1,0,1],
[1,0,1],
[1,1,1]])

mat_1 = np.array([
[0,1,1],
[0,0,1],
[0,0,1],
[0,0,1],
[0,0,1]])

mat_2 = np.array([
[1,1,1],
[0,0,1],
[1,1,1],
[1,0,0],
[1,1,1]])

mat_3 = np.array([
[1,1,1],
[0,0,1],
[1,1,1],
[0,0,1],
[1,1,1]])

mat_4 = np.array([
[0,0,1],
[0,0,1],
[0,0,1],
[1,1,1],
[0,1,0]])

mat_5 = np.array([
[1,1,1],
[1,0,0],
[1,1,1],
[0,0,1],
[1,1,1]])

mat_6 = np.array([
[1,1,1],
[1,0,0],
[1,1,1],
[1,0,1],
[1,1,1]])

mat_7 = np.array([
[1,1,1],
[0,0,1],
[0,1,1],
[0,0,1],
[0,0,1]])

mat_8 = np.array([
[1,1,1],
[1,0,1],
[1,1,1],
[1,0,1],
[1,1,1]])

mat_9 = np.array([
[1,1,1],
[1,0,1],
[1,1,1],
[0,0,1],
[1,1,1]])

mat_comp = [mat_0, mat_1, mat_2, mat_3, mat_4, mat_5, mat_6, mat_7, mat_8, mat_9]

# Utility Functions :
def compute_matrix(number):
    """Compute the visual matrix representation of a number between 0 and 99."""

    if (number < 0) or (number > 99) : 
        logger.warning("Cannot display numbers below 0 or above 99. Automatically setting number to 0.")
        number = 0

    [unit_v, dozen_v] = [number%10, number//10]
    dozen = np.pad(mat_comp[dozen_v], ((1,2) , (0,5)), mode = 'constant', constant_values=(0, 0))
    unit = np.pad(mat_comp[unit_v], ((1,2) , (4,1)), mode = 'constant', constant_values=(0, 0))
    return dozen + unit


def colour_grad(minimum, maximum, value):
    minimum, maximum = float(minimum), float(maximum)
    ratio = 2 * (value-minimum) / (maximum - minimum)
    b = int(max(0, 255*(1 - ratio)))
    g = int(max(0, 255*(ratio - 1)))
    r = 255 - b - g
    return r, g, b	
		

def twos_complement(hexadecimal,taille):
    """Calculate the two's complement of a hexadecimal number."""
    integer = int(hexadecimal, 16)
    mask = int('0x'+('F' * taille), 16)
    one_complement = ~integer & mask
    tow_complement = (one_complement + 1)
    return tow_complement


def calcul_signed_int(hexadecimal):
    """Convert a hexadecimal string to a signed integer."""
    if (hexadecimal[0]=="8" or hexadecimal[0]=="9" or hexadecimal[0]=="a" or hexadecimal[0]=="b" or hexadecimal[0]=="c" or hexadecimal[0]=="d" or hexadecimal[0]=="e" or hexadecimal[0]=="f"):
        value = twos_complement(hexadecimal,4)*(-1)
    else:
        value = int(hexadecimal, 16)
    return value




# Data Extraction Functions :
def init():
    """Initialize and calibrate temperature and humidity measurements."""

    # Calibrate temperature measurements.
    # Read temperature from the pressure sensor.
    os.system("i2cset -y 1 0x5c 0x20 0xc4")
    os.system("i2cset -y 1 0x5c 0x21 0x40")

    # Read temperature from the humidity sensor.
    os.system("i2cset -y 1 0x5f 0x20 0x1b")
    os.system("i2cset -y 1 0x5f 0x20 0x87")

    # Calculate T0_OUT.
    T0_OUT_bit_msb = os.popen("i2cget -y 1 0x5F 0x3D").read()
    T0_OUT_bit_lsb = os.popen("i2cget -y 1 0x5F 0x3C").read()

    T0_OUT_hex_bit_msb = T0_OUT_bit_msb[2:-1]
    T0_OUT_hex_bit_lsb = T0_OUT_bit_lsb[2:-1]

    T0_OUT_hex_total = T0_OUT_hex_bit_msb + T0_OUT_hex_bit_lsb

    # Convert T0_OUT to signed integer
    T0_OUT = calcul_signed_int(T0_OUT_hex_total)

    # Calculate T1_OUT
    T1_OUT_bit_msb = os.popen("i2cget -y 1 0x5F 0x3F").read()
    T1_OUT_bit_lsb = os.popen("i2cget -y 1 0x5F 0x3E").read()
    
    T1_OUT_hex_bit_msb = T1_OUT_bit_msb[2:-1]
    T1_OUT_hex_bit_lsb = T1_OUT_bit_lsb[2:-1]

    T1_OUT_hex_total = T1_OUT_hex_bit_msb + T1_OUT_hex_bit_lsb

    # Convert T1_OUT to signed integer
    T1_OUT = calcul_signed_int(T1_OUT_hex_total)

    # Retrieve additional bits for T1_degC and T0_degC.
    bits_supp = os.popen("i2cget -y 1 0x5F 0x35").read()
    bits_supp_hex = bits_supp[3:-1]
    bits_supp_int = int(bits_supp_hex, 16)
    bits_supp = format(bits_supp_int, '0>4b')

    T1_bits_supp = int(bits_supp[:-2], 2)
    T0_bits_supp = int(bits_supp[2:], 2)

    # Calculate T0_degC_x8
    T0_degC_x8 = os.popen("i2cget -y 1 0x5F 0x32").read()

    T0_degC_x8_hex = str(T0_bits_supp) + T0_degC_x8[2:-1]
    T0_degC_x8 = int(T0_degC_x8_hex, 16)
    T0_degC = T0_degC_x8/8

    # Calculate T1_degC_x8#Calibrating Humidity
    T1_degC_x8 = os.popen("i2cget -y 1 0x5F 0x33").read()

    T1_degC_x8_hex = str(T1_bits_supp) + T1_degC_x8[2:-1]
    T1_degC_x8 = int(T1_degC_x8_hex, 16)
    T1_degC = T1_degC_x8/8
    
    # Create correlation array for temperature measurements.
    if (T1_OUT < T0_OUT):
        values = np.linspace(T0_degC, T1_degC, T0_OUT-T1_OUT)
    else:
        values = np.linspace(T0_degC, T1_degC, T1_OUT-T0_OUT)

    # Save the temperature correlation array to a file.
    np.save("/usr/bin/hendrics/saveTemp.npy", values)


    # Calibrating humidity measurements.
    # Retrieve and calculate H0_OUT (first humidity output).
    H0_OUT_bit_msb = os.popen("i2cget -y 1 0x5F 0x37").read()
    H0_OUT_bit_lsb = os.popen("i2cget -y 1 0x5F 0x36").read()

    H0_OUT_hex_bit_msb = H0_OUT_bit_msb[2:-1]
    H0_OUT_hex_bit_lsb = H0_OUT_bit_lsb[2:-1]

    H0_OUT_hex_total = H0_OUT_hex_bit_msb + H0_OUT_hex_bit_lsb

    # Convert H0_OUT to signed integer
    H0_OUT = calcul_signed_int(H0_OUT_hex_total)

    # Retrieve and calculate H1_OUT (second humidity output).
    H1_OUT_bit_msb = os.popen("i2cget -y 1 0x5F 0x3B").read()
    H1_OUT_bit_lsb = os.popen("i2cget -y 1 0x5F 0x3A").read()
    
    H1_OUT_hex_bit_msb = H1_OUT_bit_msb[2:-1]
    H1_OUT_hex_bit_lsb = H1_OUT_bit_lsb[2:-1]

    H1_OUT_hex_total = H1_OUT_hex_bit_msb + H1_OUT_hex_bit_lsb

    # Convert H1_OUT to signed integer
    H1_OUT = calcul_signed_int(H1_OUT_hex_total)

    # Calculate H0_rH_x2
    H0_rH_x2 = os.popen("i2cget -y 1 0x5F 0x30").read()

    H0_rH_x2_hex = H0_rH_x2[2:-1]
    H0_rH_x2 = int(H0_rH_x2_hex, 16)
    H0_rH = H0_rH_x2 / 2

    # Calculate H1_rH_x2
    H1_rH_x2 = os.popen("i2cget -y 1 0x5F 0x31").read()

    H1_rH_x2_hex = H1_rH_x2[2:-1]
    H1_rH_x2 = int(H1_rH_x2_hex, 16)
    H1_rH = H1_rH_x2 / 2
    
    # Create correlation array for humidity measurements.
    if (H1_OUT < H0_OUT):
        values = np.linspace(H0_rH, H1_rH, H0_OUT-H1_OUT)
    else:
        values = np.linspace(H0_rH, H1_rH, H1_OUT-H0_OUT)
    
    # Save the humidity correlation array to a file.
    np.save("/usr/bin/hendrics/saveHum.npy", values)


def get_pressure():
    """Retrieve the pressure value from the SensHat sensor via I2C communication."""
    output_bit_msb = os.popen("i2cget -y 1 0x5C 0x2A").read()
    output_bit_lsb = os.popen("i2cget -y 1 0x5C 0x29").read()
    output_bit_very_least_significant = os.popen("i2cget -y 1 0x5C 0x28").read()

    hex_bit_msb = output_bit_msb[2:-1]
    hex_bit_lsb = output_bit_lsb[2:-1]
    hex_bit_very_least_significant = output_bit_very_least_significant[2:-1]

    hex_total = hex_bit_msb + hex_bit_lsb + hex_bit_very_least_significant
    if (hex_total[0]=="8" or hex_total[0]=="9" or hex_total[0]=="a" or hex_total[0]=="b" or hex_total[0]=="c" or hex_total[0]=="d" or hex_total[0]=="e" or hex_total[0]=="f"):
        value = twos_complement(hex_total,6)
    else:
        value = int(hex_total, 16) / 4096
    return value


def get_temperature_from_pressure():
    """Retrieve the temperature value based on pressure sensor data via I2C communication."""
    output_bit_msb = os.popen("i2cget -y 1 0x5C 0x2C").read()
    output_bit_lsb = os.popen("i2cget -y 1 0x5C 0x2B").read()

    hex_bit_msb = output_bit_msb[2:-1]
    hex_bit_lsb = output_bit_lsb[2:-1]

    hex_total = hex_bit_msb + hex_bit_lsb
    value = 42.5 + calcul_signed_int(hex_total)/480

    return value


def get_temperature():
    """Retrieve the temperature value from the SensHat sensor via I2C communication."""

    # Calculate T_OUT
    T_OUT_bit_msb = os.popen("i2cget -y 1 0x5F 0x2B").read()
    T_OUT_bit_lsb = os.popen("i2cget -y 1 0x5F 0x2A").read()
    
    T_OUT_hex_bit_msb = T_OUT_bit_msb[2:-1]
    T_OUT_hex_bit_lsb = T_OUT_bit_lsb[2:-1]

    T_OUT_hex_total = T_OUT_hex_bit_msb + T_OUT_hex_bit_lsb
    T_OUT = calcul_signed_int(T_OUT_hex_total)

    # Calculate T0_OUT
    T0_OUT_bit_msb = os.popen("i2cget -y 1 0x5F 0x3D").read()
    T0_OUT_bit_lsb = os.popen("i2cget -y 1 0x5F 0x3C").read()

    T0_OUT_hex_bit_msb = T0_OUT_bit_msb[2:-1]
    T0_OUT_hex_bit_lsb = T0_OUT_bit_lsb[2:-1]

    T0_OUT_hex_total = T0_OUT_hex_bit_msb + T0_OUT_hex_bit_lsb

    # Convert T0_OUT to signed integer 
    T0_OUT = calcul_signed_int(T0_OUT_hex_total)

    # Calculate temperature
    values = np.load("/usr/bin/hendrics/saveTemp.npy")

    if (T_OUT<T0_OUT):
        if (T0_OUT>=0 and T_OUT>=0):
            value = values[abs(T0_OUT-T_OUT)]
        else:
            value = values[abs(T_OUT-T0_OUT)]
    else:
        if (T0_OUT<=0 and T_OUT>=0):
            value = values[abs(T_OUT+T0_OUT)]
        else:
            value = values[abs(T_OUT-T0_OUT)]

    return value


def get_humidity():
    """Retrieve the humidity value from the SensHat sensor via I2C communication."""

    # Calculate H_OUT
    H_OUT_bit_msb = os.popen("i2cget -y 1 0x5F 0x29").read()
    H_OUT_bit_lsb = os.popen("i2cget -y 1 0x5F 0x28").read()
    
    H_OUT_hex_bit_msb = H_OUT_bit_msb[2:-1]
    H_OUT_hex_bit_lsb = H_OUT_bit_lsb[2:-1]

    H_OUT_hex_total = H_OUT_hex_bit_msb + H_OUT_hex_bit_lsb
    H_OUT = calcul_signed_int(H_OUT_hex_total)

    # Calculate H0_OUT
    H0_OUT_bit_msb = os.popen("i2cget -y 1 0x5F 0x37").read()
    H0_OUT_bit_lsb = os.popen("i2cget -y 1 0x5F 0x36").read()

    H0_OUT_hex_bit_msb = H0_OUT_bit_msb[2:-1]
    H0_OUT_hex_bit_lsb = H0_OUT_bit_lsb[2:-1]

    H0_OUT_hex_total = H0_OUT_hex_bit_msb + H0_OUT_hex_bit_lsb

    # Convert H0_OUT to signed integer 
    H0_OUT = calcul_signed_int(H0_OUT_hex_total)
    
    # Calculate humidity
    values = np.load("/usr/bin/hendrics/saveHum.npy")        

    if (H_OUT<H0_OUT):
        if (H0_OUT>=0 and H_OUT>=0):
            value = values[abs(H0_OUT-H_OUT)]
        else:
            value = values[abs(H_OUT-H0_OUT)]
    else:
        if (H0_OUT<=0 and H_OUT>=0):
            value = values[abs(H_OUT+H0_OUT)]
        else:
            value = values[abs(H_OUT-H0_OUT)]

    return value




# Display Functions :
def Screen_value(value_temp):
    """Display the temperature value on the SensHat screen."""
    screen =  compute_matrix(value_temp)

    i = 0
    data = '0x00 '
    
    lum_r,lum_g,lum_b = colour_grad(0,50,value_temp)

    for y in screen :
            
            for x in y :
                    lum = x * lum_r
                    data += '0x%02x ' %(lum)
                    i += 1

            for x in y:
                    lum = x * lum_g
                    data += '0x%02x ' %(lum)
                    i += 1

            for x in y:
                    lum = x * lum_b
                    data += '0x%02x ' %(lum)
                    i += 1

    exit_code = os.system('i2ctransfer -f -y 1 w193@0x46 %s' %(data))
    if exit_code != 0:
         logger.error("Failed to execute 'i2ctransfer' command. Exit code: %d", exit_code)


def Screen_blank():
    """Clear the SensHat screen by setting all LEDs to off."""
    screen = [[0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0]]

    i = 0
    data = '0x00 '

    for y in screen :
            
            for x in y :
                    lum = (x * 63)//255
                    data += '0x%02x ' %(lum)
                    i += 1

            for j in range(8):
                    data += '0x00 '
                    i += 1

            for j in range(8):
                    data += '0x00 '

    exit_code = os.system('i2ctransfer -f -y 1 w193@0x46 %s' %(data))
    if exit_code != 0:
         logger.error("Failed to execute 'i2ctransfer' command. Exit code: %d", exit_code)

def Screen_OK():
    """Display 'OK' on the SensHat screen."""
    screen = [[0,0,255,255,255,255,0,0],
            [0,255,0,0,0,0,255,0],
            [255,0,0,0,0,0,0,255],
            [255,0,0,0,0,255,0,255],
            [255,0,255,0,255,0,0,255],
            [255,0,0,255,0,0,0,255],
            [0,255,0,0,0,0,255,0],
            [0,0,255,255,255,255,0,0]]

    i = 0
    data = '0x00 '

    for y in screen :

            for j in range(8):
                    data += '0x00 '
                    i += 1

            for x in y :
                    lum = (x * 63)//255
                    data += '0x%02x ' %(lum)
                    i += 1

            for j in range(8):
                    data += '0x00 '

    os.system('i2ctransfer -f -y 1 w193@0x46 %s' %(data))


def Screen_KO():
    """Display 'KO' on the SensHat screen."""
    screen = [[0,0,255,255,255,255,0,0],
            [0,255,0,0,0,0,255,0],
            [255,0,255,0,0,0,0,255],
            [255,0,0,255,0,0,0,255],
            [255,0,0,0,255,0,0,255],
            [255,0,0,0,0,255,0,255],
            [0,255,0,0,0,0,255,0],
            [0,0,255,255,255,255,0,0]]

    i = 0
    data = '0x00 '

    for y in screen :
            
            for x in y :
                    lum = (x * 63)//255
                    data += '0x%02x ' %(lum)
                    i += 1

            for j in range(8):
                    data += '0x00 '
                    i += 1

            for j in range(8):
                    data += '0x00 '

    os.system('i2ctransfer -f -y 1 w193@0x46 %s' %(data))
