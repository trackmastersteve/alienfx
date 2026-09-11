#
# colour_palette.py
#
# Copyright (C) 2013-2014 Ashwin Menon <ashwin.menon@gmail.com>
# Copyright (C) 2015-2026 Track Master Steve <trackmastersteve@gmail.com>
#
# Alienfx is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# Alienfx is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with alienfx.    If not, write to:
#       The Free Software Foundation, Inc.,
#       51 Franklin Street, Fifth Floor
#       Boston, MA  02110-1301, USA.
#

"""GTK4 colour palette widgets."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, Gtk


class ColourPaletteSquare(Gtk.Button):
    """A clickable colour swatch."""

    def __init__(self, rgba, max_colour_val):
        super().__init__()
        self.max_colour_val = max_colour_val
        self.colour = (rgba.red, rgba.green, rgba.blue)
        self.set_size_request(32, 28)
        for margin in ("start", "end", "top", "bottom"):
            getattr(self, f"set_margin_{margin}")(1)
        provider = Gtk.CssProvider()
        provider.load_from_data(
            (f"button {{ background: {rgba.to_string()}; min-width: 30px; min-height: 26px; }}").encode()
        )
        self.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def get_colour(self):
        return [int(value * self.max_colour_val) for value in self.colour]


class ColourPalette(Gtk.Grid):
    """A grid of clickable colour swatches."""

    def __init__(self, colours, max_colour_val, num_rows, num_cols, horizontal, selected_handler):
        super().__init__(column_spacing=1, row_spacing=1)
        self.swatches = []
        for index, colour in enumerate(colours):
            rgba = Gdk.RGBA()
            rgba.parse(colour)
            square = ColourPaletteSquare(rgba, max_colour_val)
            square.connect("clicked", selected_handler)
            row, col = divmod(index, num_cols) if horizontal else divmod(index, num_rows)[::-1]
            self.attach(square, col, row, 1, 1)
            self.swatches.append(square)

    def set_sensitive(self, sensitive):
        super().set_sensitive(sensitive)
        for swatch in self.swatches:
            swatch.set_sensitive(sensitive)
