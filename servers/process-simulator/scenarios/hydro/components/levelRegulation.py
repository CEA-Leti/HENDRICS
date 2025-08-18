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

"""Simulation of a level regulation valve for hydropower applications.

This module simulates the control and monitoring of a barrage (dam) valve and water flow system.
It updates water levels and valve positions based on simulated control signals and system state.
"""

# coding: utf-8

import logging
from scenarios.hydro.components import component, objects
from simulator.variables import Field, FieldType

# Constants for simulation behavior
FACTOR = 0.5
MAX_WATER_LEVEL = 10.0
MIN_WATER_LEVEL = 0.0
INITIAL_WATER_LEVEL = 7.0
WATER_LEVEL_LOW = 6.0
WATER_LEVEL_HIGH = 8.0
K = 5000  # Conversion factor from flow to level
FT_IN = 75.0
ZT_VA_BARRAGE_openingTime = 8
ZT_VA_BARRAGE_MAX = 100
ZT_VA_BARRAGE_MIN = 0
ZT_VA_RGN_MAX = 100
ZT_VA_RGN_MIN = 0
ZT_VA_RGN_MIN_WORKING = 2
ZT_VA_RGN_INITIAL = 50
HEAD_VALVE_FLOW_FACTOR = 0.5
HAS_RANDOM_VALVES_IN_TEST = True


class LevelRegulation(component.Component):
    """Class representing a barrage valve with water level regulation logic."""
    def __init__(self, env, opened, waterLevelAndFlow, headValve, footValve, RGNValve):
        """Initialize the level regulation system.

        Args:
            env (simpy.Environment): Simulation environment.
            opened (Opened): Valve position controller object.
            waterLevelAndFlow (WaterLevelAndFlow): Water flow model.
            headValve (HeadValve): Head valve object.
            footValve (FootValve): Foot valve object.
            RGNValve (RGNValve): RGN valve object for controlled flow.
        """
        super().__init__(env)
        if not isinstance(opened, objects.Opened):
            raise ValueError(opened.name)
        self._opened = opened
        if not isinstance(waterLevelAndFlow, objects.WaterLevelAndFlow):
            raise ValueError(waterLevelAndFlow.name)
        self._waterLevelAndFlow = waterLevelAndFlow
        if not isinstance(headValve, objects.HeadValve):
            raise ValueError(headValve.name)
        self._headValve = headValve
        if not isinstance(footValve, objects.FootValve):
            raise ValueError(footValve.name)
        self._footValve = footValve
        if not isinstance(RGNValve, objects.RGNValve):
            raise ValueError(RGNValve.name)
        self._RGNValve = RGNValve

    def _updateOpened(self):
        """Update valve opening position and its sensor flags based on control commands."""
        if self._opened.HYDRO_CMDO_VA_BARRAGE.value:
            self._opened.HYDRO_ZT_VA_BARRAGE.value = min(
                ZT_VA_BARRAGE_MAX,
                self._opened.HYDRO_ZT_VA_BARRAGE.value + ZT_VA_BARRAGE_MAX / (ZT_VA_BARRAGE_openingTime/FACTOR)
            )
        elif self._opened.HYDRO_CMDC_VA_BARRAGE.value:
            self._opened.HYDRO_ZT_VA_BARRAGE.value = max(
                ZT_VA_BARRAGE_MIN,
                self._opened.HYDRO_ZT_VA_BARRAGE.value - ZT_VA_BARRAGE_MAX / (ZT_VA_BARRAGE_openingTime/FACTOR)
            )

        self._opened.HYDRO_ZSO_VA_BARRAGE.value = self._opened.HYDRO_ZT_VA_BARRAGE.value >= ZT_VA_BARRAGE_MAX
        self._opened.HYDRO_ZSC_VA_BARRAGE.value = self._opened.HYDRO_ZT_VA_BARRAGE.value <= ZT_VA_BARRAGE_MIN

    def _updateWaterLevelAndFlow(self):
        """Calculate water levels and flows based on valve positions and system state."""
        level_change = (
            self._waterLevelAndFlow.HYDRO_FT_IN_BARRAGE.value - self._waterLevelAndFlow.HYDRO_FT_VA_BARRAGE.value -
            self._waterLevelAndFlow.HYDRO_FT_VA_TETE.value
        ) / K

        current_level = self._waterLevelAndFlow.HYDRO_LT_EAU_BARRAGE.value
        new_level = max(MIN_WATER_LEVEL, min(MAX_WATER_LEVEL, current_level + level_change))
        self._waterLevelAndFlow.HYDRO_LT_EAU_BARRAGE.value = new_level

        self._waterLevelAndFlow.HYDRO_FT_VA_BARRAGE.value = self._opened.HYDRO_ZT_VA_BARRAGE.value

        valid_head = not self._headValve.HYDRO_ZSC_VA_TETE.value
        valid_foot = not self._footValve.HYDRO_ZSC_VA_PIED.value
        sufficient_rgn = self._RGNValve.HYDRO_ZT_VA_RGN.value >= ZT_VA_RGN_MIN_WORKING
        has_water = self._waterLevelAndFlow.HYDRO_LT_EAU_BARRAGE.value >= MIN_WATER_LEVEL

        if valid_head and valid_foot and sufficient_rgn and has_water:
            self._waterLevelAndFlow.HYDRO_FT_VA_TETE.value = (
                HEAD_VALVE_FLOW_FACTOR * self._RGNValve.HYDRO_ZT_VA_RGN.value
            )
        else:
            self._waterLevelAndFlow.HYDRO_FT_VA_TETE.value = 0.0

    def process(self):
        """Main simulation loop for level regulation."""
        while True:
            self._updateWaterLevelAndFlow()
            self._updateOpened()
            yield self.env.timeout(self.UPDATE_TICK)
