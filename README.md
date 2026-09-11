
AlienFX is a Linux utility to control the lighting effects of your Alienware computer.
============

AlienFX provides both a CLI (``alienfx``) and a GTK4 GUI (``alienfx-gtk``). It
has been tested on Debian/Ubuntu/Kali/Mint, Fedora and Arch Linux.

[![Version](https://img.shields.io/badge/version-2.5.0-red.svg)]() [![GitHub license](https://img.shields.io/github/license/trackmastersteve/alienfx.svg)](https://github.com/trackmastersteve/alienfx/tree/2.1.x/LICENSE) [![Python3](https://img.shields.io/badge/python-3.14-green.svg)]() ![GTK4](https://img.shields.io/badge/gtk-4-blue.svg)]() [![GitHub issues](https://img.shields.io/github/issues/trackmastersteve/alienfx.svg)](https://github.com/trackmastersteve/alienfx/issues) [![GitHub stars](https://img.shields.io/github/stars/trackmastersteve/alienfx.svg)](https://github.com/trackmastersteve/alienfx/stargazers)  [![GitHub forks](https://img.shields.io/github/forks/trackmastersteve/alienfx.svg)](https://github.com/trackmastersteve/alienfx/network)

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com) Contributers needed! Please read [CONTRIBUTING.md](https://github.com/trackmastersteve/alienfx/blob/master/CONTRIBUTING.md) for further details. 

![AlienFX](https://github.com/trackmastersteve/alienfx/blob/master/alienfx/data/pixmaps/alienfx.png)

## Table of Contents

- [Dependencies](#dependencies)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)

## Dependencies

AlienFX is written in Python and requires Python 3.14 or newer. The GTK4 GUI
also requires GTK 4 and GObject introspection libraries. Python dependencies
are listed in ``requirements.txt`` and currently include:

```text
pyusb>=1.3.1
setuptools>=84.0.0
PyGObject>=3.58.0
pycairo>=1.29.1
```

On Arch Linux:

```sh
      $ sudo pacman -S gtk4 python-pyusb python-setuptools python-gobject python-cairo
```
    
On Debian/Ubuntu/Mint/Kali: 

```sh
      $ sudo apt install gir1.2-gtk-4.0 libcairo2-dev python3-gi python3-gi-cairo python3-setuptools python3-usb
```

On Fedora: 

```sh
      $ sudo dnf install gtk4 cairo-devel python3-gobject cairo-gobject python3-setuptools python3-pyusb
```

## Installation

On Arch Linux you can install package from AUR: [alienfx](https://aur.archlinux.org/packages/alienfx/)

For a manual installation, create a virtual environment, install the current
Python dependencies, and install AlienFX from the project directory:

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install .
```

The installed commands are ``alienfx`` and ``alienfx-gtk``. To install the
package in editable mode while developing, replace the last command with:

```sh
.venv/bin/python -m pip install -e .
```

The package includes a udev rules file that allows AlienFX to access the AlienFX
USB controller without needing root permissions. Install it separately with
root privileges, then reload udev:

```sh
sudo install -m 644 alienfx/data/etc/udev/rules.d/10-alienfx.rules /etc/udev/rules.d/10-alienfx.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Usage

Lighting configurations are stored in "theme files", which are simple json
files stored in ``$XDG_CONFIG_HOME/alienfx``. If ``XDG_CONFIG_HOME`` is not set, then
``~/.config/alienfx`` is used. Both the CLI and GUI programs use these theme
files, and the GUI program allows you to create new themes as well.

When the GTK4 interface is started without root privileges, the toolbar
includes an Authenticate action. It uses ``pkexec`` to prompt for credentials,
then relaunches the GUI in root mode so hardware access can be performed from
the elevated session.

See the man page of alienfx ``$ man alienfx`` for the cli options supported. 

If you run the CLI-version of alienfx on a currently unsupported device, the program will ask you if you wish to perform a zonescan.
Please consider using this feature to determine the correct zone-codes for your device.
If you found the correct codes, please contribute to the project. - You'll find more information in Section [Contributing](#contributing) 

Supported models and adding support for new models:
--------------------------------------------------

Please have a look at [devicelist](https://github.com/trackmastersteve/alienfx/blob/master/docs/Knowledgebase/Devicelist.md)

## Contributing

Please read [CONTRIBUTING.md](https://github.com/trackmastersteve/alienfx/blob/master/CONTRIBUTING.md) for further details. 

## Further Informatin
If you're looking for further information, have a look in docs/Knowledgebase

## Disclaimer and License
If you use this software, you use it AT YOUR OWN RISK.
I and the contributing developers DO NOT accept responsibility for frying your AlienFX controller chip with this code.
Haven't fried any yet, but this is just so we can sleep at night. ;)


This software is licenced under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)

This is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the [GNU GPL]((https://www.gnu.org/licenses/gpl-3.0.html)) for more detail.

