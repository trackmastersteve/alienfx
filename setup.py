#!/usr/bin/env python
#
# setup.py
#
# Copyright (C) 2013-2014 Ashwin Menon <ashwin.menon@gmail.com>
# Copyright (C) 2015-2018 Track Master Steve <trackmastersteve@gmail.com>
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
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

import os
import os.path
from pkg_resources import resource_filename
import shutil

data_files = [
    ("share/applications", ["alienfx/data/share/applications/alienfx.desktop"]),
    ("share/icons/hicolor/scalable/apps", ["alienfx/data/icons/hicolor/scalable/apps/alienfx.svg"]),
    ("share/icons/hicolor/48x48/apps", ["alienfx/data/icons/hicolor/48x48/apps/alienfx.png"]),
    ('share/pixmaps', ["alienfx/data/pixmaps/alienfx.png"]),
    ("share/man/man1", ["docs/man/alienfx.1"])
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
    version = "2.3.4",
    fullname = "AlienFX Configuration Utility",
    description = "AlienFX Configuration Utility",
    author = "Track Master Steve",
    author_email = "trackmastersteve@gmail.com",
    keywords = "alienfx alienware",
    long_description = """AlienFX is a utility that allows you to configure
        the lights of your Alienware computer.""",
    url = "https://github.com/trackmastersteve/alienfx",
    license = "GPLv3",
    
    install_requires = ["pyusb>=1.0.0b1"],
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
udev_file = resource_filename("alienfx", "data/etc/udev/rules.d/10-alienfx.rules")
udev_rules_dir = "/etc/udev/rules.d/"
try:
    if not os.path.exists(udev_rules_dir):
        print("Udev rules directory {} does not exist. Will not copy udev rules file.".format(udev_rules_dir))
    elif not os.access(udev_rules_dir, os.W_OK):
        print("Udev rules directory {} is not writable. Will not copy udev rules file.".format(udev_rules_dir))
    else:
        shutil.copy(udev_file, udev_rules_dir)
except IOError:
    print("Unable to copy udev rules file {} to {}".format(udev_file, udev_rules_dir))
