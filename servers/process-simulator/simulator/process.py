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

"""Generic class for a simulation process."""

import os
import logging

import toml
import simpy
import redis

import simulator.variables as variables


class Process:
    """
    Generic class for a simulation process.

    Attributes:
        _env (simpy.RealtimeEnvironment): Simulation environment.
        _broker (redis.Redis): Redis broker for field communication.
        _factor (float): Time scaling factor for the simulation.
        _verbose (bool): Verbosity flag for monitoring.
    """
    def __init__(self, config_file, verbose=False):
        """
        Initialize the simulation process.

        Args:
            config_file (str): Path to the TOML configuration file.
            verbose (bool): If True, enables monitoring.
        """
        # Redis broker.
        self._broker = redis.Redis(host=os.environ["REDIS_HOST"], port=6379)

        # Read and apply configuration.
        parsed = toml.load(config_file)
        self._init_all_fields(parsed)

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

    def get_field_value(self, name):
        """
        Retrieve the value of a field by its name.

        Args:
            name (str): Field name.

        Returns:
            The value of the field.
        """
        return getattr(self, name).value

    def _init_all_fields(self, data):
        """
        Add all fields as attributes of the Process class and publish them.

        Args:
            data (dict): Parsed configuration data.
        """
        self._factor = data["environment"]["factor"]
        for key, val in data["variables"].items():
            io_type = (getattr(variables.FieldType, val["ioType"]) if "ioType" in val else None)
            hide = val.get("hide")

            if "compositeType" in val:
                var_type = getattr(variables, val["compositeType"])
                if isinstance(val["value"], str):
                    obj, attr = val["value"].split(".")
                    value = getattr(getattr(variables, obj), attr)
                else:
                    value = val["value"]
            else:
                var_type = variables.Field
                value = val.get("value")

            var = var_type(key, io_type, value, hide)
            setattr(self, key, var)
        self._publish_fields(force_all=True)

    def _publish_fields(self, force_all=False):
        """
        Publish all output fields to the Redis broker.

        Args:
            force_all (bool): If True, publishes all fields regardless of IO type.
        """
        for name, var in {
            key: val for key, val in self.__dict__.items()
            if isinstance(val, variables.Field)
            and (val.ioType.value & variables.FieldType.OUTPUT_BIT.value or force_all)
        }.items():
            val = var.toJSON()
            self._broker.set(name, val)

    def _retrieve_fields(self):
        """
        Retrieve all input fields from the Redis broker.
        """
        for name, var in {
            key: val for key, val in self.__dict__.items()
            if isinstance(val, variables.Field)
            and val.ioType.value & variables.FieldType.INPUT_BIT.value
        }.items():
            val = self._broker.get(name)
            getattr(self, name).fromJSON(val)

    def process(self):
        """
        Main simulation process loop.
        """
        while True:
            # Retrieve input fields from the broker.
            self._retrieve_fields()

            # Wait for the next simulation step.
            yield self._env.timeout(1)

            # Publish output fields to the broker.
            self._publish_fields()

    def monitor(self):
        """
        Monitor and log the state of all fields periodically.
        """
        while True:
            logging.info("===================================")
            for key, val in self.__dict__.items():
                if isinstance(val, variables.Field) and not val.hide:
                    logging.info(str(val))

            # Wait for the next monitoring step.
            yield self._env.timeout(1)

    def run(self, until=None):
        """
        Start the simulation process.

        Args:
            until (int, optional): Duration to run the simulation. Defaults to None.
        """
        self._env.run(until=until)
