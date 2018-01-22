# -*- coding: utf-8 -*-
"""The Raspberry onewire bus

Installation :

Load modules at boot :

.. code-block:: bash

    sudo vim /etc/modules

To add :

.. code-block:: bash

    w1-gpio
    w1-therm

Update boot config :

.. code-block:: bash

    sudo vim /boot/config.txt

To add :

.. code-block:: bash

    dtoverlay=w1-gpio,gpiopin=4

"""

__license__ = """
    This file is part of Janitoo.

    Janitoo is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Janitoo is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Janitoo. If not, see <http://www.gnu.org/licenses/>.

"""
__author__ = 'Sébastien GALLET aka bibi21000'
__email__ = 'bibi21000@gmail.com'
__copyright__ = "Copyright © 2013-2014-2015-2016 Sébastien GALLET aka bibi21000"

# Set default logging handler to avoid "No handler found" warnings.
import logging
logger = logging.getLogger(__name__)
import os
from janitoo.bus import JNTBus

##############################################################
#Check that we are in sync with the official command classes
#Must be implemented for non-regression
from janitoo.classes import COMMAND_DESC

COMMAND_CONTROLLER = 0x1050

assert(COMMAND_DESC[COMMAND_CONTROLLER] == 'COMMAND_CONTROLLER')
##############################################################

from janitoo_raspberry_1wire import OID

def make_thread(options, force=False):
    if get_option_autostart(options, OID) or force:
        return Rpi1wireThread(options)
    else:
        return None

class Rpi1wireThread(JNTBusThread):
    """The I2C thread

    """
    def init_bus(self):
        """Build the bus
        """
        from janitoo_raspberry_1wire.bus_1wire import OnewireBus
        self.section = OID
        self.bus = OnewireBus(options=self.options, oid=self.section, product_name="Raspberry 1Wire bus")
