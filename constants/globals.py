# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.
#
# Author: Jeffersson Abreu (ctw6av)

import logging
import os

# Add a base to build absolute path's
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger()

format_string = f'[%(levelname)s] [%(module)s] %(message)s'
format_date = '%d-%m-%y %H:%M:%S'

logging.basicConfig(
    filename=f'{os.environ["HOME"]}/strino.log',
    format=format_string,
    datefmt=format_date,
    level=logging.INFO,
    filemode='w'
)
