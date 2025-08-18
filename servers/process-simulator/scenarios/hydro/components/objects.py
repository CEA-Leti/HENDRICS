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

# coding: utf-8

from simulator.variables import Field, FieldType


class Opened:
    """Represents the open/closed status and commands for a barrage valve.

    Attributes:
        HYDRO_ZSO_VA_BARRAGE (DigitalInput): Digital input for valve open limit switch.
        HYDRO_ZSC_VA_BARRAGE (DigitalInput): Digital input for valve closed limit switch.
        HYDRO_CMDO_VA_BARRAGE (DigitalOutput): Digital output to command valve opening.
        HYDRO_CMDC_VA_BARRAGE (DigitalOutput): Digital output to command valve closing.
        HYDRO_ZT_VA_BARRAGE (AnalogInput): Analog input for barrage valve position sensor.
    """
    HYDRO_ZSO_VA_BARRAGE = None  # Digital Input (DI)
    HYDRO_ZSC_VA_BARRAGE = None  # Digital Input (DI)
    HYDRO_CMDO_VA_BARRAGE = None  # Digital Output (DO)
    HYDRO_CMDC_VA_BARRAGE = None  # Digital Output (DO)
    HYDRO_ZT_VA_BARRAGE = None  # Barrage valve position sensor

    def __init__(
        self,
        HYDRO_CMDO_VA_BARRAGE,
        HYDRO_CMDC_VA_BARRAGE,
        HYDRO_ZSO_VA_BARRAGE,
        HYDRO_ZSC_VA_BARRAGE,
        HYDRO_ZT_VA_BARRAGE
    ):
        """Initializes the Opened class.

        Args:
            HYDRO_CMDO_VA_BARRAGE (DigitalOutput): Digital output to command valve opening.
            HYDRO_CMDC_VA_BARRAGE (DigitalOutput): Digital output to command valve closing.
            HYDRO_ZSO_VA_BARRAGE (DigitalInput): Digital input for valve open limit switch.
            HYDRO_ZSC_VA_BARRAGE (DigitalInput): Digital input for valve closed limit switch.
            HYDRO_ZT_VA_BARRAGE (AnalogInput): Analog input for barrage valve position sensor.
        """
        self.HYDRO_CMDO_VA_BARRAGE = HYDRO_CMDO_VA_BARRAGE
        self.HYDRO_CMDC_VA_BARRAGE = HYDRO_CMDC_VA_BARRAGE
        self.HYDRO_ZSO_VA_BARRAGE = HYDRO_ZSO_VA_BARRAGE
        self.HYDRO_ZSC_VA_BARRAGE = HYDRO_ZSC_VA_BARRAGE
        self.HYDRO_ZT_VA_BARRAGE = HYDRO_ZT_VA_BARRAGE


class WaterLevelAndFlow:
    """Represents sensors for water level and flow at the barrage.

    Attributes:
        HYDRO_LT_EAU_BARRAGE (AnalogInput): Analog input for barrage water level sensor.
        HYDRO_FT_IN_BARRAGE (AnalogInput): Analog input for incoming barrage water flow sensor.
        HYDRO_FT_VA_BARRAGE (AnalogInput): Analog input for barrage valve outlet water flow sensor.
        HYDRO_FT_VA_TETE (AnalogInput): Analog input for head valve outlet water flow measurement.
    """
    HYDRO_LT_EAU_BARRAGE = None  # Barrage water level sensor (AI)
    HYDRO_FT_IN_BARRAGE = None  # Incoming barrage water flow sensor (AI)
    HYDRO_FT_VA_BARRAGE = None  # Barrage valve outlet water flow sensor (AI)
    HYDRO_FT_VA_TETE = None  # Head valve outlet water flow measurement (AI)

    def __init__(self, HYDRO_LT_EAU_BARRAGE, HYDRO_FT_IN_BARRAGE, HYDRO_FT_VA_BARRAGE, HYDRO_FT_VA_TETE):
        """Initializes the WaterLevelAndFlow class.

        Args:
            HYDRO_LT_EAU_BARRAGE (AnalogInput): Analog input for barrage water level sensor.
            HYDRO_FT_IN_BARRAGE (AnalogInput): Analog input for incoming barrage water flow sensor.
            HYDRO_FT_VA_BARRAGE (AnalogInput): Analog input for barrage valve outlet water flow sensor.
            HYDRO_FT_VA_TETE (AnalogInput): Analog input for head valve outlet water flow measurement.
        """
        self.HYDRO_LT_EAU_BARRAGE = HYDRO_LT_EAU_BARRAGE
        self.HYDRO_FT_IN_BARRAGE = HYDRO_FT_IN_BARRAGE
        self.HYDRO_FT_VA_BARRAGE = HYDRO_FT_VA_BARRAGE
        self.HYDRO_FT_VA_TETE = HYDRO_FT_VA_TETE


class OilPump:
    """Represents the oil pump controls and status.

    Attributes:
        HYDRO_RM_PO_HUILE (DigitalInput): Digital input for oil pump running feedback.
        HYDRO_CMD_PO_HUILE (DigitalOutput): Digital output to command oil pump ON/OFF.
    """
    HYDRO_RM_PO_HUILE = None  # Oil pump running feedback (DI)
    HYDRO_CMD_PO_HUILE = None  # Oil pump motor ON/OFF command (DO)

    def __init__(self, HYDRO_CMD_PO_HUILE, HYDRO_RM_PO_HUILE):
        """Initializes the OilPump class.

        Args:
            HYDRO_CMD_PO_HUILE (DigitalOutput): Digital output to command oil pump ON/OFF.
            HYDRO_RM_PO_HUILE (DigitalInput): Digital input for oil pump running feedback.
        """
        self.HYDRO_CMD_PO_HUILE = HYDRO_CMD_PO_HUILE
        self.HYDRO_RM_PO_HUILE = HYDRO_RM_PO_HUILE


class OilTemperature:
    """Represents the oil temperature sensor.

    Attributes:
        HYDRO_TT_HUILE (AnalogInput): Analog input for oil temperature sensor.
    """
    HYDRO_TT_HUILE = None  # Oil temperature sensor (AI)

    def __init__(self, HYDRO_TT_HUILE):
        """Initializes the OilTemperature class.

        Args:
            HYDRO_TT_HUILE (AnalogInput): Analog input for oil temperature sensor.
        """
        self.HYDRO_TT_HUILE = HYDRO_TT_HUILE


class WaterPump:
    """Represents the water pump controls, status, and speed.

    Attributes:
        HYDRO_CMD_PO_EAU (DigitalOutput): Digital output to command water pump ON/OFF.
        HYDRO_RM_PO_EAU (DigitalInput): Digital input for water pump running feedback.
        HYDRO_ST_PO_EAU (AnalogInput): Analog input for water pump motor speed sensor.
        HYDRO_SSP_PO_EAU (AnalogOutput): Analog output for water pump speed setpoint.
    """
    HYDRO_CMD_PO_EAU = None  # Water pump motor ON/OFF command (DO)
    HYDRO_RM_PO_EAU = None  # Water pump running feedback (DI)
    HYDRO_ST_PO_EAU = None  # Water pump motor speed sensor (AI)
    HYDRO_SSP_PO_EAU = None  # Water pump speed setpoint (AO)

    def __init__(self, HYDRO_CMD_PO_EAU, HYDRO_RM_PO_EAU, HYDRO_ST_PO_EAU, HYDRO_SSP_PO_EAU):
        """Initializes the WaterPump class.

        Args:
            HYDRO_CMD_PO_EAU (DigitalOutput): Digital output to command water pump ON/OFF.
            HYDRO_RM_PO_EAU (DigitalInput): Digital input for water pump running feedback.
            HYDRO_ST_PO_EAU (AnalogInput): Analog input for water pump motor speed sensor.
            HYDRO_SSP_PO_EAU (AnalogOutput): Analog output for water pump speed setpoint.
        """
        self.HYDRO_CMD_PO_EAU = HYDRO_CMD_PO_EAU
        self.HYDRO_RM_PO_EAU = HYDRO_RM_PO_EAU
        self.HYDRO_ST_PO_EAU = HYDRO_ST_PO_EAU
        self.HYDRO_SSP_PO_EAU = HYDRO_SSP_PO_EAU


class WaterFlow:
    """Represents the cooling water flow sensor.

    Attributes:
        HYDRO_FT_EAU_REFR (AnalogInput): Analog input for cooling water flow sensor.
    """
    HYDRO_FT_EAU_REFR = None  # Cooling water flow sensor (AI)

    def __init__(self, HYDRO_FT_EAU_REFR):
        """Initializes the WaterFlow class.

        Args:
            HYDRO_FT_EAU_REFR (AnalogInput): Analog input for cooling water flow sensor.
        """
        self.HYDRO_FT_EAU_REFR = HYDRO_FT_EAU_REFR


class WaterTemperature:
    """Represents the water temperature sensor.

    Attributes:
        HYDRO_TT_EAU (AnalogInput): Analog input for water temperature sensor.
    """
    HYDRO_TT_EAU = None  # Water temperature sensor (AI)

    def __init__(self, HYDRO_TT_EAU):
        """Initializes the WaterTemperature class.

        Args:
            HYDRO_TT_EAU (AnalogInput): Analog input for water temperature sensor.
        """
        self.HYDRO_TT_EAU = HYDRO_TT_EAU


class WarmingTemperature:
    """Represents the warming water temperature sensor.

    Attributes:
        HYDRO_TT_ECHAUFF (AnalogInput): Analog input for warming water temperature sensor.
    """
    HYDRO_TT_ECHAUFF = None  # Warming water temperature sensor (AI)

    def __init__(self, HYDRO_TT_ECHAUFF):
        """Initializes the WarmingTemperature class.

        Args:
            HYDRO_TT_ECHAUFF (AnalogInput): Analog input for warming water temperature sensor.
        """
        self.HYDRO_TT_ECHAUFF = HYDRO_TT_ECHAUFF


class CoolingTemperature:
    """Represents the cooling water temperature sensor.

    Attributes:
        HYDRO_TT_EAU_REFR (AnalogInput): Analog input for cooling water temperature sensor.
    """
    HYDRO_TT_EAU_REFR = None  # Cooling water temperature sensor (AI)

    def __init__(self, HYDRO_TT_EAU_REFR):
        """Initializes the CoolingTemperature class.

        Args:
            HYDRO_TT_EAU_REFR (AnalogInput): Analog input for cooling water temperature sensor.
        """
        self.HYDRO_TT_EAU_REFR = HYDRO_TT_EAU_REFR


class HeadValve:
    """Represents the head valve controls and status.

    Attributes:
        HYDRO_ZSO_VA_TETE (DigitalInput): Digital input for head valve open limit switch.
        HYDRO_ZSC_VA_TETE (DigitalInput): Digital input for head valve closed limit switch.
        HYDRO_CMDO_VA_TETE (DigitalOutput): Digital output to command head valve opening.
        HYDRO_CMDC_VA_TETE (DigitalOutput): Digital output to command head valve closing.
        Opening (int): Current opening percentage of the head valve (0-100).
    """
    HYDRO_ZSO_VA_TETE = None  # Digital Input (DI)
    HYDRO_ZSC_VA_TETE = None  # Digital Input (DI)
    HYDRO_CMDO_VA_TETE = None  # Digital Output (DO)
    HYDRO_CMDC_VA_TETE = None  # Digital Output (DO)
    Opening = 0

    def __init__(self, HYDRO_CMDO_VA_TETE, HYDRO_CMDC_VA_TETE, HYDRO_ZSO_VA_TETE, HYDRO_ZSC_VA_TETE):
        """Initializes the HeadValve class.

        Args:
            HYDRO_CMDO_VA_TETE (DigitalOutput): Digital output to command head valve opening.
            HYDRO_CMDC_VA_TETE (DigitalOutput): Digital output to command head valve closing.
            HYDRO_ZSO_VA_TETE (DigitalInput): Digital input for head valve open limit switch.
            HYDRO_ZSC_VA_TETE (DigitalInput): Digital input for head valve closed limit switch.
        """
        self.HYDRO_CMDO_VA_TETE = HYDRO_CMDO_VA_TETE
        self.HYDRO_CMDC_VA_TETE = HYDRO_CMDC_VA_TETE
        self.HYDRO_ZSO_VA_TETE = HYDRO_ZSO_VA_TETE
        self.HYDRO_ZSC_VA_TETE = HYDRO_ZSC_VA_TETE


class FootValve:
    """Represents the foot valve controls and status.

    Attributes:
        HYDRO_ZSO_VA_PIED (DigitalInput): Digital input for foot valve open limit switch.
        HYDRO_ZSC_VA_PIED (DigitalInput): Digital input for foot valve closed limit switch.
        HYDRO_CMDO_VA_PIED (DigitalOutput): Digital output to command foot valve opening.
        HYDRO_CMDC_VA_PIED (DigitalOutput): Digital output to command foot valve closing.
        Opening (int): Current opening percentage of the foot valve (0-100).
    """
    HYDRO_ZSO_VA_PIED = 0  # Digital Input (DI)
    HYDRO_ZSC_VA_PIED = 0  # Digital Input (DI)
    HYDRO_CMDO_VA_PIED = 0  # Digital Output (DO)
    HYDRO_CMDC_VA_PIED = 0  # Digital Output (DO)
    Opening = 0

    def __init__(self, HYDRO_CMDO_VA_PIED, HYDRO_CMDC_VA_PIED, HYDRO_ZSO_VA_PIED, HYDRO_ZSC_VA_PIED):
        """Initializes the FootValve class.

        Args:
            HYDRO_CMDO_VA_PIED (DigitalOutput): Digital output to command foot valve opening.
            HYDRO_CMDC_VA_PIED (DigitalOutput): Digital output to command foot valve closing.
            HYDRO_ZSO_VA_PIED (DigitalInput): Digital input for foot valve open limit switch.
            HYDRO_ZSC_VA_PIED (DigitalInput): Digital input for foot valve closed limit switch.
        """
        self.HYDRO_CMDO_VA_PIED = HYDRO_CMDO_VA_PIED
        self.HYDRO_CMDC_VA_PIED = HYDRO_CMDC_VA_PIED
        self.HYDRO_ZSO_VA_PIED = HYDRO_ZSO_VA_PIED
        self.HYDRO_ZSC_VA_PIED = HYDRO_ZSC_VA_PIED


class RGNValve:
    """Represents the RGN (Regulation) valve controls and status.

    Attributes:
        HYDRO_ST_TURB (AnalogInput): Analog input for turbine speed sensor.
        HYDRO_ZT_VA_RGN (AnalogOutput): Analog output for RGN valve position setpoint.
    """
    HYDRO_ST_TURB = None  # Turbine speed sensor (AI)
    HYDRO_ZT_VA_RGN = None  # RGN valve position setpoint (AO)

    def __init__(self, HYDRO_ST_TURB, HYDRO_ZT_VA_RGN):
        """Initializes the RGNValve class.

        Args:
            HYDRO_ST_TURB (AnalogInput): Analog input for turbine speed sensor.
            HYDRO_ZT_VA_RGN (AnalogOutput): Analog output for RGN valve position setpoint.
        """
        self.HYDRO_ST_TURB = HYDRO_ST_TURB
        self.HYDRO_ZT_VA_RGN = HYDRO_ZT_VA_RGN


class RGUExcitation:
    """Represents the RGU (Generator Unit) excitation system.

    Attributes:
        HYDRO_VT_ALTERN (AnalogInput): Analog input for alternator voltage sensor.
        HYDRO_FQT_ALTERN (AnalogInput): Analog input for alternator frequency sensor.
        HYDRO_VSP_ALTERN (AnalogOutput): Analog output for alternator voltage setpoint.
    """
    HYDRO_VT_ALTERN = None  # Alternator voltage sensor (AI)
    HYDRO_FQT_ALTERN = None  # Alternator frequency sensor (AI)
    HYDRO_VSP_ALTERN = None  # Alternator voltage setpoint (AO)

    def __init__(self, HYDRO_VT_ALTERN, HYDRO_FQT_ALTERN, HYDRO_VSP_ALTERN):
        """Initializes the RGUExcitation class.

        Args:
            HYDRO_VT_ALTERN (AnalogInput): Analog input for alternator voltage sensor.
            HYDRO_FQT_ALTERN (AnalogInput): Analog input for alternator frequency sensor.
            HYDRO_VSP_ALTERN (AnalogOutput): Analog output for alternator voltage setpoint.
        """
        self.HYDRO_VT_ALTERN = HYDRO_VT_ALTERN
        self.HYDRO_FQT_ALTERN = HYDRO_FQT_ALTERN
        self.HYDRO_VSP_ALTERN = HYDRO_VSP_ALTERN


class SyncCoupler:
    """Represents the synchronization coupler.

    Attributes:
        HYDRO_AUTORIZ_CPL (DigitalInput): Digital input for coupling authorization.
        HYDRO_CMD_COUPLAGE (DigitalOutput): Digital output to command coupling.
    """
    HYDRO_AUTORIZ_CPL = None  # Coupling authorization (DI)
    HYDRO_CMD_COUPLAGE = None  # Coupling command (DO)

    def __init__(self, HYDRO_CMD_COUPLAGE, HYDRO_AUTORIZ_CPL):
        """Initializes the SyncCoupler class.

        Args:
            HYDRO_CMD_COUPLAGE (DigitalOutput): Digital output to command coupling.
            HYDRO_AUTORIZ_CPL (DigitalInput): Digital input for coupling authorization.
        """
        self.HYDRO_CMD_COUPLAGE = HYDRO_CMD_COUPLAGE
        self.HYDRO_AUTORIZ_CPL = HYDRO_AUTORIZ_CPL


class SEPAM:
    """Represents the SEPAM protection relay measurements.

    Attributes:
        HYDRO_JT_ALTERN (AnalogInput): Analog input for generated electrical power (to SCADA).
        FREQ (AnalogInput): Analog input for frequency (to power board).
        COURANT1 (AnalogInput): Analog input for current phase 1.
        COURANT2 (AnalogInput): Analog input for current phase 2.
        COURANT3 (AnalogInput): Analog input for current phase 3.
        SHIFT (AnalogInput): Analog input for power factor angle.
    """
    HYDRO_JT_ALTERN = 0  # Generated electrical power (AI to SCADA)
    FREQ = 0  # Frequency (AI to power board)
    COURANT1 = 0
    COURANT2 = 0
    COURANT3 = 0
    SHIFT = 0

    def __init__(self, HYDRO_JT_ALTERN, FREQ, COURANT1, COURANT2, COURANT3, SHIFT):
        """Initializes the SEPAM class.

        Args:
            HYDRO_JT_ALTERN (AnalogInput): Analog input for generated electrical power (to SCADA).
            FREQ (AnalogInput): Analog input for frequency (to power board).
            COURANT1 (AnalogInput): Analog input for current phase 1.
            COURANT2 (AnalogInput): Analog input for current phase 2.
            COURANT3 (AnalogInput): Analog input for current phase 3.
            SHIFT (AnalogInput): Analog input for power factor angle.
        """
        self.HYDRO_JT_ALTERN = HYDRO_JT_ALTERN
        self.FREQ = FREQ
        self.COURANT1 = COURANT1
        self.COURANT2 = COURANT2
        self.COURANT3 = COURANT3
        self.SHIFT = SHIFT
