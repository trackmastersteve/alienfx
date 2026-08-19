# ASM100 (Alienware Alpha) GTK UI Integration

## Summary of Changes

This document outlines the integration of the Alienware Alpha ASM100 ACPI/WMI controller into the GTK UI system.

## ASM100 Controller Details

The ASM100 (Alienware Alpha) is a desktop system with ACPI/WMI-based lighting control:

- **Device Type**: Desktop (Chassis)
- **Control Interface**: alienware-wmi kernel module (ACPI/WMI)
- **LED Zones**: 2
  - LED 0: Alienhead (Group01)
  - LED 1: Side Left (Group02)
- **Power States**: AC-only (no battery states)
  - Boot (visualization type 1)
  - AC Sleep (visualization type 2)
  - AC Charged (visualization type 5)
  - AC On (visualization type 8)
- **Actions per Zone**: 1

## GTK UI Compatibility

The GTK UI now properly supports both:
- **Laptop controllers** (with battery states): M-series, R-series, etc.
- **Desktop controllers** (AC-only): ASM100, Aurora, Area51, etc.

The `load_theme()` method dynamically filters power states based on what the controller supports, making it agnostic to controller type.

## Installation & Usage

### Install Dependencies
```bash
pip install -r requirements.txt
```
### Install
```bash
python setup.py install
python setup.py install_data
```

### Launch
```bash
sudo alienfx

# or sudo python /usr/local/bin/alienfx-gtk

```

### Uninstall
```bash
python remove.py
```
The GTK UI will automatically detect your controller (USB or ACPI/WMI) and load appropriate zones and states.

## Color Utilities API

The new `colorutil` module provides:

- `parse_rgb_string(input_str)` - Parse named colors or RGB triplets
- `validate_rgb_values(r, g, b, max_val)` - Validate RGB ranges
- `rgb_to_hex(r, g, b)` - Convert to hex color strings
- `hex_to_rgb(hex_str, scale_to_4bit)` - Convert from hex

### Examples
```python
from alienfx.core.colorutil import parse_rgb_string

# Named colors
parse_rgb_string('red')        # (15, 0, 0)
parse_rgb_string('cyan')       # (0, 15, 15)

# RGB triplets
parse_rgb_string('15 8 0')     # (15, 8, 0)

# Fallback to blue
parse_rgb_string('invalid')    # (0, 0, 15)
```

## Files Modified

1. `alienfx/ui/gtkui/gtkui.py` - Dynamic power state filtering
2. `alienfx/ui/console/main.py` - Use shared colorutil
3. `alienfx/core/colorutil.py` - New shared utility module
4. `requirements.txt` - Added PyGObject and pycairo

## Testing

Verify installation:
```bash
python3 -c "from alienfx.core.controller_asm100 import AlienFXControllerASM100; asm100 = AlienFXControllerASM100(); print(asm100.name)"
```

Expected output:
```
Alienware Alpha ASM100
```

## Issues Fixed

### 1. **Hardcoded Power States in GTK UI** 
   - **Problem**: The `load_theme()` method in `gtkui.py` was hardcoding all power states including battery states (STATE_BATTERY_SLEEP, STATE_BATTERY_ON, STATE_BATTERY_CRITICAL)
   - **Impact**: The ASM100 desktop controller only supports AC states (no battery), causing incompatibility with the GUI
   - **Solution**: Modified `load_theme()` to dynamically read available states from the controller's `state_map`
   - **File**: `alienfx/ui/gtkui/gtkui.py`

### 2. **Missing Color Utility Module**
   - **Problem**: RGB color parsing code was duplicated in `console/main.py` with inconsistent implementations
   - **Impact**: No centralized, tested color parsing available for UI modules
   - **Solution**: Created `alienfx/core/colorutil.py` with comprehensive color utilities
   - **File**: `alienfx/core/colorutil.py` (new)

### 3. **Console UI Color Parsing**
   - **Problem**: Local `parse_rgb_string()` function in `console/main.py` was redundant
   - **Impact**: Code duplication, maintenance burden
   - **Solution**: Updated to import from `colorutil`
   - **File**: `alienfx/ui/console/main.py`

### 4. **Missing Dependencies**
   - **Problem**: PyGObject and pycairo not listed in requirements
   - **Impact**: GTK UI would fail without explicit installation
   - **Solution**: Added to `requirements.txt`
   - **File**: `requirements.txt`
