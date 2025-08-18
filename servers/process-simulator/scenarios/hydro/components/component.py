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
""" Generic class for a simulated component. """

class Component(object):
    """ Generic class for a simulated component. """
    UPDATE_TICK = None  # Number of clock ticks between two updates.
    _env = None

    def __init__(self, env, updateTick=1):
        """Initialize the component.

        Args:
            env (simpy.Environment): Simulation environment.
            updateTick (int): How many simulation ticks are passed each update.
        """
        self._env = env
        self.UPDATE_TICK = updateTick
        self._env.process(self.process())

    @property
    def env(self):
        """Returns component's environment."""
        return self._env

    def process(self):
        """Abstract method to be specified by child classes."""
        raise NotImplementedError
