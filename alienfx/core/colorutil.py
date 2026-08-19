#
# colorutil.py
#
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
# along with alienfx. If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#

""" Color utility functions for RGB parsing and validation.

This module provides common color utilities used by both console and GUI interfaces.
"""


def parse_rgb_string(input_str):
    """Parse an RGB color string into a tuple of (red, green, blue) values.
    
    Supports:
    - Named colors: 'black', 'white', 'red', 'yellow', 'green', 'cyan', 'blue', 'magenta'
    - RGB triplets: '255 128 0' or '15 8 0' (depending on system)
    - Default fallback: (0, 0, 15) - blue
    
    Args:
        input_str (str): Color string to parse (e.g., 'red', '15 0 0')
        
    Returns:
        tuple: (r, g, b) values as integers, or None if invalid
        
    Examples:
        >>> parse_rgb_string('red')
        (15, 0, 0)
        >>> parse_rgb_string('15 8 0')
        (15, 8, 0)
        >>> parse_rgb_string('invalid')
        (0, 0, 15)
    """
    if input_str is None:
        return None
    
    s = input_str.lower().strip()
    
    # Named colors mapping (4-bit color values: 0-15)
    named_colors = {
        'black': (0, 0, 0),
        'white': (15, 15, 15),
        'red': (15, 0, 0),
        'yellow': (15, 15, 0),
        'green': (0, 15, 0),
        'cyan': (0, 15, 15),
        'blue': (0, 0, 15),
        'magenta': (15, 0, 15),
    }
    
    if s in named_colors:
        return named_colors[s]
    
    # Try parsing as RGB triplet
    try:
        parts = [int(x) for x in s.split()]
        if len(parts) == 3:
            # Validate range (support both 0-15 and 0-255)
            for val in parts:
                if val < 0 or val > 255:
                    break
            else:
                return (parts[0], parts[1], parts[2])
    except (ValueError, AttributeError):
        pass
    
    # Default fallback to blue
    return (0, 0, 15)


def validate_rgb_values(r, g, b, max_val=15):
    """Validate RGB values are within acceptable range.
    
    Args:
        r, g, b (int): Red, green, blue values
        max_val (int): Maximum allowed value (default 15 for 4-bit, 255 for 8-bit)
        
    Returns:
        bool: True if all values are valid (0 <= value <= max_val)
    """
    return all(0 <= v <= max_val for v in [r, g, b])


def rgb_to_hex(r, g, b):
    """Convert RGB values to hex color string.
    
    Args:
        r, g, b (int): Red, green, blue values (0-15)
        
    Returns:
        str: Hex color string (e.g., '#FF0000')
    """
    # Scale 4-bit values (0-15) to 8-bit (0-255)
    r_scaled = int((r / 15.0) * 255) if r <= 15 else r
    g_scaled = int((g / 15.0) * 255) if g <= 15 else g
    b_scaled = int((b / 15.0) * 255) if b <= 15 else b
    
    return "#{:02X}{:02X}{:02X}".format(r_scaled, g_scaled, b_scaled)


def hex_to_rgb(hex_str, scale_to_4bit=True):
    """Convert hex color string to RGB values.
    
    Args:
        hex_str (str): Hex color string (e.g., '#FF0000')
        scale_to_4bit (bool): If True, scale to 4-bit (0-15), else 8-bit (0-255)
        
    Returns:
        tuple: (r, g, b) values
    """
    hex_str = hex_str.lstrip('#')
    
    if len(hex_str) != 6:
        return (0, 0, 15)  # Default blue
    
    try:
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        
        if scale_to_4bit:
            # Scale 8-bit values (0-255) to 4-bit (0-15)
            r = int((r / 255.0) * 15)
            g = int((g / 255.0) * 15)
            b = int((b / 255.0) * 15)
        
        return (r, g, b)
    except ValueError:
        return (0, 0, 15)  # Default blue
