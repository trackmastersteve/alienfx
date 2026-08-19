# ACPI/WMI Controller Support

## Overview

Some Alienware systems (like the Alienware Alpha ASM100) use ACPI/WMI interface for lighting control instead of USB. This requires the `alienware-wmi` kernel module. 

## Supported Systems

- **Alienware Alpha ASM100** - Compact desktop with minimal lighting zones (Alienhead, Side Left)

## Requirements

### 1. Load the Kernel Module

```bash
sudo modprobe alienware-wmi
```

### 2. Verify the Module is Loaded

```bash
ls /sys/devices/platform/alienware-wmi
```

You should see sysfs attributes for controlling the lighting. 

### 3. Make the Module Load at Boot (Optional)

Add to `/etc/modules-load.d/alienware. conf`:
```
alienware-wmi
```

## Differences from USB Controllers

1. **No USB VID/PID** - ACPI controllers are identified by the sysfs path
2. **Different Communication** - Uses sysfs file I/O instead of USB control transfers
3. **Limited Status** - Some status checking features may not be available
4. **Requires Root/Permissions** - You may need appropriate permissions to write to sysfs

## Troubleshooting

### Module Not Found
```
ERROR: No AlienFX ACPI/WMI controller found
```

**Solution:**
```bash
# Check if module exists
modinfo alienware-wmi

# Load the module
sudo modprobe alienware-wmi

# Check kernel messages
dmesg | grep alienware
```

### Permission Denied

**Solution:** Run with sudo or add udev rules: 

Create `/etc/udev/rules.d/99-alienware-wmi.rules`:
```
SUBSYSTEM=="platform", DRIVER=="alienware-wmi", RUN+="/bin/chmod 0666 /sys/devices/platform/alienware-wmi/*"
```

Then reload udev:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Implementation Details

The ACPI controller (`AlienFXACPIController`) uses: 
- `AlienFXACPIDriver` for sysfs communication
- Same command packet format as USB controllers
- Default path: `/sys/devices/platform/alienware-wmi`

Subclasses (like `AlienFXControllerASM100`) inherit from `AlienFXACPIController` instead of the standard USB `AlienFXController`.
