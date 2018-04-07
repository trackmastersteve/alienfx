#
# action_renderer.py
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

""" Classes to render the AlienFX theme actions in a Gtk.TreeView. 

This module provides the following classes:
AlienFXActions: encapsulates the theme actions for a lighting zone.
AlienFxActionCellRenderer: Gtk.CellRenderer subclass to render actions in a
Gtk.TreeView.
"""


from past.utils import old_div
import cairo

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from gi.repository import Gtk

from alienfx.core.themefile import AlienFXThemeFile

class AlienFXActions(GObject.GObject):
    
    """ Encapsulates the theme actions for a lighting zone. Instances of this
    class are stored in a Gtk.ListStore that is displayed by the GUI.
    """
    
    def __init__(self):
        GObject.GObject.__init__(self)
        self.actions = []
        
class AlienFXActionCellRenderer(Gtk.CellRenderer):
    
    """ Gtk.CellRenderer subclass to render instances of AlienFxActions in
    a Gtk.TreeView in the GUI.
    """
    
    actions = GObject.property(type=AlienFXActions)
    item_width = 40
    item_height = 25
    item_spacing = 5
    line_width = 1
    cell_padding = 0
    border_normal = (0.5, 0.5, 0.5)
    border_selected_dark = (0, 0, 0, 0.8)
    border_selected_light = (1, 1, 1, 0.8)
    
    def __init__(self, treeview, max_colour_val):
        Gtk.CellRenderer.__init__(self)
        prop = GObject.Value()
        prop.init(GObject.TYPE_INT)
        treeview.style_get_property("horizontal-separator", prop)
        self.cell_padding = old_div(prop.get_int(),2)
        treeview.style_get_property("grid-line-width", prop)
        self.cell_padding += prop.get_int()
        self.selected_action = None
        self.max_colour_val = max_colour_val
        
    def _convert_x_to_action_index(self, x):
        """ Convert the given x coordinate to an action index. """
        return int(old_div((x - self.cell_padding - 1),
            (self.item_width + self.item_spacing + self.line_width)))
        
    def select_action_at_index(self, index):
        """ Select the action at the given index. """
        self.selected_action = index
        
    def select_action_at_x(self, x):
        """ Select the action at the given cell x coordinate. If x is None,
        then select nothing.
        """
        if x is None:
            self.selected_action = None
        else:
            self.selected_action = self._convert_x_to_action_index(x)
        return self.selected_action
        
    @staticmethod
    def _get_intensity(colour):
        """ If the given colour is light, return a number < 0.5; return a number
        > 0.5 if the given colour is dark."""
        (red, green, blue) = colour
        return red*0.30 + green*0.59 + blue*0.11
        
    def do_render(self, cr, widget, background_area, cell_area, flags):
        """ Render the actions. Implementation of Gtk.CellRenderer.render()."""
        
        cr.set_line_width(self.line_width)
         
        # Draw a white background.
        cr.rectangle(
            background_area.x, background_area.y, 
            background_area.width, background_area.height)
        cr.set_source_rgb(1, 1, 1)
        cr.fill()
        
        # Draw the actions.
        actions = self.get_property("actions").actions
        start_x = cell_area.x + self.item_spacing
        start_y = cell_area.y + old_div((cell_area.height - self.item_height),2)
        action_num = 0
        for action in actions:
            action_type = AlienFXThemeFile.get_action_type(action)
            if action_type == AlienFXThemeFile.KW_ACTION_TYPE_FIXED:
                colours = AlienFXThemeFile.get_action_colours(action)
                if len(colours) == 1:
                    colours_normalized = [
                        old_div(float(x),self.max_colour_val) for x in colours[0]]
                    if self._get_intensity(colours_normalized) > 0.5:
                        border_colour = self.border_selected_dark
                    else:
                        border_colour = self.border_selected_light
                    (red, green, blue) = colours_normalized
                    cr.rectangle(
                        start_x, start_y, self.item_width, self.item_height)
                    cr.set_source_rgb(red, green, blue)
                    cr.fill()
            elif action_type == AlienFXThemeFile.KW_ACTION_TYPE_BLINK:
                colours = AlienFXThemeFile.get_action_colours(action)
                if len(colours) == 1:
                    colours_normalized = [
                        old_div(float(x),self.max_colour_val) for x in colours[0]]
                    border_colour = self.border_selected_light
                    (red, green, blue) = colours_normalized
                    cr.rectangle(
                        start_x, start_y, old_div(self.item_width,2), self.item_height)
                    cr.set_source_rgb(red, green, blue)
                    cr.fill()
                    cr.rectangle(
                        start_x+ old_div(self.item_width,2), start_y, 
                        old_div(self.item_width,2), self.item_height)
                    cr.set_source_rgb(0, 0, 0)
                    cr.fill()
            elif action_type == AlienFXThemeFile.KW_ACTION_TYPE_MORPH:
                colours = AlienFXThemeFile.get_action_colours(action)
                if len(colours) == 2:
                    colours_normalized1 = [
                        old_div(float(x),self.max_colour_val) for x in colours[0]]
                    colours_normalized2 = [
                        old_div(float(x),self.max_colour_val) for x in colours[1]]
                    border_colours = [
                        self.border_selected_light, self.border_selected_dark]
                    if (self._get_intensity(colours_normalized1) + 
                            self._get_intensity(colours_normalized2)) > 1:
                        border_colour = self.border_selected_dark
                    else:
                        border_colour = self.border_selected_light
                    (red1, green1, blue1) = colours_normalized1
                    (red2, green2, blue2) = colours_normalized2
                    cr.rectangle(
                        start_x, start_y, self.item_width, self.item_height)
                    gradient = cairo.LinearGradient(
                        start_x, 0, start_x + self.item_width, 0)
                    gradient.add_color_stop_rgb(0, red1, green1, blue1)
                    gradient.add_color_stop_rgb(1, red2, green2, blue2)
                    cr.set_source(gradient)
                    cr.fill()
                    
            # Check if this action is selected.
            selected = False
            if ((self.selected_action is not None) and 
                (action_num == self.selected_action) and
                (flags & Gtk.CellRendererState.SELECTED)):
                    selected = True
                    
            # draw the action border.
            (red, green, blue) = self.border_normal
            cr.rectangle(start_x, start_y, self.item_width, self.item_height)
            cr.set_source_rgb(red, green, blue)
            cr.stroke()
            
            # Draw the selection border.
            if selected:
                cr.set_line_width(2)
                (red, green, blue, alpha) = border_colour
                cr.set_source_rgba(red, green, blue, alpha)
                cr.rectangle(start_x+3, start_y+3, self.item_width-3-3, 
                    self.item_height-3-3)
                cr.stroke()
            start_x += self.item_spacing + self.item_width + self.line_width
            action_num += 1

    def do_get_request_mode(self):
        """ Implementation of Gtk.CellRenderer.get_request_mode()."""
        return Gtk.SizeRequestMode.HEIGHT_FOR_WIDTH
        
    def do_get_preferred_height(self, widget):
        """ Implementation of Gtk.CellRenderer.get_preferred_height()."""
        preferred_height = self.item_height + self.item_spacing
        return (preferred_height, preferred_height)
        
    def do_get_preferred_width(self, widget):
        """ Implementation of Gtk.CellRenderer.get_preferred_width()."""
        actions = self.get_property("actions").actions
        preferred_width = (len(actions)*(self.item_width + self.item_spacing + 
            self.line_width) + self.cell_padding)
        return (preferred_width, preferred_width)
