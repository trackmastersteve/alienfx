#
# cmdpacket.py
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
# Tried to implement a unified cmdpacket-class for all Alien-FX-controllers.
# It seems that Dell / Alienware ist modifying the protocol in every incarnation of their devices.
# This is based on the classic cmdpacket.py and newcmdpacket.py.bak created by me earlier.
#
# This should replace both old files at least work for the old models and the mid-aged 2016 (17R4 and 15R3) controllers
# Dennis <derCo0n> Marx (https://github.com/derco0n) 2019/12
#

""" Base class for AlienFX command packets. This may be subclassed for
specific controllers.

This module provides the following classes:
AlienFXCmdPacket: base class for AlienFX command packets
"""

from builtins import hex
from builtins import object

class AlienFXCmdPacket(object):

    """Provides facilities to parse and create packets

    This class provides methods to parse binary packets into human readable
    strings. It also provides methods to create binary packets.
    """

    # Command codes
    CMD_SET_MORPH_COLOUR = 0x1
    CMD_SET_BLINK_COLOUR = 0x2
    CMD_SET_COLOUR = 0x3
    CMD_LOOP_BLOCK_END = 0x4
    CMD_TRANSMIT_EXECUTE = 0x5
    CMD_GET_STATUS = 0x6
    CMD_RESET = 0x7
    CMD_SAVE_NEXT = 0x8
    CMD_SAVE = 0x9
    CMD_SET_SPEED = 0xe

    # Status codes
    STATUS_BUSY = 0x11
    STATUS_READY = 0x10
    STATUS_UNKNOWN_COMMAND = 0x12




    command_parsers = {}

    def __init__(self, controlrev=1):
        # controlrev = 1    -> Classic models
        # Controlrev = 2    -> 17R4 / 15R3
        # Controller = ...  -> Please implement changes needed if your device is newer and needs modifications. But please don't break things working for other devices.

        self.controllerrevision = controlrev

        if self.controllerrevision == 1:
            # Old controllers   -> 4 Bit per colors
            self.PACKET_LENGTH = 9
        elif self.controllerrevision == 2:
            # 17R4 controllers  -> 8 Bits per colors
            self.PACKET_LENGTH = 12

        self.command_parsers = {
            self.CMD_SET_MORPH_COLOUR: self._parse_cmd_set_morph_colour,
            self.CMD_SET_BLINK_COLOUR: self._parse_cmd_set_blink_colour,
            self.CMD_SET_COLOUR: self._parse_cmd_set_colour,
            self.CMD_LOOP_BLOCK_END: self._parse_cmd_loop_block_end,
            self.CMD_TRANSMIT_EXECUTE: self._parse_cmd_transmit_execute,
            self.CMD_GET_STATUS: self._parse_cmd_get_status,
            self.CMD_RESET: self._parse_cmd_reset,
            self.CMD_SAVE_NEXT: self._parse_cmd_save_next,
            self.CMD_SAVE: self._parse_cmd_save,
            self.CMD_SET_SPEED: self._parse_cmd_set_speed
        }

    # @staticmethod
    def _unpack_colour_pair(self, pkt):
        """ Unpack two colour values from the given packet and return them as a
        list of two tuples (each colour is a 3-member tuple)

        TODO: This might need improvement for newer controllers...
        """
        red1 = hex(pkt[0] >> 4)
        green1 = hex(pkt[0] & 0xf)
        blue1 = hex(pkt[1] >> 4)
        red2 = hex(pkt[1] & 0xf)
        green2 = hex(pkt[2] >> 4)
        blue2 = hex(pkt[2] & 0xf)
        return [(red1, green1, blue1), (red2, green2, blue2)]

    def _pack_colour_pair(self, colour1, colour2):
        """ Pack two colours into a list of bytes and return the list. Each
        colour is a 3-member tuple
        """
        (red1, green1, blue1) = colour1
        (red2, green2, blue2) = colour2
        pkt = []

        if self.PACKET_LENGTH == 9:
            # Old controllers:
            # ================
            pkt.append(((red1&0xf)<<4) + (green1&0xf))
            pkt.append(((blue1&0xf)<<4) + (red2&0xf))
            pkt.append(((green2&0xf)<<4) + (blue2&0xf))
        elif self.PACKET_LENGTH == 12:
            # Newer controllers:
            # ==================
            # Theoretically due to the 8-Bits per pixel, the colors could be stepped much finer
            # But we want to use the existing JSON-Definitions
            red8_1 = red1 / float(15) * 255
            green8_1 = green1 / float(15) * 255
            blue8_1 = blue1 / float(15) * 255
            red8_2 = red2 / float(15) * 255
            green8_2 = green2 / float(15) * 255
            blue8_2 = blue2 / float(15) * 255
            pkt.append(int(red8_1))
            pkt.append(int(green8_1))
            pkt.append(int(blue8_1))
            pkt.append(int(red8_2))
            pkt.append(int(green8_2))
            pkt.append(int(blue8_2))
        return pkt

    # @staticmethod
    def _unpack_colour(self, pkt):
        """ Unpack a colour value from the given packet and return it as a
        3-member tuple

        TODO: This too might need improvement for newer controllers
        """
        red = hex(pkt[0] >> 4)
        green = hex(pkt[0] & 0xf)
        blue = hex(pkt[1] >> 4)
        return (red, green, blue)

    def _pack_colour(self, colour):
        """ Pack a colour into a list of bytes and return the list.
        colour is a 3-member tuple
        """
        (red, green, blue) = colour
        pkt = []
        if self.PACKET_LENGTH == 9:
            # Old controllers:
            # ================
            pkt.append(((red&0xf)<<4) + (green&0xf))
            pkt.append((blue&0xf)<<4)
        elif self.PACKET_LENGTH == 12:
            # Newer controllers:
            # ==================
            # Theoretically due to the 8-Bits per pixel, the colors could be stepped much finer
            # But we want to use the existing JSON-Definitions
            red8 = red / float(15) * 255
            green8 = green / float(15) * 255
            blue8 = blue / float(15) * 255
            pkt.append(int(red8))
            pkt.append(int(green8))
            pkt.append(int(blue8))
        return pkt

    # @classmethod
    def _parse_cmd_set_morph_colour(self, args):
        """ Parse a packet containing the "set morph colour" command and
        return it as a human readable string.
        """
        pkt = args["pkt"]
        controller = args["controller"]
        [(red1, green1, blue1), (red2, green2, blue2)] = (
            self._unpack_colour_pair(pkt[6:9]))
        msg = "SET_MORPH_COLOUR: "
        msg += "BLOCK: {}".format(pkt[2])
        msg += ", ZONE: {}".format(controller.get_zone_name(pkt[3:6]))
        msg += ", ({},{},{})-({},{},{})".format(
            red1, green1, blue1, red2, green2, blue2)
        return msg

    # @classmethod
    def _parse_cmd_set_blink_colour(self, args):
        """ Parse a packet containing the "set blink colour" command and
        return it as a human readable string.
        """
        pkt = args["pkt"]
        controller = args["controller"]
        (red, green, blue) = self._unpack_colour(pkt[6:8])
        msg = "SET_BLINK_COLOUR: "
        msg += "BLOCK: {}".format(pkt[2])
        msg += ", ZONE: {}".format(controller.get_zone_name(pkt[3:6]))
        msg += ", ({},{},{})".format(red, green, blue)
        return msg

    # @classmethod
    def _parse_cmd_set_colour(self, args):
        """ Parse a packet containing the "set colour" command and
        return it as a human readable string.
        """
        pkt = args["pkt"]
        controller = args["controller"]
        (red, green, blue) = self._unpack_colour(pkt[6:8])
        msg = "SET_COLOUR: "
        msg += "BLOCK: {}".format(pkt[2])
        msg += ", ZONE: {}".format(controller.get_zone_name(pkt[3:6]))
        msg += ", ({},{},{})".format(red, green, blue)
        return msg

    # @classmethod
    def _parse_cmd_loop_block_end(self, args):
        """ Parse a packet containing the "loop block end" command and
        return it as a human readable string.
        """
        return "LOOP_BLOCK_END"

    # @classmethod
    def _parse_cmd_transmit_execute(self, args):
        """ Parse a packet containing the "transmit execute" command and
        return it as a human readable string.
        """
        return "TRANSMIT_EXECUTE"

    # @classmethod
    def _parse_cmd_get_status(self, args):
        """ Parse a packet containing the "get status" command and
        return it as a human readable string.
        """
        return "GET_STATUS"

    # @classmethod
    def _parse_cmd_reset(self, args):
        """ Parse a packet containing the "reset" command and
        return it as a human readable string.
        """
        pkt = args["pkt"]
        controller = args["controller"]
        return "RESET: {}".format(controller.get_reset_type_name(pkt[2]))

    # @classmethod
    def _parse_cmd_save_next(self, args):
        """ Parse a packet containing the "save next" command and
        return it as a human readable string.
        """
        pkt = args["pkt"]
        controller = args["controller"]
        return "SAVE_NEXT: STATE {}".format(controller.get_state_name(pkt[2]))

    # @classmethod
    def _parse_cmd_save(self, args):
        """ Parse a packet containing the "save" command and
        return it as a human readable string.
        """
        return "SAVE"

    # @classmethod
    def _parse_cmd_set_speed(self, args):
        """ Parse a packet containing the "set speed" command and
        return it as a human readable string.
        """
        pkt = args["pkt"]
        return "SET_SPEED: {}".format(hex((pkt[2] << 8) + pkt[3]))

    # @classmethod
    def _parse_cmd_unknown(self, args):
        """ Return a string reporting an unknown command packet.
        """
        pkt = args["pkt"]
        return "UNKNOWN COMMAND : {} IN PACKET {}".format(pkt[1], pkt)

    def pkt_to_string(self, pkt_bytes, controller):
        """ Return a human readable string representation of a command packet.
        """
        if (len(pkt_bytes) != self.PACKET_LENGTH):
            return "BAD PACKET: {}".format(pkt_bytes)
        else:
            cmd = pkt_bytes[1]
            args = {"pkt": pkt_bytes, "controller": controller}
            if (cmd in list(self.command_parsers.keys())):
                return self.command_parsers[cmd](args)
            else:
                return self._parse_cmd_unknown(args)

    # @classmethod
    def make_cmd_set_morph_colour(self, block, zone, colour1, colour2):
        """ Return a command packet for the "set morph colour" command with the
        given parameters.
        """
        pkt = [0x02, self.CMD_SET_MORPH_COLOUR, 0, 0, 0, 0, 0, 0, 0]
        pkt[2] = block & 0xff
        pkt[3:6] = [(zone&0xff0000) >> 16, (zone&0xff00) >> 8, zone & 0xff]
        pkt[6:9] = self._pack_colour_pair(colour1, colour2)
        return pkt

    # @classmethod
    def make_cmd_set_blink_colour(self, block, zone, colour):
        """ Return a command packet for the "set blink colour" command with the
        given parameters.
        """
        pkt = [0x02, self.CMD_SET_BLINK_COLOUR, 0, 0, 0, 0, 0, 0, 0]
        pkt[2] = block & 0xff
        pkt[3:6] = [(zone&0xff0000) >> 16, (zone&0xff00) >> 8, zone & 0xff]
        pkt[6:8] = self._pack_colour(colour)
        return pkt

    # @classmethod
    def make_cmd_set_colour(self, block, zone, colour):
        """ Return a command packet for the "set colour" command with the
        given parameters.
        """
        pkt = [0x02, self.CMD_SET_COLOUR, 0, 0, 0, 0, 0, 0, 0]
        pkt[2] = block & 0xff
        pkt[3:6] = [(zone&0xff0000) >> 16, (zone&0xff00) >> 8, zone & 0xff]
        pkt[6:8] = self._pack_colour(colour)
        return pkt

    # @classmethod
    def make_cmd_loop_block_end(self):
        """ Return a command packet for the "loop block end" command with the
        given parameters.
        """
        pkt = [0x02, self.CMD_LOOP_BLOCK_END, 0, 0, 0, 0, 0, 0, 0]
        return pkt

    # @classmethod
    def make_cmd_transmit_execute(self):
        """ Return a command packet for the "transmit execute" command with the
        given parameters.
        """
        pkt = [0x02, self.CMD_TRANSMIT_EXECUTE, 0, 0, 0, 0, 0, 0, 0]
        return pkt

    # @classmethod
    def make_cmd_get_status(self):
        """ Return a command packet for the "get status" command with the
        given parameters.
        """
        pkt = [0x02, self.CMD_GET_STATUS, 0, 0, 0, 0, 0, 0, 0]
        return pkt

    # @classmethod
    def make_cmd_reset(self, reset_type):
        """ Return a command packet for the "reset" command with the
        given parameters.
        """
        pkt = [0x02, self.CMD_RESET, 0, 0, 0, 0, 0, 0, 0]
        pkt[2] = reset_type & 0xff
        return pkt

    # @classmethod
    def make_cmd_save_next(self, state):
        """ Return a command packet for the "save next" command with the
        given parameters.
        """
        pkt = [0x02, self.CMD_SAVE_NEXT, 0, 0, 0, 0, 0, 0, 0]
        pkt[2] = state & 0xff
        return pkt

    # @classmethod
    def make_cmd_save(self):
        """ Return a command packet for the "save" command with the
        given parameters.
        """
        pkt = [0x02, self.CMD_SAVE, 0, 0, 0, 0, 0, 0, 0]
        return pkt

    # @classmethod
    def make_cmd_set_speed(self, speed):
        """ Return a command packet for the "set speed" command with the
        given parameters.
        """
        pkt = [0x02, self.CMD_SET_SPEED, 0, 0, 0, 0, 0, 0, 0]
        pkt[2:4] = [(speed&0xff00) >> 8, speed & 0xff]
        return pkt
