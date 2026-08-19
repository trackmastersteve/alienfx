#
# acpi_controller.py
#
# Copyright (C) 2013-2014 Ashwin Menon <ashwin.menon@gmail. com>
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

""" Base class for ACPI/WMI-based AlienFX controllers.

This module provides the following classes: 
AlienFXACPIController:  base class for ACPI/WMI AlienFX controller chips
AlienFXACPIDriver: low level ACPI/WMI communication driver
"""

from builtins import hex
from builtins import object
import logging
import os
import struct

import alienfx. core.cmdpacket as alienfx_cmdpacket
from alienfx.core.themefile import AlienFXThemeFile
from functools import reduce


class AlienFXACPIDriver(object):
    
    """ Provides low level acquire/release and read/write access to an AlienFX
    ACPI/WMI controller via sysfs.
    """
    
    # WMI interface attributes
    WMI_COMMAND_ATTR = "lighting_control_state"
    WMI_ZONE_ATTR = "lighting_control_zone"
    
    def __init__(self, controller):
        self._control_taken = False
        self._controller = controller
        self._acpi_path = None
        
    def write_packet(self, pkt):
        """ Write the given packet to the ACPI/WMI interface."""
        if not self._control_taken:
            logging.warning("write_packet: control not taken, skipping write")
            return
            
        if not self._acpi_path or not os.path.exists(self._acpi_path):
            logging.error("write_packet: ACPI path not available:  {}".format(self._acpi_path))
            return
            
        try:
            # Convert packet to bytes if needed
            if isinstance(pkt, list):
                pkt_bytes = bytes(pkt)
            else:
                pkt_bytes = pkt
                
            # Write to the WMI interface
            # The alienware-wmi driver expects specific formats
            # For now, we'll write the raw packet data
            control_file = os.path.join(self._acpi_path, "rgb_zones", self.WMI_COMMAND_ATTR)
            
            if os.path.exists(control_file):
                with open(control_file, 'wb') as f:
                    f.write(pkt_bytes)
                logging.debug("ACPI write successful:  {} bytes".format(len(pkt_bytes)))
            else:
                logging.error("Control file not found: {}".format(control_file))
                
        except IOError as exc:
            logging.error("write_packet ACPI error: {}".format(exc))
        except Exception as exc:
            logging.error("write_packet unexpected error: {}".format(exc))
            
    def read_packet(self):
        """ Read a packet from the ACPI/WMI interface and return it."""
        if not self._control_taken:
            logging.error("read_packet: control not taken...")
            return None
            
        if not self._acpi_path or not os.path.exists(self._acpi_path):
            logging.error("read_packet: ACPI path not available:  {}".format(self._acpi_path))
            return None
            
        try:
            control_file = os.path.join(self._acpi_path, "rgb_zones", self.WMI_COMMAND_ATTR)
            
            if os.path.exists(control_file):
                with open(control_file, 'rb') as f:
                    pkt = f.read(self._controller.cmd_packet. PACKET_LENGTH)
                    if pkt:
                        logging.debug("ACPI read successful: {} bytes".format(len(pkt)))
                        return list(pkt) if isinstance(pkt, bytes) else pkt
            else:
                logging.error("Control file not found: {}".format(control_file))
                
        except IOError as exc: 
            logging.error("read_packet ACPI error: {}".format(exc))
        except Exception as exc:
            logging.error("read_packet unexpected error: {}". format(exc))
            
        return None

    def acquire(self):
        """ Acquire control of the ACPI/WMI AlienFX controller."""
        if self._control_taken:
            logging.debug("ACPI device already acquired")
            return
            
        # Get ACPI path from controller
        if hasattr(self._controller, 'acpi_path'):
            self._acpi_path = self._controller.acpi_path
        else:
            self._acpi_path = "/sys/devices/platform/alienware-wmi"
            
        # Check if the ACPI/WMI interface exists
        if not os.path. exists(self._acpi_path):
            msg = "ERROR: No AlienFX ACPI/WMI controller found at: {}".format(self._acpi_path)
            msg += "\nMake sure the alienware-wmi kernel module is loaded."
            msg += "\nRun: sudo modprobe alienware-wmi"
            logging.error(msg)
            raise IOError(msg)
            
        # Check for required sysfs attributes
        control_file = os.path.join(self._acpi_path, self.WMI_COMMAND_ATTR)
        if not os.path.exists(control_file):
            logging.warning("Control attribute not found: {}".format(control_file))
            logging.warning("Continuing anyway, some features may not work")
            
        self._control_taken = True
        logging.info("ACPI/WMI device acquired:  {}".format(self._acpi_path))
        
    def release(self):
        """ Release control of the ACPI/WMI AlienFX controller."""
        if not self._control_taken:
            return
            
        # No special cleanup needed for ACPI/WMI interface
        self._control_taken = False
        logging.debug("ACPI/WMI device released:  {}".format(self._acpi_path))


class AlienFXACPIController(object):
    
    """ Provides facilities to communicate with an ACPI/WMI-based AlienFX controller. 
    
    This class provides methods to send commands to an ACPI/WMI AlienFX controller,
    and receive status from the controller. It must be overridden to provide
    behaviour specific to a particular AlienFX controller.
    """
    
    # List of all ACPI-based subclasses.  Subclasses must add instances of
    # themselves to this list. 
    supported_controllers = []
    
    # Zone names (same as USB controllers)
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
    ZONE_RIGHT_DISPLAY = "Right Display"
    ZONE_LEFT_DISPLAY = "Left Display"

    # State names
    STATE_BOOT = "Boot"
    STATE_AC_SLEEP = "AC Sleep"
    STATE_AC_CHARGED = "AC Charged"
    STATE_AC_CHARGING = "AC Charging"
    STATE_BATTERY_SLEEP = "Battery Sleep"
    STATE_BATTERY_ON = "Battery On"
    STATE_BATTERY_CRITICAL = "Battery Critical"
    STATE_AC_ON = "AC On"

    ALIENFX_CONTROLLER_TYPE = "acpi"
    
    def __init__(self, conrev=1):
        # conrev=1  -> old controllers (DEFAULT)
        # conrev=2  -> newer controllers (17R4 ...)
        self.zone_map = {}
        self.power_zones = []
        self.reset_types = {}
        self.state_map = {}
        self.vendor_id = 0  # Not used for ACPI, kept for compatibility
        self.product_id = 0  # Not used for ACPI, kept for compatibility
        self.acpi_path = "/sys/devices/platform/alienware-wmi"

        self.cmd_packet = alienfx_cmdpacket.AlienFXCmdPacket(conrev)
        self._driver = AlienFXACPIDriver(self)

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
        controller_type = getattr(self, "_controller_type", self.ALIENFX_CONTROLLER_TYPE)
        if controller_type != self.ALIENFX_CONTROLLER_TYPE:
            logging.debug("WMI status ping skipped")
            return
        pkt = self.cmd_packet. make_cmd_get_status()
        logging.debug("SENDING:  {}".format(self.pkt_to_string(pkt)))
        self._driver.write_packet(pkt)
        # ACPI might not support reading status the same way
        # Try to read, but don't fail if it doesn't work
        try:
            self._driver.read_packet()
        except Exception as e:
            logging.debug("Status read not supported on ACPI: {}".format(e))
            
    def _reset(self, reset_type):
        """ Send a "reset" packet to the AlienFX controller."""
        reset_code = self._get_reset_code(reset_type)
        pkt = self. cmd_packet.make_cmd_reset(reset_code)
        logging.debug("SENDING: {}".format(self.pkt_to_string(pkt)))
        self._driver.write_packet(pkt)
        
    def _wait_controller_ready(self):
        """ Keep sending a "get status" packet to the AlienFX controller and 
        return only when the controller is ready. 
        
        ACPI controllers can be polled,  status checking may not be available. 
        WMI controllers do not expose the same status path, so readiness is treated as immediate.
        ACPI-style effects like morphing are not replayed through the WMI RGB interface.
        """
        controller_type = getattr(self, "_controller_type", self.ALIENFX_CONTROLLER_TYPE)
        if controller_type != self.ALIENFX_CONTROLLER_TYPE:
            logging.debug("WMI controller ready check skipped")
            return

        ready = False
        errcount = 0
        max_retries = 10  # Fewer retries for ACPI

        while not ready and errcount < max_retries:
            pkt = self.cmd_packet.make_cmd_get_status()
            logging.debug("SENDING: {}".format(self.pkt_to_string(pkt)))
            self._driver.write_packet(pkt)
            try:
                resp = self._driver.read_packet()
                if resp:
                    ready = (resp[0] == self.cmd_packet.STATUS_READY)
                else:
                    # If we can't read status, assume ready after a few tries
                    errcount += 1
                    if errcount >= 3:
                        logging.debug("ACPI status not available, assuming ready")
                        ready = True
            except TypeError:
                errcount += 1
                logging.debug("No Status received yet...  Failed tries={}".format(errcount))
            except Exception as e:
                logging.debug("Status check error: {}".format(e))
                errcount += 1

        if not ready:
            logging.warning("Controller status could not be verified (ACPI mode)")
        
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
        """ Given the name of a reset action, return its code.  """
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
        SAVE_NEXT commands.  Also, the final command is one to set the colour
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
                    zone_cmds. append(loop_cmd)
                if not boot:
                    zone_cmds.append(pkt. make_cmd_save_next(state))
                zone_cmds.append(pkt.make_cmd_loop_block_end())
        if zone_cmds:
            if not boot:
                zone_cmds.append(pkt.make_cmd_save())
        if boot:
            zone_cmds. append(
                pkt.make_cmd_set_colour(
                    block, self._get_no_zone_code(), (0,0,0)))
            zone_cmds.append(pkt.make_cmd_loop_block_end())
        return zone_cmds
        
    def _send_cmds(self, cmds):
        """ Send the given commands to the controller.  """
        for cmd in cmds:
            logging.debug("SENDING: {}". format(self.pkt_to_string(cmd)))
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
        except Exception as e:
            logging. error("Error setting theme on ACPI controller: {}".format(e))
            raise
        finally:
            self._driver.release()
