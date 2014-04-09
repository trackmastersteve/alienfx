#
# themefile.py
#
# Copyright (C) 2013-2014 Ashwin Menon <ashwin.menon@gmail.com>
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

""" Classes for handling AlienFX theme files.

This module only deals with the mechanisms of loading and saving theme files
to disk.

This module provides the following classes:
AlienFXThemeFile: theme file abstraction
"""

import json
import logging
import os
import os.path

class AlienFXThemeFile:
    
    """ Provides facilities to read and write AlienFX theme files. The theme
    files are stored in JSON format in $XDG_CONFIG_HOME/alienfx. 
    If XDG_CONFIG_HOME is not set, then ~/.config/alienfx is used. This
    directory is created if it does not exist.
    
    The theme is stored in the "theme" public member as a dict.
    """
    
    # Theme file keywords
    KW_ACTION_TYPE_FIXED = "fixed"
    KW_ACTION_TYPE_BLINK = "blink"
    KW_ACTION_TYPE_MORPH = "morph"
    KW_SPEED = "speed"
    KW_STATE_BOOT = "boot"
    KW_STATE_AC_SLEEP = "ac-sleep"
    KW_STATE_AC_CHARGED = "ac-charged"
    KW_STATE_AC_CHARGING = "ac-charging"
    KW_STATE_BATT_SLEEP = "battery-sleep"
    KW_STATE_BATT_ON = "battery-on"
    KW_STATE_BATT_CRITICAL = "battery-critical"
    KW_ZONES = "zones"
    KW_LOOP = "loop"
    KW_ACTION_TYPE = "type"
    KW_ACTION_COLOURS = "colours"
    
    def __init__(self, controller):
        try:
            if not "XDG_CONFIG_HOME" in os.environ:
                self._theme_dir = os.path.expanduser("~/.config/alienfx")
            else:
                self._theme_dir = os.path.join(
                    os.environ("XDG_CONFIG_HOME"), "alienfx")
            if not os.path.exists(self._theme_dir):
                os.makedirs(self._theme_dir)
        except Exception as exc:
            logging.error(exc)
        self.theme = {}
        self.theme_name = ""
        self.controller = controller
        
    def get_themes(self):
        """ Return a list of all theme file names (minus the filename extension)
        in the themes directory. """
        if not os.path.exists(self._theme_dir):
            os.mkdir(self._theme_dir)
            return []
        theme_dir_files = os.listdir(self._theme_dir)
        files_and_exts = [os.path.splitext(x) for x in theme_dir_files]
        theme_names = []
        for file_ext in files_and_exts:
            if file_ext[1] == ".json":
                theme_names.append(file_ext[0])
        theme_names = sorted(theme_names)
        return theme_names
        
    def set_default_theme(self):
        """ Sets the theme contents to a default value."""
        theme = {}
        self.theme_name = ""
        controller = self.controller
        self.set_speed(controller.DEFAULT_SPEED)
        # Non-power actions
        for zone in controller.zone_map:
            if not zone in controller.power_zones:
                default_action = self.make_zone_action(
                    self.KW_ACTION_TYPE_FIXED, [[0, 0, 15]])
                self.set_zone_actions(
                    controller.STATE_BOOT, [zone], [default_action])
        non_power_zones = [x for x in controller.zone_map if not x in controller.power_zones]
        # AC Charged actions
        actions = []
        actions.append(self.make_zone_action(
            self.KW_ACTION_TYPE_FIXED, [[0, 0, 15]]))
        self.set_zone_actions(
            controller.STATE_AC_CHARGED, controller.power_zones, actions)
        # AC Sleep actions
        actions = []
        actions.append(self.make_zone_action(
            self.KW_ACTION_TYPE_MORPH, [[0, 0, 15], [0, 0, 0]]))
        actions.append(self.make_zone_action(
            self.KW_ACTION_TYPE_MORPH, [[0, 0, 0], [0, 0, 15]]))
        self.set_zone_actions(
            controller.STATE_AC_SLEEP, controller.power_zones, actions)
        actions = []
        actions.append(self.make_zone_action(
            self.KW_ACTION_TYPE_FIXED, [[0, 0, 0]]))
        self.set_zone_actions(
            controller.STATE_AC_SLEEP, non_power_zones, actions)
        # AC Charging actions
        actions = []
        actions.append(self.make_zone_action(
            self.KW_ACTION_TYPE_MORPH, [[0, 0, 15], [15, 9, 0]]))
        actions.append(self.make_zone_action(
            self.KW_ACTION_TYPE_MORPH, [[15, 9, 0], [0, 0, 15]]))
        self.set_zone_actions(
            controller.STATE_AC_CHARGING, controller.power_zones, actions)
        # Battery Sleep actions
        actions = []
        actions.append(self.make_zone_action(
            self.KW_ACTION_TYPE_MORPH, [[15, 9, 0], [0, 0, 0]]))
        actions.append(self.make_zone_action(
            self.KW_ACTION_TYPE_MORPH, [[0, 0, 0], [15, 9, 0]]))
        self.set_zone_actions(
            controller.STATE_BATTERY_SLEEP, controller.power_zones, actions)
        actions = []
        actions.append(self.make_zone_action(
            self.KW_ACTION_TYPE_FIXED, [[0, 0, 0]]))
        self.set_zone_actions(
            controller.STATE_BATTERY_SLEEP, non_power_zones, actions)
        # Battery On actions
        actions = []
        actions.append(self.make_zone_action(
            self.KW_ACTION_TYPE_FIXED, [[15, 9, 0]]))
        self.set_zone_actions(
            controller.STATE_BATTERY_ON, controller.power_zones, actions)
        # Battery Critical actions
        actions = []
        actions.append(self.make_zone_action(
            self.KW_ACTION_TYPE_BLINK, [[15, 9, 0]]))
        self.set_zone_actions(
            controller.STATE_BATTERY_CRITICAL, controller.power_zones, actions)
        
    def set_speed(self, speed):
        """ Set the speed. """
        self.theme[self.KW_SPEED] = speed
        
    def get_speed(self):
        """ Return the speed. """
        return self.theme.get(self.KW_SPEED, self.controller.DEFAULT_SPEED)
        
    def get_state_items(self, state_name):
        """ Return the state items for the given state name. """
        if not state_name in self.theme:
            return []
        return self.theme[state_name]
        
    def get_zone_names(self, state_item):
        """ Given a state item, return the zone names it contains. """
        if self.KW_ZONES not in state_item:
            logging.warning("No zones found in state-item")
            return []
        return state_item[self.KW_ZONES]
        
    def set_zone_actions(self, state, zones, actions):
        """ Set the actions for the given zones, in the given state. """
        state_item = {}
        state_item[self.KW_ZONES] = zones
        state_item[self.KW_LOOP] = actions
        if not state in self.theme:
            self.theme[state] = []
        self.theme[state].append(state_item)
       
    def get_loop_items(self, state_item):
        """ Given a state item, return the loop items it contains. """
        if self.KW_LOOP not in state_item:
            logging.warning("No loop found in state-item")
            return []
        return state_item[self.KW_LOOP]
        
    def get_zone_actions(self, state, zone):
        """ From the theme file, return an array of actions for the given 
        state and zone. 
        """
        if self.theme is None:
            return []
        if state not in self.theme:
            return []
        for item in self.theme[state]:
            if self.KW_ZONES not in item:
                continue
            if zone not in item[self.KW_ZONES]:
                continue
            if self.KW_LOOP not in item:
                continue
            return item[self.KW_LOOP]
        return []
        
    @classmethod
    def make_zone_action(cls, type, colours):
        """ Create a zone action item and return it. """
        zone_action = {}
        zone_action[cls.KW_ACTION_TYPE] = type
        zone_action[cls.KW_ACTION_COLOURS] = colours
        return zone_action
        
    def load(self, theme_name):
        """ Load a theme from the given file. """
        if self._theme_dir is None:
            return
        theme_file = theme_name + ".json"
        try:
            with open(os.path.join(self._theme_dir, theme_file)) as tfile:
                self.theme = json.load(tfile)
            self.theme_name = theme_name
        except Exception as exc:
            logging.error(exc)
            self.theme = {}
        
    def save(self, theme_name=None):
        """ Save the current theme to the given file.
        If the file name is not given, then save it to the previously loaded
        theme file. If no such file was loaded previously, then do nothing.
        """
        if self._theme_dir is None:
            return
        if theme_name is None:
            if self.theme_name == "":
                return
        else:
            theme_file = theme_name + ".json"
        try:
            with open(os.path.join(self._theme_dir, theme_file), "w") as tfile:
                json.dump(self.theme, tfile, indent=4, separators=(',', ': '))
            self.theme_name = theme_name
        except Exception as exc:
            logging.error(exc)
    
    @classmethod
    def get_action_type(cls, action):
        """ From the given action, return the type of the action. """
        if cls.KW_ACTION_TYPE not in action:
            return None
        return action[cls.KW_ACTION_TYPE]
        
    @classmethod
    def set_action_type(cls, action, action_type):
        """ Set the action type of the given action. """
        if action_type in [
                cls.KW_ACTION_TYPE_FIXED,
                cls.KW_ACTION_TYPE_BLINK,
                cls.KW_ACTION_TYPE_MORPH]:
            action[cls.KW_ACTION_TYPE] = action_type

    @classmethod
    def get_action_colours(cls, action):
        """ From the given action, return the colour(s) of the action. """
        if cls.KW_ACTION_COLOURS not in action:
            return []
        return action[cls.KW_ACTION_COLOURS]
    
    @classmethod
    def set_action_colours(cls, action, action_colours):
        """ Set the action colours of the given action. """
        action_type = cls.get_action_type(action)
        if action_type is None:
            return
        if action_type in [cls.KW_ACTION_TYPE_FIXED, cls.KW_ACTION_TYPE_BLINK]:
            if len(action_colours) != 1:
                return
            action[cls.KW_ACTION_COLOURS] = action_colours
        if action_type == cls.KW_ACTION_TYPE_MORPH:
            if len(action_colours) != 2:
                return
            action[cls.KW_ACTION_COLOURS] = action_colours
            
