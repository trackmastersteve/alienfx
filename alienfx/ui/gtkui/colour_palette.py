#
# colour_palette.py
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

""" Classes to display a colour palette to select colours for lighting zones.

Classes provided by this module:
ColourPaletteSquare: A single colour of the palette.
ColourPalette: A colour palette consisting of instances of ColourPaletteSquare.
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
import cairo

class ColourPaletteSquare(Gtk.EventBox):
    
    """ A single colour square belonging to a ColourPalette instance."""
    
    def __init__(self, rgba, width, height, max_colour_val):
        Gtk.EventBox.__init__(self)
        self.max_colour_val = max_colour_val
        self.set_property("margin", 1)
        self.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        
        # Draw the contents.
        self.colour = (rgba.red, rgba.green, rgba.blue)
        (red, green, blue) = self.colour
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
        cr = cairo.Context(surface)
        cr.rectangle(0, 0, width, height)
        cr.set_source_rgb(red, green, blue)
        cr.fill()
        cr.rectangle(0, 0, width, height)
        cr.set_line_width(2)
        cr.set_source_rgb(0x0, 0x0, 0x0)
        cr.stroke()
        pb = Gdk.pixbuf_get_from_surface(surface, 0, 0, width, height)
        self.active_image = Gtk.Image()
        self.active_image.set_from_pixbuf(pb)
        self.add(self.active_image)
        
        # Make the inactive version
        y = 0.2126*red + 0.7152*green + 0.0722*blue
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
        cr = cairo.Context(surface)
        cr.rectangle(0, 0, width, height)
        cr.set_source_rgb(y, y, y)
        cr.fill()
        pb = Gdk.pixbuf_get_from_surface(surface, 0, 0, width, height)
        self.inactive_image = Gtk.Image()
        self.inactive_image.set_from_pixbuf(pb)
        
    def get_colour(self):
        """ Return the colour stored in this instance."""
        return [int(x*self.max_colour_val) for x in self.colour]
        
    def set_active(self, active):
        """ Override Gtk.EventBox.set_active()."""
        if active:
            self.remove(self.inactive_image)
            self.add(self.active_image)
        else:
            self.remove(self.active_image)
            self.add(self.inactive_image)
        self.get_child().show()
            
class ColourPalette(Gtk.Grid):
        
    """ A colour palette consisting of instances of ColourPaletteSquare."""
    
    def __init__(
            self, colours, max_colour_val, num_rows, num_cols, horizontal, 
            selected_handler):
        Gtk.Grid.__init__(self)
        row = 0
        col = 0
        (ret, width, height) = Gtk.icon_size_lookup(Gtk.IconSize.BUTTON)
        rgba = Gdk.RGBA()
        for c in colours:
            rgba.parse(c)
            colour_square = ColourPaletteSquare(
                rgba, width, height, max_colour_val)
            colour_square.connect("button-release-event", selected_handler)
            self.attach(colour_square, col, row, 1, 1)
            if horizontal:
                col += 1
                if col == num_cols:
                    col = 0
                    row += 1
            else:
                row += 1
                if row == num_rows:
                    row = 0
                    col += 1
    
    def set_sensitive(self, sensitive):
        """ Override Gtk.Grid.set_sensitive()."""
        if self.get_parent().get_sensitive() == sensitive:
            return
        self.get_parent().set_sensitive(sensitive)
        for c in self.get_children():
            c.set_active(sensitive)
