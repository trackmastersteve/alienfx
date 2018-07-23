#
# zonescanner.py
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
#
# Zonescanner-class which should test different zone codes. - This could make adding new devices easier.
# initial development by derco0n <https://github.com/derco0n> (July/2018)

from alienfx.core.prober import AlienFXProber
from builtins import str,hex
import alienfx.core.controller as alienfx_controller
import os


class Zonescanner:
    def __init__(self, vendorid):
        self.vendorid=vendorid

    def scan(self):
        if os.geteuid() != 0:
            exit("You need to have root privileges to run zonescanning as we need to probe usb-devices.\nPlease try again, this time using 'sudo'. Exiting.")

        afxcontroldevs=AlienFXProber.find_controllers(self.vendorid)  # Get a list of all usb-devices with the given vendor-id
        for controller in afxcontroldevs:
            print("Found device \""+str(hex(controller.idVendor))+" / "+str(hex(controller.idProduct))+"\". - Testing zones...")
            # TODO: Perform zone scanning for each controller found...

        return False