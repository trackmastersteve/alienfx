#!/usr/bin/env python3
#
# setup.py
#
# Copyright (C) 2013-2014 Ashwin Menon <ashwin.menon@gmail.com>
# Copyright (C) 2015-2024 Track Master Steve <trackmastersteve@gmail.com>
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

try:
    from setuptools import setup, find_packages
except ImportError as exc:
    raise SystemExit(
        "ImportError: Unable to import 'setup' and 'find_packages' from setuptools."
    ) from exc

import os
import os.path
from importlib import resources
from collections.abc import Sequence
import shutil
import gzip

man1 = "docs/man/alienfx.1"
man1_gz = "docs/man/alienfx.1.gz"
# Ensure a gzipped manpage exists so installations provide alienfx.1.gz
try:
    if os.path.exists(man1) and not os.path.exists(man1_gz):
        with open(man1, "rb") as f_in, gzip.open(man1_gz, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
except Exception:
    # If gz creation fails, fall back to installing the uncompressed manpage
    man1_gz = man1

data_files: list[tuple[str, Sequence[str]]] = [
    ("share/applications", ["alienfx/data/share/applications/alienfx.desktop"]),
    ("share/icons/hicolor/scalable/apps", ["alienfx/data/icons/hicolor/scalable/apps/alienfx.svg"]),
    ("share/icons/hicolor/48x48/apps", ["alienfx/data/icons/hicolor/48x48/apps/alienfx.png"]),
    ("share/pixmaps", ["alienfx/data/pixmaps/alienfx.png"]),
    ("share/man/man1", [man1_gz])
]
        
entry_points = {
    "console_scripts": [
        "alienfx = alienfx.ui.console:start",
    ],
    "gui_scripts": [
        "alienfx-gtk = alienfx.ui.gtkui:start"
    ]
}

setup(
    name = "alienfx",
    version = "2.4.4",
    fullname = "AlienFX Configuration Utility",
    description = "AlienFX Configuration Utility",
    author = "Track Master Steve",
    author_email = "trackmastersteve@gmail.com",
    keywords = "alienfx alienware",
    long_description = """AlienFX is a utility that allows you to configure
        the lights of your Alienware computer.""",
    url = "https://github.com/trackmastersteve/alienfx",
    license = "GPLv3",
    
    install_requires = ["pyusb>=1.2.1"],
    data_files = data_files,
    entry_points = entry_points,
    packages = find_packages(),
    package_data = {"alienfx": [
        "ui/gtkui/glade/*.glade", 
        "data/icons/hicolor/scalable/apps/*.svg",
        "data/themes/default.json",
        "data/etc/udev/rules.d/10-alienfx.rules"
    ]}
)

# Copy the udev rules file
udev_file = resources.files("alienfx").joinpath("data/etc/udev/rules.d/10-alienfx.rules")
udev_rules_dir = "/etc/udev/rules.d/"
try:
    if not os.path.exists(udev_rules_dir):
        print("Udev rules directory {} does not exist. Will not copy udev rules file.".format(udev_rules_dir))
    elif not os.access(udev_rules_dir, os.W_OK):
        print("Udev rules directory {} is not writable. Will not copy udev rules file.".format(udev_rules_dir))
    else:
        shutil.copy(str(udev_file), udev_rules_dir)
except IOError:
    print("Unable to copy udev rules file {} to {}".format(udev_file, udev_rules_dir))
