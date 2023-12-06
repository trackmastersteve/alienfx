#
# controller_17r4.py
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

""" Specialization of the AlienFxController class for the M17xR4 controller.

This module provides the following classes:
AlienFXControllerM17R4 : 17R4 controller
"""

import alienfx.core.controller as alienfx_controller

class AlienFXControllerM17xR4(alienfx_controller.AlienFXController):
    
    """ Specialization of the AlienFxController class for the M17xR4 controller.
    """
    
    # Speed capabilities. The higher the number, the slower the speed of 
    # blink/morph actions. The min speed is selected by trial and error as 
    # the lowest value that will not result in strange blink/morph behaviour.
    DEFAULT_SPEED = 75
    MIN_SPEED = 1

    # Zone codes
    LEFT_KEYBOARD = 0x0008  # Code OK
    MIDDLE_LEFT_KEYBOARD = 0x0004  # Code OK
    MIDDLE_RIGHT_KEYBOARD = 0x0002  # Code OK
    RIGHT_KEYBOARD = 0x0001  # Code OK
    # 0x000F - Keyboard: all fields (0x1+0x2+0x4+0x8=0xF). You may have look at reverse-engineering-knowledgebase.md

    RIGHT_SPEAKER = 0x0800  # Code OK, Bottom  - Right light bar
    LEFT_SPEAKER = 0x0400  # Code OK, Bottom  - Left light bar
    LEFT_DISPLAY = 0x1000  # Code OK, Display - Left light bar
    RIGHT_DISPLAY = 0x2000  # Code OK, Display - Right light bar

    ALIEN_HEAD = 0x0020  # Code OK
    LOGO = 0x0040  # Code OK. Alienware-logo below screen.
    # 0x0060 seems to bee alien head and logo (0x20+0x40=0x60). You may have look at reverse-engineering-knowledgebase.md

    # Touchpad:
    # Seems OK. You may need to set touchpad-lightning to always on in BIOS for this to work,
    # as the on-touch-event seems to be not recognized correctly
    TOUCH_PAD = 0x0080  # Code OK. Have a look at your BIOS settings.
    MEDIA_BAR = 0x4000  # Seems OK. If Media_Bar should be Macro-Key-Bar
    POWER_BUTTON = 0x0100  # Seems OK. Caution: S1 (Boot) conflicts with settings for other states...
    # HDD_LEDS = ???  # Inactive: Device has no hdd indicator

    # Reset codes
    RESET_ALL_LIGHTS_OFF = 3
    RESET_ALL_LIGHTS_ON = 4
    
    # State codes
    BOOT = 1  # Seems some zone can only be defined by Boot-State and have no effect on higher states
    AC_SLEEP = 2
    AC_CHARGED = 5
    AC_CHARGING = 6
    BATTERY_SLEEP = 7
    BATTERY_ON = 8
    BATTERY_CRITICAL = 9

    #Controller Type
    # Defines the controllertype:
    # 1 = old pre Alienware 17R4 (4 bits per color)
    # 2 = AW17R4 and probably others, which are using 8 bits per color
    MYCONTROLLERREV = 2

    
    def __init__(self):
        # For new controller-defintions controller-revision should be provided as it defaults to 1!
        # Wrong revision might result in packet errors 32 and 75 (Overflow and Pipeoverflow)
        alienfx_controller.AlienFXController.__init__(self, self.MYCONTROLLERREV)

        self.name = "Alienware 17R4"
        
        # USB VID and PID
        self.vendor_id = 0x187c
        self.product_id = 0x0530

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
            self.ZONE_LEFT_DISPLAY: self.LEFT_DISPLAY,
            self.ZONE_RIGHT_DISPLAY: self.RIGHT_DISPLAY
            # self.ZONE_HDD_LEDS: self.HDD_LEDS,  # Not used, as de AW17R4 does not have an HDD indicator
        }
        
        # zones that have special behaviour in the different power states
        self.power_zones = [
            self.ZONE_POWER_BUTTON  # ,
            # self.ZONE_HDD_LEDS
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
