#
# controller_m17xr3.py
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

""" Specialization of the AlienFxController class for the M17xR4 controller.

This module provides the following classes:
AlienFXControllerM17xR4 : M17xR4 controller
"""

import alienfx.core.controller as alienfx_controller

class AlienFXControllerM17xR4(alienfx_controller.AlienFXController):
    
    """ Specialization of the AlienFxController class for the M17xR4 controller.
    """
    
    # Speed capabilities. The higher the number, the slower the speed of 
    # blink/morph actions. The min speed is selected by trial and error as 
    # the lowest value that will not result in strange blink/morph behaviour.
    DEFAULT_SPEED = 200
    MIN_SPEED = 50
    
    # Zone codes
    LEFT_KEYBOARD = 0x0008  # Code OK
    MIDDLE_LEFT_KEYBOARD = 0x0004  # Code OK
    MIDDLE_RIGHT_KEYBOARD = 0x0002  # Code OK
    RIGHT_KEYBOARD = 0x0001  # Code OK
    # Both speakers change together
    RIGHT_SPEAKER = 0x0800  # (bottom right?) wrong
    LEFT_SPEAKER = 0x0400  # Not sure (bottom left?)
    ALIEN_HEAD = 0x0080  # TODO: wrong. causes flashing in bottom right
    LOGO = 0x0200  # TODO: Seems to be wrong
    TOUCH_PAD = 0x0300  # TODO: Seems to be wrong
    MEDIA_BAR = 0x0900  # TODO: seems to be bottom right but also causes power button to flash in that color...
    POWER_BUTTON = 0x0100  # Todo: Seems to be wrong. causes flashing in powerbutton and bottom right...
    HDD_LEDS = 0x4000  # TODO: Device has no hdd indicator

    # Reset codes
    RESET_ALL_LIGHTS_OFF = 3
    RESET_ALL_LIGHTS_ON = 4
    
    # State codes
    BOOT = 1  # Todo: Seems to be wrong. Seems State is 1 when booted and on AC. may be other states are wrong as well
    AC_SLEEP = 2
    AC_CHARGED = 5
    AC_CHARGING = 6
    BATTERY_SLEEP = 7
    BATTERY_ON = 8
    BATTERY_CRITICAL = 9

    #Controller Type
    MYCONTROLLER = "new" #Defines the controllertype: old=pre Alienware 17R4 (4 bits per color) / new=AW17R4 and probably others, which are using 8 bits per color
    
    def __init__(self):
        alienfx_controller.AlienFXController.__init__(self)
        self.name = "Alienware M17xR4"
        
        # USB VID and PID
        self.vendor_id = 0x187c
        self.product_id = 0x0530

        #Switch Controllertype
        if self.MYCONTROLLER == "new":
            self.switch_to_new_controller()
        else:
            self.switch_to_old_controller()

        
        # map the zone names to their codes
        self.zone_map = {
            self.ZONE_LEFT_KEYBOARD: self.LEFT_KEYBOARD,
            self.ZONE_MIDDLE_LEFT_KEYBOARD: self.MIDDLE_LEFT_KEYBOARD,
            self.ZONE_MIDDLE_RIGHT_KEYBOARD: self.MIDDLE_RIGHT_KEYBOARD,
            self.ZONE_RIGHT_KEYBOARD: self.RIGHT_KEYBOARD,
            self.ZONE_RIGHT_SPEAKER: self.RIGHT_SPEAKER,
            self.ZONE_LEFT_SPEAKER: self.LEFT_SPEAKER,
            self.ZONE_ALIEN_HEAD: self.ALIEN_HEAD,
            self.ZONE_LOGO: self.LOGO,
            self.ZONE_TOUCH_PAD: self.TOUCH_PAD,
            self.ZONE_MEDIA_BAR: self.MEDIA_BAR,
            self.ZONE_POWER_BUTTON: self.POWER_BUTTON,
            self.ZONE_HDD_LEDS: self.HDD_LEDS,
        }
        
        # zones that have special behaviour in the different power states
        self.power_zones = [
            self.ZONE_POWER_BUTTON,
            self.ZONE_HDD_LEDS
        ]
        
        # map the reset names to their codes
        self.reset_types = {
            self.RESET_ALL_LIGHTS_OFF: "all-lights-off",
            self.RESET_ALL_LIGHTS_ON: "all-lights-on"
        }
        
        # map the state names to their codes
        self.state_map = {
            self.STATE_BOOT: self.BOOT,
            self.STATE_AC_SLEEP: self.AC_SLEEP,
            self.STATE_AC_CHARGED: self.AC_CHARGED,
            self.STATE_AC_CHARGING: self.AC_CHARGING,
            self.STATE_BATTERY_SLEEP: self.BATTERY_SLEEP,
            self.STATE_BATTERY_ON: self.BATTERY_ON,
            self.STATE_BATTERY_CRITICAL: self.BATTERY_CRITICAL
        }

alienfx_controller.AlienFXController.supported_controllers.append(
    AlienFXControllerM17xR4())
