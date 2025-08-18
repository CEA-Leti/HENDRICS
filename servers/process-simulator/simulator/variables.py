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

"""Components input/output classes."""

import enum
import json


class FieldType(enum.Enum):
    """Class listing possible data types for interface card."""
    INPUT_BIT = 0x01
    OUTPUT_BIT = 0x02
    DIGITAL_BIT = 0x04
    ANALOG_BIT = 0x08

    DIGITAL_INPUT = INPUT_BIT | DIGITAL_BIT
    DIGITAL_OUTPUT = OUTPUT_BIT | DIGITAL_BIT
    ANALOG_INPUT = INPUT_BIT | ANALOG_BIT
    ANALOG_OUTPUT = OUTPUT_BIT | ANALOG_BIT
    _NONE_TYPE = None


class Field:
    """Definition of input/output variables."""
    def __init__(self, name, io_type=None, value=None, hide=False):
        """
        Initialize a Field instance.

        Args:
            name (str): Name of the field.
            io_type (FieldType, optional): Type of IO for the field. Defaults to None.
            value (any, optional): Initial value for the field. Defaults to None.
            hide (bool, optional): Whether the field is hidden. Defaults to False.
        """
        self.name = name
        self.ioType = io_type
        self.value = value
        self.hide = hide

    def __str__(self):
        return json.dumps({
            k: str(v)
            for k,
            v in self.__dict__.items()
            if v is not None
        })

    def toJSON(self):
        """Convert the field's value to a JSON string."""
        return json.dumps(self.value)

    def fromJSON(self, value):
        """Set the field's value from a JSON string."""
        self.value = json.loads(value)


class FieldCollection:
    """Collection of fields. Must implement a field property."""
    def __init__(self, fields):
        """
        Initialize a FieldCollection instance.

        Args:
            fields (list[Field]): List of Field objects.

        Raises:
            ValueError: If any element in fields is not an instance of Field.
        """
        for field in fields:
            if not isinstance(field, Field):
                raise ValueError(field.name)
        self._fields = fields

    @property
    def fields(self):
        """Get the list of fields."""
        return self._fields

    @fields.setter
    def fields(self, fields):
        """Set the list of fields."""
        self._fields = fields


class FluidField(Field):
    """Definition of input/output variable related to fluids (gas/liquids)."""

    AIR = "AIR"
    H2 = "H2"
    N2 = "N2"

    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"
    P5 = "P5"
    P7 = "P7"
    P8 = "P8"
    P9 = "P9"
    P10 = "P10"
    PA = "P1_P2_P5"
    PB = "P3_P4_P7"

    def __init__(self, name, io_type=None, value=None, hide=False, fluid_dict=None, temperature=-1):
        """
        Initialize a FluidField instance.

        Args:
            name (str): Name of the field.
            io_type (FieldType, optional): Type of IO for the field. Defaults to None.
            value (any, optional): Initial value for the field. Defaults to None.
            hide (bool, optional): Whether the field is hidden. Defaults to False.
            fluid_dict (dict, optional): Dictionary of fluid quantities. Defaults to None.
            temperature (float, optional): Temperature of the fluid. Defaults to -1.
        """
        super().__init__(name, io_type, value, hide)
        self._fluidDict = self._normalize(fluid_dict) if fluid_dict else None
        self._temperature = temperature

    def _normalize(self, fluid_dict):
        """
        Normalize gas quantities to ensure they sum to 1 and remove null entries.

        Args:
            fluid_dict (dict): Dictionary of fluid quantities.

        Returns:
            dict: Normalized fluid quantities.
        """
        total = sum(fluid_dict.values())
        if total > 0:
            return {
                key: val / total
                for key,
                val in fluid_dict.items()
                if val != 0
            }
        return {}

    @property
    def fluidDict(self):
        """Get the fluid dictionary."""
        return self._fluidDict

    @fluidDict.setter
    def fluidDict(self, fluid_dict):
        """Set the fluid dictionary."""
        self._fluidDict = self._normalize(fluid_dict) if fluid_dict else None

    def fluidQuantity(self, key):
        """Retrieve the quantity of a specific fluid.

        Args:
            key (str): Fluid key.

        Returns:
            float: Quantity of the specified fluid.
        """
        return self._fluidDict.get(key, 0.0)

    @property
    def temperature(self):
        """Get the temperature of the fluid."""
        return self._temperature

    @temperature.setter
    def temperature(self, temperature):
        """Set the temperature of the fluid."""
        self._temperature = temperature


class BreakerStateType(enum.Enum):
    """Class listing possible types for breaker state value."""
    CLOSED = (False, True)
    OPEN = (True, False)
    TRANSITION = (False, False)
    BROKEN = (True, True)


class DisconnectorStateType(enum.Enum):
    """Class listing possible types for disconnector state value."""
    OPEN = "Open"
    CLOSED = "Closed"
    BROKEN = "Broken"


class BreakerStateField(FieldCollection):
    """Variable defining breaker state."""
    def __init__(self, fields, value, hide=False):
        """
        Initialize a BreakerStateField instance.

        Args:
            fields (list[Field]): List of Field objects representing breaker states.
            value (BreakerStateType): Initial breaker state.
            hide (bool, optional): Whether the field is hidden. Defaults to False.

        Raises:
            TypeError: If the value is not a BreakerStateType.
        """
        if not isinstance(value, BreakerStateType):
            raise TypeError(fields, value)
        super().__init__(fields)
        self.value = value

    @property
    def value(self):
        """Get the current breaker state."""
        return BreakerStateType((self.fields[0].value, self.fields[1].value))

    @value.setter
    def value(self, value):
        """Set the breaker state."""
        state0, state1 = self.fields
        val0, val1 = value.value
        state0.value = val0
        state1.value = val1


class DisconnectorStateField(Field):
    """Variable defining disconnector state."""
    def __init__(self, name, io_type=None, value=None, hide=False):
        """
        Initialize a DisconnectorStateField instance.

        Args:
            name (str): Name of the field.
            io_type (FieldType, optional): Type of IO for the field. Defaults to None.
            value (DisconnectorStateType): Initial disconnector state.
            hide (bool, optional): Whether the field is hidden. Defaults to False.

        Raises:
            TypeError: If the value is not a DisconnectorStateType.
        """
        if not isinstance(value, DisconnectorStateType):
            raise TypeError(name, value)
        self._observer = None
        super().__init__(name, io_type, value, hide)

    def __setattr__(self, name, value):
        """
        Override setattr to handle disconnector state transitions.

        Args:
            name (str): Attribute name.
            value (any): Attribute value.
        """
        if name == "value":
            current_value = self.__getattribute__(name)
            if current_value == DisconnectorStateType.CLOSED and value == DisconnectorStateType.OPEN:
                if self._observer and not self._observer(value):
                    return
            elif current_value == DisconnectorStateType.BROKEN:
                raise ValueError(f"Cannot transition from {current_value} to {value}.")
        super().__setattr__(name, value)

    @property
    def observer(self):
        """Get the observer callback."""
        return self._observer

    def bindTo(self, callback):
        """
        Set the observer callback.

        Args:
            callback (callable): Function to call when a state transition occurs.
        """
        if not callable(callback):
            raise TypeError("Observer must be callable.")
        self._observer = callback

    def toJSON(self):
        """Serializes the field as JSON."""
        return json.dumps(self.value.name)

    def fromJSON(self, value):
        """Creates the field from JSON."""
        self.value = DisconnectorStateType[json.loads(value)]
