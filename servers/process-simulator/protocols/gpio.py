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

"""Generic class for a GPIO-based simulation process.

This script simulates the behavior of a physical process using GPIO for input/output 
and communicates with a Redis broker for state management.
"""

import os
import logging
import toml
import json
import simpy
import redis
import argparse

# Configure logging
logging.basicConfig(level=logging.ERROR)

try:
    if os.getuid() == 0:
        import subprocess
        subprocess.run("pigpiod")

    import time
    import pigpio
    gpio = pigpio.pi()
    while not gpio.connected:
        time.sleep(1)
        gpio = pigpio.pi()
except ImportError:
    print("GPIO module not found!")
    import sys
    sys.exit(1)

VALID_GPIO = [
    2,
    3,
    4,
    14,
    15,
    17,
    18,
    27,
    22,
    23,
    24,
    10,
    9,
    25,
    11,
    8,
    7,
    5,
    6,
    12,
    13,
    19,
    16,
    26,
    20,
    21,
]


class Process:
    """Class representing a GPIO-based simulation process."""
    def __init__(self, configFile, slaveId, verbose=False):
        """Initialize the Process instance.

        Args:
            configFile (str): Path to the TOML configuration file.
            slaveId (int): ID of the associated slave device.
            verbose (bool): If True, enables detailed logging.
        """
        self._slaveId = slaveId
        self._varNames = []

        # Redis broker.
        self._broker = redis.Redis(host=os.environ["REDIS_HOST"], port=6379)

        # Parse and apply configuration from TOML files.
        parsed = {}
        tomlFiles = configFile.split(",")
        for tomlFile in tomlFiles:
            parsed.update(toml.load(tomlFile))

        self._initAllFields(parsed)

        # SimPy environment.
        self._env = simpy.RealtimeEnvironment(factor=self._factor)
        self._env.process(self.process())

        # Verbosity.
        self._verbose = verbose
        if self._verbose:
            self._env.process(self.monitor())

    @property
    def env(self):
        """Get the simulation environment."""
        return self._env

    def getFieldValue(self, name):
        """Retrieve the value of a specific field.

        Args:
            name (str): Name of the field.

        Returns:
            any: The value of the specified field.
        """
        return getattr(self, name).value

    def _initAllFields(self, data):
        """Initialize all fields from the configuration data.

        Args:
            data (dict): Parsed configuration data.
        """
        self._factor = data["environment"]["factor"]
        for key, val in data["variables"].items():
            if "gpioPort" not in val:
                # Skip variables that are not GPIO-based.
                continue

            if "gpioSlave" in val and val["gpioSlave"] != self._slaveId:
                # Skip variables not associated with this slave.
                continue

            ioType = None
            if val["ioType"].endswith("INPUT"):
                ioType = pigpio.INPUT
            elif val["ioType"].endswith("OUTPUT"):
                ioType = pigpio.OUTPUT
            else:
                raise ValueError(f"Invalid I/O type for variable {key}: {val['ioType']}")

            hide = val.get("hide", False)
            value = None
            gpioPort = val["gpioPort"]

            var = [ioType, gpioPort, value, hide]
            self._varNames.append(key)
            setattr(self, key, var)
            self._initGPIO(gpioPort, ioType)

        self._writeGPIO()

    def _initGPIO(self, gpioPort, ioType):
        """Initialize a GPIO port.

        Args:
            gpioPort (int): GPIO port number.
            ioType (int): GPIO input/output type.
        """
        assert gpioPort in VALID_GPIO
        assert ioType in (pigpio.INPUT, pigpio.OUTPUT)
        gpio.set_mode(gpioPort, ioType)
        gpio.set_pull_up_down(gpioPort, pigpio.PUD_DOWN)

    def _updateLocalVal(self, name, val):
        """Update the local value of a field.

        Args:
            name (str): Name of the field.
            val (any): New value for the field.
        """
        currentVal = getattr(self, name)
        currentVal[2] = val
        setattr(self, name, currentVal)

    def _writeGPIO(self):
        """Write output values to GPIO ports."""
        for name, var in {
            key: val for key, val in self.__dict__.items()
            if key in self._varNames and val[0] == pigpio.OUTPUT
        }.items():
            val = json.loads(self._broker.get(name))
            self._updateLocalVal(name, val)
            gpioVal = pigpio.HIGH if val else pigpio.LOW
            gpio.write(var[1], gpioVal)

    def _readGPIO(self):
        """Read input values from GPIO ports."""
        for name, var in {
            key: val for key, val in self.__dict__.items()
            if key in self._varNames and val[0] == pigpio.INPUT
        }.items():
            gpioVal = gpio.read(var[1])
            val = gpioVal == pigpio.HIGH
            self._updateLocalVal(name, val)
            self._broker.set(name, json.dumps(val))

    def process(self):
        """Main process loop for simulation."""
        while True:
            # Read input values.
            self._readGPIO()

            # Write output values.
            self._writeGPIO()

            # Wait for the next simulation step.
            yield self._env.timeout(1)

    def monitor(self):
        """Monitor and log the state of all fields periodically."""
        while True:
            logging.info("===================================")
            for name, var in {
                key: val for key, val in self.__dict__.items()
                if key in self._varNames and not val[3]
            }.items():
                logging.info(f"{name}: {var}")

            # Wait for the next monitoring step.
            yield self._env.timeout(1)

    def run(self, until=None):
        """Run the simulation process.

        Args:
            until (int, optional): Duration to run the simulation. Defaults to None.
        """
        self._env.run(until=until)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--toml",
        help="Path to TOML configuration file",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--slave-id",
        help="ID of the slave device",
        type=int,
        default=0,
    )
    args = parser.parse_args()

    # Create and run the simulation process.
    Process(
        configFile=args.toml,
        slaveId=args.slave_id,
        verbose=True,
    ).run()


if __name__ == "__main__":
    main()
