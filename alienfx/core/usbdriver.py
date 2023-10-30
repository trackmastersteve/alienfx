#
# usbdriver.py
#
# Copyright (C) 2013-2014 Ashwin Menon <ashwin.menon@gmail.com>
# Copyright (C) 2015-2024 Track Master Steve <trackmastersteve@gmail.com>
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

""" USB communication with an AlienFX controller.

This module provides the following classes:
AlienFXUSBDriver: low level USB communication API with an AlienFX controller.
"""

from builtins import hex
from builtins import object
import logging

import usb
from usb import USBError


class AlienFXUSBDriver(object):
    
    """ Provides low level acquire/release and read/write access to an AlienFX
    USB controller.
    """
    
    OUT_BM_REQUEST_TYPE = 0x21 
    OUT_B_REQUEST = 0x09 # bRequest = Set Configuration
    OUT_W_VALUE = 0x202  # configuration
    OUT_W_INDEX = 0x00   # must be 0 as per USB
    IN_BM_REQUEST_TYPE = 0xa1 
    IN_B_REQUEST = 0x01 # bRequest = Clear Feature
    IN_W_VALUE = 0x101
    IN_W_INDEX = 0x0
        
    def __init__(self, controller):
        self._control_taken = False
        self._controller = controller
        self._dev = None
    
    def write_packet(self, pkt):
        """ Write the given packet over USB to the AlienFX controller."""
        if not self._control_taken:
            return
        try:
            self._dev.ctrl_transfer(
                self.OUT_BM_REQUEST_TYPE, 
                self.OUT_B_REQUEST, self.OUT_W_VALUE, 
                self.OUT_W_INDEX, pkt, 0)
        except USBError as exc:
            logging.error("write_packet: {}".format(exc))
            
    def read_packet(self):
        """ Read a packet over USB from the AlienFX controller and return it."""
        if not self._control_taken:
            logging.error("read_packet: control not taken...")
            return
        try:
            pkt = self._dev.ctrl_transfer(
                self.IN_BM_REQUEST_TYPE, 
                self.IN_B_REQUEST, self.IN_W_VALUE, 
                self.IN_W_INDEX, self._controller.cmd_packet.PACKET_LENGTH, 0)
            return pkt
        except USBError as exc:
            logging.error("read_packet: {}".format(exc))

        
    def acquire(self):
        """ Acquire control from libusb of the AlienFX controller."""
        if self._control_taken:
            return
        self._dev = usb.core.find(
            idVendor=self._controller.vendor_id, 
            idProduct=self._controller.product_id)
        if (self._dev is None):
            msg = "ERROR: No AlienFX USB controller found; tried "
            msg += "VID {}".format(self._controller.vendor_id)
            msg += ", PID {}".format(self._controller.product_id)
            logging.error(msg)
        try:
            self._dev.detach_kernel_driver(0)
        except USBError as exc: 
            logging.error(
                "Cant detach kernel driver. Error : {}".format(exc.strerror))
        try:
            self._dev.set_configuration()
        except USBError as exc: 
            logging.error(
                "Cant set configuration. Error : {}".format(exc.strerror))
        try:
            usb.util.claim_interface(self._dev, 0)
        except USBError as exc: 
            logging.error(
                "Cant claim interface. Error : {}".format(exc.strerror))
        self._control_taken = True
        logging.debug("USB device acquired, VID={}, PID={}".format(
            hex(self._controller.vendor_id), hex(self._controller.product_id)))
        
    def release(self):
        """ Release control to libusb of the AlienFX controller."""
        if not self._control_taken:
            return
        try:
            usb.util.release_interface(self._dev, 0)
        except USBError as exc: 
            logging.error(
                "Cant release interface. Error : {}".format(exc.strerror))
        try:
            self._dev.attach_kernel_driver(0)
        except USBError as exc: 
            logging.error("Cant re-attach. Error : {}".format(exc.strerror))
        self._control_taken = False
        logging.debug("USB device released, VID={}, PID={}".format(
            hex(self._controller.vendor_id), hex(self._controller.product_id)))
