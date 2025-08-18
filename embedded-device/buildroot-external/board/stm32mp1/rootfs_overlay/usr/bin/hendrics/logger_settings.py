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

import logging

LOGFILE_NAME = "STM32_python.log"
LOGGING_LEVEL = "WARNING"

def setup_logger():
    """Configures and returns a logger instance that records log messages to a file named STM32_python.log."""
    
    logger = logging.getLogger("my_logger")
    logger.setLevel(level=LOGGING_LEVEL)

    if not logger.handlers:
        # Create a FileHandler to write log messages to the specified file.
        file_handler = logging.FileHandler(filename=LOGFILE_NAME, mode="a", encoding="utf-8")
        file_handler.setLevel(level=LOGGING_LEVEL)

        # Define the format for log entries.
        FORMAT = '%(asctime)s - %(levelname)s - %(filename)s: %(message)s'
        formatter = logging.Formatter(FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    return logger


