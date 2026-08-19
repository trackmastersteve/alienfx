"""Top-level package exports for alienfx.

Expose a small helper `Alienware` class for direct sysfs access (HDMI/RGB).
"""
from .core.sysfs import Alienware, HDMI, RGBZones, RGBZone, HDMISource, HDMICableState, Zone

__all__ = [
	"Alienware",
	"HDMI",
	"RGBZones",
	"RGBZone",
	"HDMISource",
	"HDMICableState",
	"Zone",
]
