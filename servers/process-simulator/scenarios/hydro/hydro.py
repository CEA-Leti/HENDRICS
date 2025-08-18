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

"""
Hydro scenario.
This script sets up and runs a simulation of a hydraulic power plant,
integrating various components like level regulation, a hydraulic
central, a cooling system, and a turbine.
"""

import argparse
import logging
import os

import simulator.process as process
from scenarios.hydro.components import (cooling, hydraulicCentral, levelRegulation, objects, turbine)
from simulator.variables import Field, FieldType

#############################################################
#   Main process                                            #
#############################################################

# Set up argument parser for command-line arguments.
parser = argparse.ArgumentParser(prog='Hydro Simulator',)
# Add argument for configuration file path.
parser.add_argument("-c", "--config", type=str)
args = parser.parse_args()

# Set default configuration file path if not provided.
if not args.config:
    args.config = "/opt/process-simulator/scenarios/hydro/config.toml"

# Initialize the simulation process with the specified configuration.
world = process.Process(
    config_file=args.config,
    verbose=True,
)

#############################################################
#   Building Level Regulation                               #
#############################################################

# Create an instance of the 'Opened' object, representing the barrage valve's open/closed status.
opened = objects.Opened(
    world.HYDRO_CMDO_VA_BARRAGE,
    world.HYDRO_CMDC_VA_BARRAGE,
    world.HYDRO_ZSO_VA_BARRAGE,
    world.HYDRO_ZSC_VA_BARRAGE,
    world.HYDRO_ZT_VA_BARRAGE,
)
# Create an instance of the 'WaterLevelAndFlow' object, representing water level and flow sensors.
water_level_and_flow = objects.WaterLevelAndFlow(
    world.HYDRO_LT_EAU_BARRAGE,
    world.HYDRO_FT_IN_BARRAGE,
    world.HYDRO_FT_VA_BARRAGE,
    world.HYDRO_FT_VA_TETE,
)

#############################################################
#   Building Hydraulic Central                              #
#############################################################

# Create an instance of the 'OilPump' object.
oil_pump = objects.OilPump(
    world.HYDRO_CMD_PO_HUILE,
    world.HYDRO_RM_PO_HUILE,
)
# Create an instance of the 'OilTemperature' object.
oil_temperature = objects.OilTemperature(world.HYDRO_TT_HUILE)

#############################################################
#   Building Cooler                                         #
#############################################################

# Create an instance of the 'WaterPump' object.
water_pump = objects.WaterPump(
    world.HYDRO_CMD_PO_EAU,
    world.HYDRO_RM_PO_EAU,
    world.HYDRO_ST_PO_EAU,
    world.HYDRO_SSP_PO_EAU,
)
# Create an instance of the 'WaterFlow' object.
water_flow = objects.WaterFlow(world.HYDRO_FT_EAU_REFR)
# Create an instance of the 'WaterTemperature' object.
water_temperature = objects.WaterTemperature(world.HYDRO_TT_EAU)
# Create an instance of the 'WarmingTemperature' object.
warming_temperature = objects.WarmingTemperature(world.HYDRO_TT_ECHAUFF)
# Create an instance of the 'CoolingTemperature' object.
cooling_temperature = objects.CoolingTemperature(world.HYDRO_TT_EAU_REFR)

#############################################################
#   Building Turbine                                        #
#############################################################

# Create an instance of the 'HeadValve' object.
head_valve = objects.HeadValve(
    world.HYDRO_CMDO_VA_TETE,
    world.HYDRO_CMDC_VA_TETE,
    world.HYDRO_ZSO_VA_TETE,
    world.HYDRO_ZSC_VA_TETE,
)
# Create an instance of the 'FootValve' object.
foot_valve = objects.FootValve(
    world.HYDRO_CMDO_VA_PIED,
    world.HYDRO_CMDC_VA_PIED,
    world.HYDRO_ZSO_VA_PIED,
    world.HYDRO_ZSC_VA_PIED,
)
# Create an instance of the 'RGNValve' object.
rgn_valve = objects.RGNValve(
    world.HYDRO_ST_TURB,
    world.HYDRO_ZT_VA_RGN,
)
# Create an instance of the 'RGUExcitation' object.
rgu_excitation = objects.RGUExcitation(
    world.HYDRO_VT_ALTERN,
    world.HYDRO_FQT_ALTERN,
    world.HYDRO_VSP_ALTERN,
)
# Create an instance of the 'SyncCoupler' object.
sync_coupler = objects.SyncCoupler(
    world.HYDRO_CMD_COUPLAGE,
    world.HYDRO_AUTORIZ_CPL,
)
# Create an instance of the 'SEPAM' object.
sepam = objects.SEPAM(
    world.HYDRO_JT_ALTERN,
    world.HYDRO_FREQ,
    world.HYDRO_COURANT1,
    world.HYDRO_COURANT2,
    world.HYDRO_COURANT3,
    world.HYDRO_SHIFT,
)

#############################################################
#   Main components                                         #
#############################################################

# Instantiate the LevelRegulation component.
level_regulation = levelRegulation.LevelRegulation(
    world.env,
    opened,
    water_level_and_flow,
    head_valve,
    foot_valve,
    rgn_valve,
)
# Instantiate the HydraulicCentral component.
hydraulic_central = hydraulicCentral.HydraulicCentral(
    world.env,
    oil_pump,
    oil_temperature,
)
# Instantiate the Cooling component.
cooling = cooling.Cooling(
    world.env,
    water_pump,
    water_flow,
    water_temperature,
    warming_temperature,
    cooling_temperature,
    sync_coupler,
    rgn_valve,
    rgu_excitation,
    water_level_and_flow,
    sepam,
)
# Instantiate the Turbine component.
turbine = turbine.Turbine(
    world.env,
    head_valve,
    foot_valve,
    rgn_valve,
    rgu_excitation,
    sync_coupler,
    water_level_and_flow,
    sepam,
)

# Entry point for running the simulation.
if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)  # Configure basic logging.
    world.run()  # Run the simulation.
