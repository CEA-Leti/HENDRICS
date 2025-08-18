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

import logging

from scenarios.hydro.components import component, objects
from simulator.variables import FieldType, Field

MIN_OIL_TEMPERATURE = 20.0  # ⁰C
MAX_OIL_TEMPERATURE = 70.0  # ⁰C
INITIAL_OIL_TEMPERATURE = MIN_OIL_TEMPERATURE


class HydraulicCentral(component.Component):
    """
    Simulates the behavior of a hydraulic central, specifically focusing on the oil pump and oil temperature.
    """
    _oilPump = None  # DI: HYDRO_RM_PO_HUILE DO: HYDRO_CMD_PO_HUILE
    _oilTemperature = None  # AI: HYDRO_TT_HUILE

    def __init__(self, env, oilPump, oilTemperature):
        """
        Initializes the HydraulicCentral.

        Args:
            env (simpy.Environment): The simulation environment.
            oilPump (objects.OilPump): An instance of the OilPump object.
            oilTemperature (objects.OilTemperature): An instance of the OilTemperature object.

        Raises:
            ValueError: If oilPump or oilTemperature are not instances of their respective types.
        """
        super().__init__(env)
        if not isinstance(oilPump, objects.OilPump):
            raise ValueError(oilPump)
        self._oilPump = oilPump
        if not isinstance(oilTemperature, objects.OilTemperature):
            raise ValueError(oilTemperature)
        self._oilTemperature = oilTemperature

    def _update_oil_temperature(self):
        """
        Increases or decreases the oil temperature linearly by 1 degree Celsius per UPDATE_TICK.
        The temperature is capped between MIN_OIL_TEMPERATURE and MAX_OIL_TEMPERATURE.
        """
        # Increases/decreases linearly by 1.
        if self._oilPump.HYDRO_RM_PO_HUILE.value:
            temperature = self._oilTemperature.HYDRO_TT_HUILE.value + 1
        else:
            temperature = self._oilTemperature.HYDRO_TT_HUILE.value - 1
        if temperature > MAX_OIL_TEMPERATURE:
            temperature = MAX_OIL_TEMPERATURE
        elif temperature < MIN_OIL_TEMPERATURE:
            temperature = MIN_OIL_TEMPERATURE
        self._oilTemperature.HYDRO_TT_HUILE.value = temperature

    def _update_oil_pump(self):
        """
        Synchronizes the oil pump's running feedback with its command.
        In a real scenario, a motor would provide this feedback, but here the simulator
        copies the command status to the feedback to simulate it.
        """
        # The simulator will copy the pump's start/stop command to the status feedback.
        # Without a wired motor, the TeSys would not be able to send motor running feedback.
        self._oilPump.HYDRO_RM_PO_HUILE.value = self._oilPump.HYDRO_CMD_PO_HUILE.value

    def process(self):
        """
        The main simulation process for the hydraulic central.
        Continuously updates oil temperature and oil pump status.
        """
        while True:
            self._update_oil_temperature()
            self._update_oil_pump()
            yield self.env.timeout(self.UPDATE_TICK)


if __name__ == "__main__":
    import random
    import simpy
    from tqdm import tqdm

    ITER = 500
    bar = tqdm(total=ITER)

    HYDRO_CMD_PO_HUILE = Field("HYDRO_CMD_PO_HUILE", io_type=FieldType.DIGITAL_OUTPUT.value, io_port=0x08, value=False)
    HYDRO_RM_PO_HUILE = Field("HYDRO_RM_PO_HUILE", io_type=FieldType.DIGITAL_INPUT.value, io_port=0x04, value=False)

    HYDRO_TT_HUILE = Field(
        "HYDRO_TT_HUILE",
        io_type=FieldType.ANALOG_INPUT.value,
        io_port=0x01,
        value=INITIAL_OIL_TEMPERATURE
    )

    oilPump = objects.OilPump(HYDRO_CMD_PO_HUILE, HYDRO_RM_PO_HUILE)
    oilTemperature = objects.OilTemperature(HYDRO_TT_HUILE)

    # Outputs
    monitor_pump_on_off = []
    monitor_oil_temperature = []

    def change_pump_state(env):
        """
        Simulates random changes in the oil pump's command state.
        """
        while True:
            bar.update(1)
            if random.random() > 0.99:
                oilPump.HYDRO_CMD_PO_HUILE.value = not oilPump.HYDRO_CMD_PO_HUILE.value
            yield env.timeout(1)

    def monitor_pump(env):
        """
        Monitors the oil pump's ON/OFF status and oil temperature.
        """
        global monitor_pump_on_off, monitor_oil_temperature
        while True:
            monitor_pump_on_off.append(10 * oilPump.HYDRO_RM_PO_HUILE.value)
            monitor_oil_temperature.append(oilTemperature.HYDRO_TT_HUILE.value)
            yield env.timeout(1)

    logging.basicConfig(level=logging.ERROR)
    env = simpy.Environment()
    pump = HydraulicCentral(env, oilPump=oilPump, oilTemperature=oilTemperature)
    env.process(change_pump_state(env))
    env.process(monitor_pump(env))
    env.run(until=ITER)
    bar.close()

    import matplotlib.pyplot as plt

    plt.figure()
    plt.plot(range(ITER), monitor_pump_on_off, label="Pump ON/OFF")
    plt.plot(range(ITER), monitor_oil_temperature, label="Oil Temperature")
    plt.legend(loc="upper right")
    plt.title("Oil Pump states")
    plt.show()
