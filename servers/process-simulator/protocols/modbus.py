#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

"""Modified version of Pymodbus synchronous server example to add REDIS datastore support.

This script demonstrates the implementation of a single-threaded synchronous 
server for the MODBUS protocol. It supports communication over TCP, UDP, 
serial, and TLS, and provides configuration options for various datastore 
types, log levels, and communication parameters.

Usage:
    python server_sync.py [-h] [--comm {tcp,udp,serial,tls}]
                          [--framer {ascii,binary,rtu,socket,tls}]
                          [--log {critical,error,warning,info,debug}]
                          [--port PORT] [--store {sequential,sparse,factory,none}]
                          [--slaves SLAVES]

Command-line Options:
    -h, --help               Show help message and exit.
    --comm                   Communication type: "tcp", "udp", "serial", or "tls".
    --framer                 Framer type: "ascii", "binary", "rtu", "socket", or "tls".
    --log                    Log level: "critical", "error", "warning", "info", or "debug".
    --port                   Port to use.
    --baudrate               Baud rate for the serial device (default: 9600).
    --store                  Type of datastore: "sequential", "sparse", "factory", "none", or "redis".
    --slaves                 Comma-separated list of slave IDs (default: 0, any).

Example:
    To run the server:
        python server_sync.py --comm tcp --port 5020 --store redis

Note:
    It is recommended to use the asynchronous server. This synchronous server 
    is a thin wrapper over the async server and may exhibit slower performance.

"""

import argparse
import logging
import asyncio
import redis
import toml
import os

from pymodbus import __version__ as pymodbus_version
from pymodbus import pymodbus_apply_logging_config
from pymodbus.transaction import (
    ModbusAsciiFramer,
    ModbusBinaryFramer,
    ModbusRtuFramer,
    ModbusSocketFramer,
    ModbusTlsFramer,
)
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import (
    StartSerialServer,
    StartTcpServer,
)

_logger = logging.getLogger()


# --------------------------------------------------------------------------- #
# Redis Data Block Implementation
# --------------------------------------------------------------------------- #
def redis_encode(val):
    """Encode Python values into Redis-compatible format.

    Args:
        val: The value to encode. It can be a boolean, numeric, or None.

    Returns:
        bytes: The Redis-compatible encoded value.
    """
    if val is True:
        return b"true"
    elif val is False:
        return b"false"
    elif val:
        return round(float(val))
    return 0


def redis_decode(val):
    """Decode Redis-compatible format into Python values.

    Args:
        val (bytes): The Redis value to decode.

    Returns:
        int | bool: The decoded value as a Python type.
    """
    if val == b"true":
        return True
    elif val == b"false":
        return False
    elif val:
        return round(float(val))
    return 0


class RedisDataBlock(ModbusSequentialDataBlock):
    """Custom Redis-based datastore for MODBUS servers.

    This datastore integrates with a Redis message queue for data persistence
    and retrieval.
    """
    def __init__(self, queue, addr, values, config_file, io_type, slave_id):
        """Initialize RedisDataBlock.

        Args:
            queue (asyncio.Queue): Message queue for communication.
            addr (int): Starting address of the block.
            values (list): Initial values for the block.
            config_file (str): TOML configuration file(s) for mapping variables.
            io_type (str): Type of I/O (e.g., "DIGITAL", "ANALOG").
            slave_id (int): MODBUS slave ID.
        """
        self.queue = queue
        self.slave_id = slave_id
        self.io_type = io_type

        # Initialize Redis broker.
        self._broker = redis.Redis(host=os.environ["REDIS_HOST"], port=6379)

        # Parse and apply configuration from TOML files.
        parsed = {}
        toml_files = config_file.split(",")
        for toml_file in toml_files:
            parsed.update(toml.load(toml_file)["variables"])

        self._toml_variables = {
            var["modbusAddress"]: key
            for key,
            var in parsed.items()
            if var.get("ioType",
                       "").startswith(io_type) and var.get("modbusSlave") == slave_id
        }

        super().__init__(addr, values)

    def __repr__(self):
        """Represent the RedisDataBlock instance as a string."""
        return f"<RedisDataBlock(slave_id={self.slave_id}, io_type={self.io_type}, variables={self._toml_variables})>"

    def setValues(self, address, values):
        """Set values in the datastore and push updates to Redis.

        Args:
            address (int): The starting address to set values.
            values (list): The values to set in the datastore.
        """
        for offset, val in enumerate(values):
            real_addr = address + offset - 1
            var_name = self._toml_variables[real_addr]
            value = redis_encode(val)
            self._broker.set(var_name, value)
            _logger.debug(f"Set value at address {real_addr}: {value}")

    def getValues(self, address, count=1):
        """Retrieve values from the datastore.

        Args:
            address (int): The starting address to retrieve values.
            count (int, optional): The number of values to retrieve. Defaults to 1.

        Returns:
            list: Retrieved values from the datastore.
        """
        results = []
        for offset in range(count):
            real_addr = address + offset - 1
            var_name = self._toml_variables[real_addr]
            value = redis_decode(self._broker.get(var_name))
            results.append(value)
        _logger.debug(f"Retrieved values from address {address}: {results}")
        return results

    def validate(self, address, count=1):
        """Validate if the requested range is within bounds.

        Args:
            address (int): The starting address to validate.
            count (int, optional): The number of values to validate. Defaults to 1.

        Returns:
            bool: True if the range is valid, False otherwise.
        """
        result = super().validate(address, count=count)
        _logger.debug(f"Validation result for address {address}, count {count}: {result}")
        return result


# --------------------------------------------------------------------------- #
# Additional Classes and Utilities
# --------------------------------------------------------------------------- #
class NanoelecRtuFramer(ModbusRtuFramer):
    """Custom RTU framer with GPIO handling for RS485 communication."""
    def sendPacket(self, message):
        """Send packet while managing GPIO for RS485.

        Args:
            message (bytes): The message packet to send.
        """
        # Set GPIO to HIGH for RS485 emission.
        # Add GPIO handling logic here.
        super().sendPacket(message)
        # Reset GPIO to LOW after sending.


# --------------------------------------------------------------------------- #
# Main Server Setup and Execution
# --------------------------------------------------------------------------- #
def get_commandline(server=False, description=None, extras=None, cmdline=None):
    """Parse and validate command-line arguments.

    Args:
        server (bool, optional): Flag to determine server setup. Defaults to False.
        description (str, optional): Description of the server. Defaults to None.
        extras (list, optional): Additional command-line arguments. Defaults to None.
        cmdline (list, optional): Input command-line arguments. Defaults to None.

    Returns:
        argparse.Namespace: Parsed arguments as a namespace.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-c",
        "--comm",
        choices=["tcp",
                 "serial"],
        help="set communication, default is tcp",
        dest="comm",
        default="tcp",
        type=str,
    )
    parser.add_argument(
        "-f",
        "--framer",
        choices=["ascii",
                 "binary",
                 "rtu",
                 "socket",
                 "tls",
                 "nanoelec"],
        help="set framer, default depends on --comm",
        dest="framer",
        type=str,
    )
    parser.add_argument(
        "-l",
        "--log",
        choices=["critical",
                 "error",
                 "warning",
                 "info",
                 "debug"],
        help="set log level, default is info",
        dest="log",
        default="info",
        type=str,
    )
    parser.add_argument(
        "-p",
        "--port",
        help="set port",
        dest="port",
        type=str,
    )
    parser.add_argument(
        "--baudrate",
        help="set serial device baud rate",
        default=9600,
        type=int,
    )
    if server:
        parser.add_argument(
            "--store",
            choices=["sequential",
                     "sparse",
                     "factory",
                     "redis",
                     "none"],
            help="set type of datastore",
            default="redis",
            type=str,
        )
        parser.add_argument(
            "--slaves",
            help="comma separated list of slave ids, default is 0 (any)",
            default=0,
            type=str,
        )
        parser.add_argument(
            "--context",
            help="ADVANCED USAGE: set datastore context object",
            default=None,
        )
        parser.add_argument(
            "--toml",
            help="ADVANCED USAGE: toml config for redis datablocks",
            type=str,
            default=None,
        )
    else:
        parser.add_argument(
            "--host",
            help="set host, default is 127.0.0.1",
            dest="host",
            default="127.0.0.1",
            type=str,
        )
    if extras:
        for extra in extras:
            parser.add_argument(extra[0], **extra[1])
    args = parser.parse_args(cmdline)

    # set defaults
    comm_defaults = {
        "tcp": ["socket",
                5020],
        "udp": ["socket",
                5020],
        "serial": ["rtu",
                   "/dev/ptyp0"],
        "tls": ["tls",
                5020],
    }
    framers = {
        "ascii": ModbusAsciiFramer,
        "binary": ModbusBinaryFramer,
        "rtu": ModbusRtuFramer,
        "socket": ModbusSocketFramer,
        "tls": ModbusTlsFramer,
        "nanoelec": NanoelecRtuFramer,
    }
    pymodbus_apply_logging_config(args.log)
    _logger.setLevel(args.log.upper())
    args.framer = framers[args.framer or comm_defaults[args.comm][0]]
    args.port = args.port or comm_defaults[args.comm][1]
    if args.comm != "serial" and args.port:
        args.port = int(args.port)
    return args


def setup_server(description=None, context=None, cmdline=None):
    """Configure and start the MODBUS server based on command-line input.

    Args:
        description (str, optional): Description for the server's operation. Defaults to None.
        context (ModbusServerContext, optional): Predefined datastore context for the server. Defaults to None.
        cmdline (list, optional): Command-line arguments passed for server setup. Defaults to None.

    Returns:
        None
    """
    args = get_commandline(server=True, description=description, cmdline=cmdline)
    if context:
        args.context = context
    if not args.context:
        _logger.info("### Create datastore")
        args.slaves = [int(i) for i in args.slaves.split(",")]
        stores = {
            i: (
                None,
                None,
            )
            for i in args.slaves
        }
        # The datastores only respond to the addresses that are initialized
        # If you initialize a DataBlock to addresses of 0x00 to 0xFF, a request to
        # 0x100 will respond with an invalid address exception.
        # This is because many devices exhibit this kind of behavior (but not all)
        if args.store == "sequential":
            # Continuing, use a sequential block without gaps.
            stores = {
                i: (
                    ModbusSequentialDataBlock(
                        0x00,
                        [17] * 100,
                    ),
                    ModbusSequentialDataBlock(
                        0x00,
                        [17] * 100,
                    ),
                )
                for i in args.slaves
            }
        elif args.store == "sparse":
            # Continuing, or use a sparse DataBlock which can have gaps
            stores = {
                i: (
                    ModbusSparseDataBlock({
                        0x00: 0,
                        0x05: 1
                    }),
                    ModbusSparseDataBlock({
                        0x00: 0,
                        0x05: 1
                    }),
                )
                for i in args.slaves
            }
        elif args.store == "factory":
            # Alternately, use the factory methods to initialize the DataBlocks
            # or simply do not pass them to have them initialized to 0x00 on the
            # full address range::
            stores = {
                i: (
                    ModbusSequentialDataBlock.create(),
                    ModbusSequentialDataBlock.create(),
                )
                for i in args.slaves
            }
        elif args.store == "redis":
            # Data stored on the REDIS database fed by the simulator.
            queue = asyncio.Queue()
            stores = {
                i:
                    (
                        RedisDataBlock(
                            queue,
                            0x00,
                            [17] * 100,
                            args.toml,
                            "DIGITAL",
                            i,
                        ),
                        RedisDataBlock(
                            queue,
                            0x00,
                            [17] * 100,
                            args.toml,
                            "ANALOG",
                            i,
                        ),
                    )
                for i in args.slaves
            }

        if args.slaves:
            # The server then makes use of a server context that allows the server
            # to respond with different slave contexts for different slave ids.
            # By default it will return the same context for every slave id supplied
            # (broadcast mode).
            # However, this can be overloaded by setting the single flag to False and
            # then supplying a dictionary of slave id to context mapping::
            #
            # The slave context can also be initialized in zero_mode which means
            # that a request to address(0-7) will map to the address (0-7).
            # The default is False which is based on section 4.4 of the
            # specification, so address(0-7) will map to (1-8)::
            single = False
            context = {
                i: ModbusSlaveContext(
                    di=stores[i][0],
                    co=stores[i][0],
                    ir=stores[i][1],
                    hr=stores[i][1],
                )
                for i in args.slaves
            }
        else:
            context = ModbusSlaveContext(
                di=stores[0][0],
                co=stores[0][0],
                ir=stores[0][1],
                hr=stores[0][1],
            )
            single = True

        # Build data storage
        args.context = ModbusServerContext(slaves=context, single=single)

    # ----------------------------------------------------------------------- #
    # initialize the server information
    # ----------------------------------------------------------------------- #
    # If you don't set this or any fields, they are defaulted to empty strings.
    # ----------------------------------------------------------------------- #
    args.identity = ModbusDeviceIdentification(
        info_name={
            "VendorName": "Pymodbus",
            "ProductCode": "PM",
            "VendorUrl": "https://github.com/pymodbus-dev/pymodbus/",
            "ProductName": "Pymodbus Server",
            "ModelName": "Pymodbus Server",
            "MajorMinorRevision": pymodbus_version,
        }
    )
    return args


def run_sync_server(args):
    """Run server.

    Args:
        args (ArgumentParser namespace): Previously parsed and configured execution context from arguments.

    Returns:
        Instance of started server.
    """
    txt = f"### start SYNC server, listening on {args.port} - {args.comm}"
    _logger.info(txt)
    if args.comm == "tcp":
        address = ("", args.port) if args.port else None
        server = StartTcpServer(
            context=args.context,  # Data storage
            identity=args.identity,  # server identify
            # TBD host=
            # TBD port=
            address=address,  # listen address
            # custom_functions=[],  # allow custom handling
            framer=args.framer,  # The framer strategy to use
            # TBD handler=None,  # handler for each session
            allow_reuse_address=True,  # allow the reuse of an address
            # ignore_missing_slaves=True,  # ignore request to a missing slave
            # broadcast_enable=False,  # treat slave_id 0 as broadcast address,
            # timeout=1,  # waiting time for request to complete
            # TBD strict=True,  # use strict timing, t1.5 for Modbus RTU
            # defer_start=False,  # Only define server do not activate
        )
    elif args.comm == "serial":
        # socat -d -d PTY,link=/tmp/ptyp0,raw,echo=0,ispeed=9600
        #             PTY,link=/tmp/ttyp0,raw,echo=0,ospeed=9600
        server = StartSerialServer(
            context=args.context,  # Data storage
            identity=args.identity,  # server identify
            # timeout=1,  # waiting time for request to complete
            port=args.port,  # serial port
            # custom_functions=[],  # allow custom handling
            framer=args.framer,  # The framer strategy to use
            # handler=None,  # handler for each session
            # stopbits=1,  # The number of stop bits to use
            # bytesize=7,  # The bytesize of the serial messages
            # parity="E",  # Which kind of parity to use
            baudrate=args.baudrate,  # The baud rate to use for the serial device
            # handle_local_echo=False,  # Handle local echo of the USB-to-RS485 adaptor
            # ignore_missing_slaves=True,  # ignore request to a missing slave
            # broadcast_enable=False,  # treat slave_id 0 as broadcast address,
            # strict=True,  # use strict timing, t1.5 for Modbus RTU
            # defer_start=False,  # Only define server do not activate
        )
    return server


if __name__ == "__main__":
    run_args = setup_server(description="Run synchronous server.")
    server = run_sync_server(run_args)
    server.shutdown()
