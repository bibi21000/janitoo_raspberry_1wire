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

import os
import re

from janitoo.component import JNTComponent

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

from janitoo_raspberry_1wire import OID

def make_ds18b20(**kwargs):
    return DS18B20(**kwargs)

class DS18B20(JNTComponent):
    """ A generic component for gpio """

    def __init__(self, bus=None, addr=None, **kwargs):
        """
        """
        oid = kwargs.pop('oid', '%s.ds18b20'%OID)
        name = kwargs.pop('name', "Onewire DS18B20 sensor")
        product_name = kwargs.pop('product_name', "DS18B20 sensor")
        product_type = kwargs.pop('product_type', "Temperature sensor")
        product_manufacturer = kwargs.pop('product_manufacturer', "Janitoo")
        JNTComponent.__init__(self, oid=oid, bus=bus, addr=addr, name=name,
                product_name=product_name, product_type=product_type, product_manufacturer=product_manufacturer, **kwargs)
        logger.debug("[%s] - __init__ node uuid:%s", self.__class__.__name__, self.uuid)

        uuid="temperature"
        self.values[uuid] = self.value_factory['sensor_temperature'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The temperature',
            label='Temp',
            get_data_cb=self.temperature,
        )
        poll_value = self.values[uuid].create_poll_value(default=300)
        self.values[poll_value.uuid] = poll_value

        uuid="hexadd"
        self.values[uuid] = self.value_factory['config_string'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The hexadecimal address of the DS18B20',
            label='Addr',
            default=kwargs.get("hexadd", "28-000005e2fdc3"),
        )

    def temperature(self, node_uuid, index):
        ret = None
        f = None
        try:
            f=open(os.path.join(self.get_bus_value("sensors_dir", oid = OID).data, self.values["hexadd"].get_data_index(index=index), 'w1_slave'), 'r')
            line = f.readline()
            if re.match(r"([0-9a-f]{2} ){9}: crc=[0-9a-f]{2} YES", line):
                line = f.readline()
                m = re.match(r"([0-9a-f]{2} ){9}t=([+-]?[0-9]+)", line)
                if m:
                    data = str(float(m.group(2)) / 1000.0)
                    ret = float(data)
        except Exception:
            logger.exception('[%s] - Exception when reading sensor', self.__class__.__name__)
        finally:
            if f is not None:
                f.close()
        return ret

    def check_heartbeat(self):
        """Check that the component is 'available'

        """
        if 'temperature' not in self.values:
            return False
        return self.values['temperature'].data is not None
