# -*- coding: utf-8 -*-
"""The Raspberry camera worker

Installation :

.. code-block:: bash

    sudo apt-get install python-pycamera

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
import os, sys
import threading
import time
import datetime
import socket
import re

from janitoo.thread import JNTBusThread
from janitoo.bus import JNTBus
from janitoo.component import JNTComponent
from janitoo.thread import BaseThread
from janitoo.options import get_option_autostart

from janitoo_raspberry_1wire.thread_1wire import OID

##############################################################
#Check that we are in sync with the official command classes
#Must be implemented for non-regression
from janitoo.classes import COMMAND_DESC

COMMAND_CAMERA_PREVIEW = 0x2200
COMMAND_CAMERA_PHOTO = 0x2201
COMMAND_CAMERA_VIDEO = 0x2202
COMMAND_CAMERA_STREAM = 0x2203

assert(COMMAND_DESC[COMMAND_CAMERA_PREVIEW] == 'COMMAND_CAMERA_PREVIEW')
assert(COMMAND_DESC[COMMAND_CAMERA_PHOTO] == 'COMMAND_CAMERA_PHOTO')
assert(COMMAND_DESC[COMMAND_CAMERA_VIDEO] == 'COMMAND_CAMERA_VIDEO')
assert(COMMAND_DESC[COMMAND_CAMERA_STREAM] == 'COMMAND_CAMERA_STREAM')
##############################################################

class OnewireBus(JNTBus):
    """A pseudo-bus to handle the Raspberry Onewire Bus
    """
    def __init__(self, oid=OID, **kwargs):
        """
        :param int bus_id: the SMBus id (see Raspberry Pi documentation)
        :param kwargs: parameters transmitted to :py:class:`smbus.SMBus` initializer
        """
        try:
            os.system('modprobe w1-gpio')
            os.system('modprobe w1-therm')
        except :
            log.exception("Can't load w1-* kernel modules")
        JNTBus.__init__(self, oid=oid, **kwargs)
        self._1wire_lock = threading.Lock()
        uuid="%s_sensors_dir"%OID
        self.values[uuid] = self.value_factory['config_string'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The sensor directory',
            label='dir.',
            default='/sys/bus/w1/devices/',
        )

    def acquire(self):
        """Get a lock on the bus"""
        pass

    def release(self):
        """Release a lock on the bus"""
        pass

    def check_heartbeat(self):
        """Check that the bus is 'available'. Is replaced by the node one when it's creates

        """
        sdir = self.get_bus_value("sensors_dir").data
        return sdir is not None and os.path.isdir(sdir)
