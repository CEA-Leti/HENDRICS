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

"""Hydraulic cooling system simulation.

This module simulates a cooling system using water pumped through a closed circuit.
It includes logic for managing pump speed, temperature mixing, and flow monitoring,
all integrated with a broader hydropower process simulation environment.
"""

# coding: utf-8

import logging
import time

from scenarios.hydro.components import component, objects, turbine, levelRegulation
from simulator.variables import Field, FieldType

MIN_WATER_TEMPERATURE = 0.0  # °C
MAX_WATER_TEMPERATURE = 100.0  # °C

MIN_WARMING_TEMPERATURE = 0.0  # °C
MAX_WARMING_TEMPERATURE = 100.0  # °C

MIN_COOLING_TEMPERATURE = 0.0  # °C
MAX_COOLING_TEMPERATURE = 10.0  # °C

MAX_SSP_PO = 1500  # RPM
INITIAL_SSP_PO = 1500  # RPM

FACTOR_FT_EAU_REFR_ST_PO = 200
FACTOR_FT_EAU_REFR_ZT_VA_RGN = 100


class Cooling(component.Component):
    """Class representing the cooling process using a water pump and exchanger."""
    def __init__(
        self,
        env,
        waterPump,
        waterFlow,
        waterTemperature,
        warmingTemperature,
        coolingTemperature,
        syncCoupler,
        RGNValve,
        RGUExcitation,
        waterLevelAndFlow,
        SEPAM
    ):
        """Initialize the Cooling system.

        Args:
            env (simpy.Environment): Simulation environment.
            waterPump (WaterPump): Water pump controlling flow.
            waterFlow (WaterFlow): Measurement of water flow rate.
            waterTemperature (WaterTemperature): Current water temperature.
            warmingTemperature (WarmingTemperature): Heat source temp.
            coolingTemperature (CoolingTemperature): Heat sink temp.
            syncCoupler (SyncCoupler): Electrical sync logic.
            RGNValve (RGNValve): Flow control valve.
            RGUExcitation (RGUExcitation): Generator excitation.
            waterLevelAndFlow (WaterLevelAndFlow): Barrage state.
            SEPAM (SEPAM): Power and current monitoring unit.
        """
        super().__init__(env)

        self._waterPump = self._validate(waterPump, objects.WaterPump)
        self._waterFlow = self._validate(waterFlow, objects.WaterFlow)
        self._waterTemperature = self._validate(waterTemperature, objects.WaterTemperature)
        self._warmingTemperature = self._validate(warmingTemperature, objects.WarmingTemperature)
        self._coolingTemperature = self._validate(coolingTemperature, objects.CoolingTemperature)
        self._syncCoupler = self._validate(syncCoupler, objects.SyncCoupler)
        self._RGNValve = self._validate(RGNValve, objects.RGNValve)
        self._RGUExcitation = self._validate(RGUExcitation, objects.RGUExcitation)
        self._waterLevelAndFlow = self._validate(waterLevelAndFlow, objects.WaterLevelAndFlow)
        self._SEPAM = self._validate(SEPAM, objects.SEPAM)

    def _validate(self, obj, expected_type):
        """Validate the object type.

        Args:
            obj: Object to validate.
            expected_type: Expected class type.

        Returns:
            The validated object.

        Raises:
            ValueError: If type does not match.
        """
        if not isinstance(obj, expected_type):
            raise ValueError(obj)
        return obj

    def _updateWaterPump(self):
        """Update the pump speed and readback based on control command."""
        if self._waterPump.HYDRO_CMD_PO_EAU.value:
            self._waterPump.HYDRO_ST_PO_EAU.value = self._waterPump.HYDRO_SSP_PO_EAU.value
        else:
            self._waterPump.HYDRO_ST_PO_EAU.value = 0.0
        self._waterPump.HYDRO_RM_PO_EAU.value = self._waterPump.HYDRO_CMD_PO_EAU.value

    def _updateWaterFlow(self):
        """Update water flow measurement based on pump speed and valve position."""
        flow = self._waterPump.HYDRO_ST_PO_EAU.value / FACTOR_FT_EAU_REFR_ST_PO
        flow *= self._RGNValve.HYDRO_ZT_VA_RGN.value / FACTOR_FT_EAU_REFR_ZT_VA_RGN
        self._waterFlow.HYDRO_FT_EAU_REFR.value = flow

    def _updateWaterTemperature(self):
        """Mix water temperature based on pump speed and thermal sources."""
        factor = (self._waterPump.HYDRO_ST_PO_EAU.value / MAX_SSP_PO) / 3
        self._waterTemperature.HYDRO_TT_EAU.value = (
            (1-factor) * self._warmingTemperature.HYDRO_TT_ECHAUFF.value +
            factor * self._coolingTemperature.HYDRO_TT_EAU_REFR.value
        )

    def _updateWarmingTemperature(self):
        """Update warming temperature based on turbine speed influence."""
        self._warmingTemperature.HYDRO_TT_ECHAUFF.value = (
            self._waterTemperature.HYDRO_TT_EAU.value + self._RGNValve.HYDRO_ST_TURB.value * 0.01
        )

    def process(self):
        """Main process loop for the cooling simulation."""
        while True:
            self._updateWaterPump()
            self._updateWaterFlow()
            self._updateWaterTemperature()
            self._updateWarmingTemperature()
            yield self.env.timeout(self.UPDATE_TICK)
