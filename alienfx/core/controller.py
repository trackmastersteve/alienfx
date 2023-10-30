#
# controller.py
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

""" Base classes for AlienFX controller chips. These must be subclassed for 
specific controllers.

This module provides the following classes:
AlienFXController: base class for AlienFX controller chips
"""

from builtins import hex
from builtins import object
import logging

import alienfx.core.usbdriver as alienfx_usbdriver
import alienfx.core.cmdpacket as alienfx_cmdpacket
from alienfx.core.themefile import AlienFXThemeFile
from functools import reduce

class AlienFXController(object):
    
    """ Provides facilities to communicate with an AlienFX controller.
    
    This class provides methods to send commands to an AlienFX controller, and
    receive status from the controller. It must be overridden to provide
    behaviour specific to a particular AlienFX controller.
    """
    
    # List of all subclasses of this class. Subclasses must add instances of
    # themselves to this list. See README for details.
    supported_controllers = []
    
    # Zone names
    ZONE_LEFT_KEYBOARD = "Left Keyboard"
    ZONE_MIDDLE_LEFT_KEYBOARD = "Middle-left Keyboard"
    ZONE_MIDDLE_RIGHT_KEYBOARD = "Middle-right Keyboard"
    ZONE_RIGHT_KEYBOARD = "Right Keyboard"
    ZONE_RIGHT_SPEAKER = "Right Speaker"
    ZONE_LEFT_SPEAKER = "Left Speaker"
    ZONE_ALIEN_HEAD = "Alien Head"
    ZONE_LOGO = "Logo"
    ZONE_TOUCH_PAD = "Touchpad"
    ZONE_MEDIA_BAR = "Media Bar"
    ZONE_STATUS_LEDS = "Status LEDs"
    ZONE_POWER_BUTTON = "Power Button"
    ZONE_HDD_LEDS = "HDD LEDs"
    ZONE_RIGHT_DISPLAY = "Right Display"  # LED-bar display right side, as built in the AW17R4
    ZONE_LEFT_DISPLAY = "Left Display"  # LED-bar display left side, as built in the AW17R4

    # State names
    STATE_BOOT = "Boot"
    STATE_AC_SLEEP = "AC Sleep"
    STATE_AC_CHARGED = "AC Charged"
    STATE_AC_CHARGING = "AC Charging"
    STATE_BATTERY_SLEEP = "Battery Sleep"
    STATE_BATTERY_ON = "Battery On"
    STATE_BATTERY_CRITICAL = "Battery Critical"

    ALIENFX_CONTROLLER_TYPE = "old"  # Default controllertype=old. Note that modern controllers are using 8 bits per color. older ones just 4
    
    def __init__(self, conrev=1):  # conrev defaulting to 1 to maintain compatibility with old definitions
        # conrev=1  -> old controllers (DEFAULT)
        # conrev=2  -> newer controllers (17R4 ...)
        self.zone_map = {}
        self.power_zones = []
        self.reset_types = {}
        self.state_map = {}
        self.vendor_id = 0
        self.product_id = 0

        self.cmd_packet = alienfx_cmdpacket.AlienFXCmdPacket(conrev)  # Loads the cmdpacket.

        self._driver = alienfx_usbdriver.AlienFXUSBDriver(self)




    def get_zone_name(self, pkt):
        """ Given 3 bytes of a command packet, return a string zone
            name corresponding to it
        """ 
        zone_mask = (pkt[0] << 16) + (pkt[1] << 8) + pkt[2]
        zone_name = ""
        for zone in self.zone_map:
            bit_mask = self.zone_map[zone]
            if zone_mask & bit_mask:
                if zone_name != "": 
                    zone_name += ","
                zone_name += zone
                zone_mask &= ~bit_mask
        if zone_mask != 0:
            if zone_name != "":
                zone_name += ","
            zone_name += "UNKNOWN({})".format(hex(zone_mask))
        return zone_name
        
    def get_state_name(self, state):
        """ Given a state number, return a string state name """
        for state_name in self.state_map:
            if self.state_map[state_name] == state:
                return state_name
        return "UNKNOWN"
            
    def get_reset_type_name(self, num):
        """ Given a reset number, return a string reset name """
        if num in list(self.reset_types.keys()):
            return self.reset_types[num]
        else:
            return "UNKNOWN"

    def _ping(self):
        """ Send a get-status command to the controller."""
        pkt = self.cmd_packet.make_cmd_get_status()
        logging.debug("SENDING: {}".format(self.pkt_to_string(pkt)))
        self._driver.write_packet(pkt)
        self._driver.read_packet()
            
    def _reset(self, reset_type):
        """ Send a "reset" packet to the AlienFX controller."""
        reset_code = self._get_reset_code(reset_type)
        pkt = self.cmd_packet.make_cmd_reset(reset_code)
        logging.debug("SENDING: {}".format(self.pkt_to_string(pkt)))
        self._driver.write_packet(pkt)
        
    def _wait_controller_ready(self):
        """ Keep sending a "get status" packet to the AlienFX controller and 
        return only when the controller is ready
        """
        ready = False
        errcount=0
        while not ready:
            pkt = self.cmd_packet.make_cmd_get_status()
            logging.debug("SENDING: {}".format(self.pkt_to_string(pkt)))
            self._driver.write_packet(pkt)
            try:
                resp = self._driver.read_packet()
                ready = (resp[0] == self.cmd_packet.STATUS_READY)
            except TypeError:
                errcount += 1
                logging.debug("No Status received yet... Failed tries=" + str(errcount))
            if errcount > 50:
                logging.error("Controller status could not be retrieved. Is the device already in use?")
                quit(-99)
        
    def pkt_to_string(self, pkt_bytes):
        """ Return a human readable string representation of an AlienFX
        command packet.
        """
        return self.cmd_packet.pkt_to_string(pkt_bytes, self)
        
    def _get_no_zone_code(self):
        """ Return a zone code corresponding to all non-visible zones."""
        zone_codes = [self.zone_map[x] for x in self.zone_map] 
        return ~reduce(lambda x,y: x|y, zone_codes, 0)
        
    def _get_zone_codes(self, zone_names):
        """ Given zone names, return the zone codes they refer to.
        """
        zones = 0
        for zone in zone_names:
            if zone in self.zone_map:
                zones |= self.zone_map[zone]
        return zones
        
    def _get_reset_code(self, reset_name):
        """ Given the name of a reset action, return its code. """
        for reset in self.reset_types:
            if reset_name == self.reset_types[reset]:
                return reset
        logging.warning("Unknown reset type: {}".format(reset_name))
        return 0
        
    def _make_loop_cmds(self, themefile, zones, block, loop_items):
        """ Given loop-items from the theme file, return a list of loop
        commands.
        """
        loop_cmds = []
        pkt = self.cmd_packet
        for item in loop_items:
            item_type = themefile.get_action_type(item)
            item_colours = themefile.get_action_colours(item)
            if item_type == AlienFXThemeFile.KW_ACTION_TYPE_FIXED:
                if len(item_colours) != 1:
                    logging.warning("fixed must have exactly one colour value")
                    continue
                loop_cmds.append(
                    pkt.make_cmd_set_colour(block, zones, item_colours[0]))
            elif item_type == AlienFXThemeFile.KW_ACTION_TYPE_BLINK:
                if len(item_colours) != 1:
                    logging.warning("blink must have exactly one colour value")
                    continue
                loop_cmds.append(
                    pkt.make_cmd_set_blink_colour(block, zones, item_colours[0]))
            elif item_type == AlienFXThemeFile.KW_ACTION_TYPE_MORPH:
                if len(item_colours) != 2:
                    logging.warning("morph must have exactly two colour values")
                    continue
                loop_cmds.append(
                    pkt.make_cmd_set_morph_colour(
                        block, zones, item_colours[0], item_colours[1]))
            else:
                logging.warning("unknown loop item type: {}".format(item_type))
        return loop_cmds
        
    def _make_zone_cmds(self, themefile, state_name, boot=False):
        """ Given a theme file, return a list of zone commands.
        
        If 'boot' is True, then the colour commands created are not saved with
        SAVE_NEXT commands. Also, the final command is one to set the colour
        of all non-visible zones to black.
        """
        zone_cmds = []
        block = 1
        pkt = self.cmd_packet
        state = self.state_map[state_name]
        state_items = themefile.get_state_items(state_name)
        for item in state_items:
            zone_codes = self._get_zone_codes(themefile.get_zone_names(item))
            loop_items = themefile.get_loop_items(item)
            loop_cmds = self._make_loop_cmds(
                themefile, zone_codes, block, loop_items)
            if (loop_cmds):
                block += 1
                for loop_cmd in loop_cmds:
                    if not boot:
                        zone_cmds.append(pkt.make_cmd_save_next(state))
                    zone_cmds.append(loop_cmd)
                if not boot:
                    zone_cmds.append(pkt.make_cmd_save_next(state))
                zone_cmds.append(pkt.make_cmd_loop_block_end())
        if zone_cmds:
            if not boot:
                zone_cmds.append(pkt.make_cmd_save())
        if boot:
            zone_cmds.append(
                pkt.make_cmd_set_colour(
                    block, self._get_no_zone_code(), (0,0,0)))
            zone_cmds.append(pkt.make_cmd_loop_block_end())
        return zone_cmds
        
    def _send_cmds(self, cmds):
        """ Send the given commands to the controller. """
        for cmd in cmds:
            logging.debug("SENDING: {}".format(self.pkt_to_string(cmd)))
            self._driver.write_packet(cmd)

    def set_theme(self, themefile):
        """ Send the given theme settings to the controller. This should result
        in the lights changing to the theme settings immediately.
        """
        try:
            self._driver.acquire()
            cmds_boot = []
            pkt = self.cmd_packet
            
            # prepare the controller
            self._ping()
            self._reset("all-lights-on")
            self._wait_controller_ready()
            
            for state_name in self.state_map:
                cmds = []
                cmds = self._make_zone_cmds(themefile, state_name)
                # Boot block commands are saved for sending again later.
                # The second time, they are sent without SAVE_NEXT commands.
                if (state_name == self.STATE_BOOT):
                    cmds_boot = self._make_zone_cmds(
                        themefile, state_name, boot=True)
                self._send_cmds(cmds)
            cmd = pkt.make_cmd_set_speed(themefile.get_speed())
            self._send_cmds([cmd])
            # send the boot block commands again
            self._send_cmds(cmds_boot)
            cmd = pkt.make_cmd_transmit_execute()
            self._send_cmds([cmd])
        finally:
            self._driver.release()

