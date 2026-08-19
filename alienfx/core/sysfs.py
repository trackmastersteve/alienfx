"""Sysfs access helpers for AlienFX (HDMI and RGB zones).

This module provides a small API to read/write the same sysfs files
that the rust `alienware-wmi` library uses. It mirrors the behaviour
needed by the CLI in the attachments.
"""
from dataclasses import dataclass
from enum import Enum
import os
import re
from pathlib import Path
from typing import Dict, Optional, Tuple


class HDMISource(Enum):
    Cable = "cable"
    Gpu = "gpu"
    Unknown = "unknown"

    def __str__(self) -> str:
        return self.value


class HDMICableState(Enum):
    Connected = "connected"
    Unconnected = "unconnected"
    Unknown = "unknown"

    def __str__(self) -> str:
        return self.value


class Zone(Enum):
    Head = 0
    Left = 1
    Right = 2

    def __str__(self) -> str:
        if self == Zone.Head:
            return "head"
        if self == Zone.Left:
            return "left"
        return "right"


@dataclass
class HDMI:
    source: HDMISource
    cable_state: HDMICableState
    exists: bool = False


@dataclass
class RGBZone:
    zone: Zone
    red: int
    green: int
    blue: int


@dataclass
class RGBZones:
    zones: Dict[Zone, RGBZone]
    exists: bool = False


class Alienware:
    """Simple accessor for the alienware-wmi sysfs files.

    Default platform path is `/sys/devices/platform/alienware-wmi`, but a
    different path may be provided for testing.
    """

    def __init__(self, platform: Optional[str] = None):
        self.platform = platform or "/sys/devices/platform/alienware-wmi"

    def is_alienware(self) -> bool:
        return Path(self.platform).exists()

    def _sys_path(self, *parts: str) -> Path:
        p = Path(self.platform)
        for part in parts:
            p = p / part
        return p

    def parse_sys_file(self, file_name: str) -> Optional[str]:
        """Parse a sysfs single-value file that uses a '[value]' marker.

        Returns the captured value or None if missing.
        """
        re_bracket = re.compile(r"\[([^)]+)\]")
        path = self._sys_path(file_name)
        with open(path, "r", encoding="utf-8") as fh:
            contents = fh.read()
        m = re_bracket.search(contents)
        return m.group(1) if m else None

    def parse_sys_rgb_file(self, file_name: str) -> Tuple[int, int, int]:
        """Parse an rgb file containing 'red: X, green: Y, blue: Z'."""
        re_rgb = re.compile(r"red: (\d+), green: (\d+), blue: (\d+)")
        path = self._sys_path(file_name)
        with open(path, "r", encoding="utf-8") as fh:
            contents = fh.read()
        m = re_rgb.search(contents)
        if m and len(m.groups()) == 3:
            return int(m.group(1)), int(m.group(2)), int(m.group(3))
        return 0, 0, 0

    def get_hdmi(self) -> HDMI:
        source = HDMISource.Unknown
        cable_state = HDMICableState.Unknown
        exists = False
        if self.is_alienware():
            exists = True
            hdmi_dir = self._sys_path("hdmi")
            if hdmi_dir.exists():
                src = self.parse_sys_file("hdmi/source")
                if src == "cable":
                    source = HDMISource.Cable
                elif src == "gpu":
                    source = HDMISource.Gpu
                else:
                    source = HDMISource.Unknown

                cable = self.parse_sys_file("hdmi/cable")
                if cable == "connected":
                    cable_state = HDMICableState.Connected
                elif cable == "unconnected":
                    cable_state = HDMICableState.Unconnected
                else:
                    cable_state = HDMICableState.Unknown

        return HDMI(source=source, cable_state=cable_state, exists=exists)

    def set_hdmi_source(self, source: HDMISource) -> None:
        path = self._sys_path("hdmi/source")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(str(source))

    def get_rgb_zones(self) -> RGBZones:
        zones: Dict[Zone, RGBZone] = {}
        exists = False
        if self.is_alienware():
            exists = True
            rgb_root = self._sys_path("rgb_zones")
            if rgb_root.exists():
                # zone00 -> head, zone01 -> left
                mapping = {"zone00": Zone.Head, "zone01": Zone.Left}
                for fname, z in mapping.items():
                    fpath = rgb_root / fname
                    if fpath.exists():
                        r, g, b = self.parse_sys_rgb_file(str(Path("rgb_zones") / fname))
                        zones[z] = RGBZone(zone=z, red=r, green=g, blue=b)
        return RGBZones(zones=zones, exists=exists)

    def set_rgb_zone(self, zone: Zone, red: int, green: int, blue: int) -> None:
        idx = {Zone.Head: "zone00", Zone.Left: "zone01"}[zone]
        path = self._sys_path("rgb_zones", idx)
        # write as hex pair each (two hex digits per component) like the rust code
        value = f"{red:02x}{green:02x}{blue:02x}"
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(value)
