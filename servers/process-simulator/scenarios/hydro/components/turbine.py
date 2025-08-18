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

"""Hydropower turbine simulation class.

This module defines the behavior of a hydropower turbine, including
its valves, excitation control, and electrical coupling. It is intended
for industrial simulation and educational purposes, particularly for
dam and hydroelectric system emulation.
"""

# coding: utf-8

import time
import math
import logging
import simpy
import matplotlib.pyplot as plt
from tqdm import tqdm
from simulator.variables import FieldType, Field
from scenarios.hydro.components import component, objects, levelRegulation

# Constants related to turbine and generator dynamics
FACTOR = 0.5
ZT_VA_TETE_openingTime = 3  # seconds
ZT_VA_TETE_MAX = 100  # %
ZT_VA_TETE_MIN = 0  # %
ZT_VA_PIED_openingTime = 3  # seconds
ZT_VA_PIED_MAX = 100  # %
ZT_VA_PIED_MIN = 0  # %
ZT_VA_RGN_INITIAL = 0
ST_TURB_MIN = 0  # RPM
ST_TURB_MAX = 1500  # RPM
FACTOR_FT_VA_TETE_ST_TURB = 300
FACTOR_ST_TURB_FQT_ALTERN = 30  # RPM to Hz
COUPLAGE_MIN = 49  # Hz
COUPLAGE_MAX = 51  # Hz
VSP_ALTERN_INITIAL = 0  # V
VSP_ALTERN_EXCITATING_TENSION = 50  # V


class Turbine(component.Component):
    """Turbine process component simulating valve, excitation and output dynamics."""
    def __init__(self, env, headValve, footValve, RGNValve, RGUExcitation, syncCoupler, waterLevelAndFlow, SEPAM):
        """Initialize turbine with all electrical, hydraulic and control subcomponents.

        Args:
            env (simpy.Environment): Simulation environment.
            headValve (HeadValve): Head valve component.
            footValve (FootValve): Foot valve component.
            RGNValve (RGNValve): Rotor speed controller.
            RGUExcitation (RGUExcitation): Generator voltage controller.
            syncCoupler (SyncCoupler): Electrical coupling logic.
            waterLevelAndFlow (WaterLevelAndFlow): Flow and reservoir monitoring.
            SEPAM (SEPAM): Output metering and protection device.
        """
        super().__init__(env)
        for comp, cls in zip(
            [headValve, footValve, RGNValve, RGUExcitation, syncCoupler, waterLevelAndFlow, SEPAM],
            [objects.HeadValve, objects.FootValve, objects.RGNValve, objects.RGUExcitation,
             objects.SyncCoupler, objects.WaterLevelAndFlow, objects.SEPAM]
        ):
            if not isinstance(comp, cls):
                raise ValueError(comp)

        self._headValve = headValve
        self._footValve = footValve
        self._RGNValve = RGNValve
        self._RGUExcitation = RGUExcitation
        self._syncCoupler = syncCoupler
        self._waterLevelAndFlow = waterLevelAndFlow
        self._SEPAM = SEPAM
        self._headValvePosition = ZT_VA_TETE_MIN
        self._footValvePosition = ZT_VA_PIED_MIN

    def _updateHeadValve(self):
        """Update head valve position based on open/close commands."""
        if self._headValve.HYDRO_CMDO_VA_TETE.value:
            self._headValvePosition = min(
                ZT_VA_TETE_MAX,
                self._headValvePosition + (ZT_VA_TETE_MAX / (ZT_VA_TETE_openingTime/FACTOR))
            )
        elif self._headValve.HYDRO_CMDC_VA_TETE.value:
            self._headValvePosition = max(
                ZT_VA_TETE_MIN,
                self._headValvePosition - (ZT_VA_TETE_MAX / (ZT_VA_TETE_openingTime/FACTOR))
            )

        self._headValve.HYDRO_ZSO_VA_TETE.value = self._headValvePosition >= ZT_VA_TETE_MAX
        self._headValve.HYDRO_ZSC_VA_TETE.value = self._headValvePosition <= ZT_VA_TETE_MIN

    def _updateFootValve(self):
        """Update foot valve position based on open/close commands."""
        if self._footValve.HYDRO_CMDO_VA_PIED.value:
            self._footValvePosition = min(
                ZT_VA_PIED_MAX,
                self._footValvePosition + (ZT_VA_PIED_MAX / (ZT_VA_PIED_openingTime/FACTOR))
            )
        elif self._footValve.HYDRO_CMDC_VA_PIED.value:
            self._footValvePosition = max(
                ZT_VA_PIED_MIN,
                self._footValvePosition - (ZT_VA_PIED_MAX / (ZT_VA_PIED_openingTime/FACTOR))
            )

        self._footValve.HYDRO_ZSO_VA_PIED.value = self._footValvePosition >= ZT_VA_PIED_MAX
        self._footValve.HYDRO_ZSC_VA_PIED.value = self._footValvePosition <= ZT_VA_PIED_MIN

    def _updateRGNValve(self):
        """Compute turbine speed from water flow and set in RGNValve."""
        if self._RGNValve.HYDRO_ZT_VA_RGN.value > levelRegulation.ZT_VA_RGN_MIN_WORKING:
            if (
                FACTOR_FT_VA_TETE_ST_TURB * self._waterLevelAndFlow.HYDRO_FT_VA_TETE.value
            ) <= ST_TURB_MAX or not self._syncCoupler.HYDRO_AUTORIZ_CPL.value:
                self._RGNValve.HYDRO_ST_TURB.value = FACTOR_FT_VA_TETE_ST_TURB * self._waterLevelAndFlow.HYDRO_FT_VA_TETE.value
            else:
                self._RGNValve.HYDRO_ST_TURB.value = ST_TURB_MAX
        else:
            self._RGNValve.HYDRO_ST_TURB.value = ST_TURB_MIN

    def _updateRGUExcitation(self):
        """Update alternator frequency and voltage from turbine speed and excitation."""
        self._RGUExcitation.HYDRO_FQT_ALTERN.value = self._RGNValve.HYDRO_ST_TURB.value / FACTOR_ST_TURB_FQT_ALTERN
        self._RGUExcitation.HYDRO_VT_ALTERN.value = self._RGUExcitation.HYDRO_VSP_ALTERN.value

    def _updateSyncCoupler(self):
        """Set synchronization authorization if frequency is within range."""
        freq = self._RGUExcitation.HYDRO_FQT_ALTERN.value
        self._syncCoupler.HYDRO_AUTORIZ_CPL.value = COUPLAGE_MIN < freq < COUPLAGE_MAX

    def _updateSEPAM(self):
        """Calculate output current and power using mechanical/electrical efficiency."""
        M_VOL_EAU = 1000  # kg/m^3
        GRAV = 9.81  # m/s^2
        HAUTEUR = 15  # m
        RENDEMENT_ELEC = 0.85
        RENDEMENT_MECA = 0.9
        FACTEUR_PUISSANCE = 0.89
        TENSION_SORTIE = 5000  # V

        pMeca = M_VOL_EAU * GRAV * HAUTEUR * RENDEMENT_MECA * self._waterLevelAndFlow.HYDRO_FT_VA_TETE.value
        if self._syncCoupler.HYDRO_AUTORIZ_CPL.value:
            self._SEPAM.HYDRO_JT_ALTERN.value = RENDEMENT_ELEC * pMeca / 1e3
        else:
            self._SEPAM.HYDRO_JT_ALTERN.value = 0

        if self._RGUExcitation.HYDRO_VSP_ALTERN.value != 0:
            courant = self._SEPAM.HYDRO_JT_ALTERN.value / (math.sqrt(3) * TENSION_SORTIE * FACTEUR_PUISSANCE) * 1e3
        else:
            courant = 0

        self._SEPAM.COURANT1.value = courant
        self._SEPAM.COURANT2.value = courant
        self._SEPAM.COURANT3.value = courant
        self._SEPAM.FREQ.value = self._RGUExcitation.HYDRO_FQT_ALTERN.value

    def process(self):
        """Main turbine update cycle."""
        while True:
            self._updateHeadValve()
            self._updateFootValve()
            self._updateRGNValve()
            self._updateRGUExcitation()
            self._updateSyncCoupler()
            self._updateSEPAM()
            yield self.env.timeout(self.UPDATE_TICK)
