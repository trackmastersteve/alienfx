#
# themefile.py
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

""" Classes for handling AlienFX theme files.

This module only deals with the mechanisms of loading and saving theme files
to disk.

This module provides the following classes:
AlienFXThemeFile: theme file abstraction
"""

from builtins import object
import json
import logging
import os
import os.path

import pkg_resources

class AlienFXThemeFile(object):
    
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
    
    # The name of the last applied theme file
    LAST_THEME_FILE = ".last_theme.json"
    
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
        
    def delete_theme_from_disk(self):
        """ Delete the currently loaded theme file from disk, and set contents
        of this instance to the default theme. Return True on success, False
        otherwise."""
        if ((self.theme_name == "") or
                (self.theme_name == os.path.splitext(self.LAST_THEME_FILE)[0])):
            return
                
        theme_file_path = os.path.join(self._theme_dir, 
            self.theme_name +  ".json")
        try:
            if os.path.exists(theme_file_path):
                os.remove(theme_file_path)
                self.set_default_theme()
                return True
        except IOError as exc:
            logging.error(exc)
        return False
        
    def get_themes(self):
        """ Return a list of all theme file names (minus the filename extension)
        in the themes directory. """
        theme_dir_files = os.listdir(self._theme_dir)
        files_and_exts = [os.path.splitext(x) for x in theme_dir_files]
        theme_names = []
        for file_ext in files_and_exts:
            if file_ext[1] == ".json":
                if file_ext[0] != os.path.splitext(self.LAST_THEME_FILE)[0]:
                    theme_names.append(file_ext[0])
        theme_names = sorted(theme_names)
        return theme_names

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
        
    def applied(self):
        """ Notify the theme file that it has been applied on the computer.
        This will make it save itself to self.LAST_THEME_FILE"""
        last_theme_file = os.path.join(self._theme_dir, self.LAST_THEME_FILE)
        self._save_to_file(last_theme_file)
        
    def load_last_theme(self):
        """ Loads the last theme applied and return True. If no theme was 
        applied previously, then load the default theme and return False."""
        last_theme_file = os.path.join(self._theme_dir, self.LAST_THEME_FILE)
        if os.path.exists(last_theme_file):
            self._load_from_file(last_theme_file)
            return True
        else:
            self.set_default_theme()
            return False
            
    def set_default_theme(self):
        """ Sets the theme contents to a default value."""
        default_themefile = pkg_resources.resource_filename(
            "alienfx", "data/themes/default.json")
        self._load_from_file(default_themefile)
        self.theme_name = ""
        
    def _load_from_file(self, theme_file_path):
        """ Load a theme from a file."""
        try:
            with open(theme_file_path) as tfile:
                self.theme = json.load(tfile)
            theme_name = os.path.splitext(
                os.path.basename(theme_file_path))[0]
            if theme_name != os.path.splitext(self.LAST_THEME_FILE)[0]:
                self.theme_name = theme_name
            else:
                self.theme_name = ""
        except Exception as exc:
            logging.error(exc)
            self.theme = {}
            self.theme_name = ""
        
    def _save_to_file(self, theme_file_path):
        """ Save theme contents to a file."""
        try:
            with open(theme_file_path, "w") as tfile:
                json.dump(self.theme, tfile, indent=4, separators=(',', ': '))
            theme_name = os.path.splitext(
                os.path.basename(theme_file_path))[0]
            if theme_name != os.path.splitext(self.LAST_THEME_FILE)[0]:
                self.theme_name = theme_name
        except Exception as exc:
            logging.error(exc)
            
    def load(self, theme_name):
        """ Load a theme given its name. """
        theme_file = theme_name + ".json"
        theme_file_path = os.path.join(self._theme_dir, theme_file)
        self._load_from_file(theme_file_path)
        
    def save(self, theme_name=None):
        """ Save the current theme with the given name.
        If the name is not given, then save it to the previously loaded
        theme file. If no such file was loaded previously, then do nothing.
        """
        if theme_name is None:
            if self.theme_name == "":
                return
        else:
            theme_file = theme_name + ".json"
        theme_file_path = os.path.join(self._theme_dir, theme_file)
        self._save_to_file(theme_file_path)
    
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
