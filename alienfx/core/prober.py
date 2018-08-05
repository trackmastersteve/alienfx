#
# prober.py
#
# Copyright (C) 2013-2014 Ashwin Menon <ashwin.menon@gmail.com>
# Copyright (C) 2015-2018 Track Master Steve <trackmastersteve@gmail.com>
#
# Alienfx is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Alienfx is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with alienfx.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#

""" Alien FX controller prober class.

This module provides the following classes:
AlienFXProber: probes the USB bus for supported Alien FX controllers.
"""

from builtins import object
from builtins import int
import usb
import usb.core

from alienfx.core.controller import AlienFXController as AlienFXController

""" Import all subclasses of AlienFXController here. """
import alienfx.core.controller_area51
import alienfx.core.controller_aurora
import alienfx.core.controller_m11xr1
import alienfx.core.controller_m11xr2
import alienfx.core.controller_m11xr3
import alienfx.core.controller_m13xr2
import alienfx.core.controller_m13xr3
import alienfx.core.controller_m14xr1
import alienfx.core.controller_m14xr2
import alienfx.core.controller_m14xr3
import alienfx.core.controller_m15x
import alienfx.core.controller_m17x
import alienfx.core.controller_m17xr3
import alienfx.core.controller_m17xr4
import alienfx.core.controller_17r3
import alienfx.core.controller_m18xr2

class AlienFXProber(object):
    
    """ Provides facilities for probing the USB bus for supported Alien FX
    controllers.
    """
        
    @staticmethod
    def get_controller():
        """ Go through the supported_controllers list in AlienFXController
        and see if any of them exist on the USB bus, Return the first one
        found, or None if none are found.
        """
        for controller in AlienFXController.supported_controllers:
            vid = controller.vendor_id
            pid = controller.product_id
            dev = usb.core.find(idVendor=vid, idProduct=pid)
            if dev is not None:
                return controller
        return None

    @staticmethod
    def find_controllers(vendor):
        """Go through the usb-bus and find devices(and most likely controllers) by vendor-id"""
        vid = int(vendor, 16)  # Convert our given Vendor-HEX-String to an equivalent intenger

        devs = usb.core.find(find_all=1)  # All USB devices
        devices = []  # List of found AFX-Controllers
        for dev in devs:
            if dev is not None:
                if dev.idVendor is not None:
                    if dev.idVendor == vid:
                        devices.append(dev)
        if len(devices):
            return devices
        return None
