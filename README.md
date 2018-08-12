
AlienFX is a Linux utility to control the lighting effects of your Alienware computer.
============

At present there is a CLI version (``alienfx``) and a gtk GUI version (``alienfx-gtk``). And 
has been tested on Debian/Ubuntu/Kali/Mint 19, Fedora and Arch Linux.

[![Version](https://img.shields.io/badge/version-2.3.4-red.svg)]() [![GitHub license](https://img.shields.io/github/license/trackmastersteve/alienfx.svg)](https://github.com/trackmastersteve/alienfx/tree/2.1.x/LICENSE) [![Python3](https://img.shields.io/badge/python-3.6-green.svg)]() [![GitHub issues](https://img.shields.io/github/issues/trackmastersteve/alienfx.svg)](https://github.com/trackmastersteve/alienfx/issues) [![GitHub stars](https://img.shields.io/github/stars/trackmastersteve/alienfx.svg)](https://github.com/trackmastersteve/alienfx/stargazers)  [![GitHub forks](https://img.shields.io/github/forks/trackmastersteve/alienfx.svg)](https://github.com/trackmastersteve/alienfx/network) 

![AlienFX](https://github.com/trackmastersteve/alienfx/blob/master/alienfx/data/pixmaps/alienfx.png)

## Table of Contents

- [Dependencies](#dependencies)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)

## Dependencies

AlienFX is written in python and has been tested on ``python 3.6`` (<2.1.1 using ``python 2.7``). It requires
the following python packages to run:

On Arch Linux:

For 2.0.6:
```sh
      $ sudo pacman -S python2-pyusb python2-setuptools python2-gobject python2-cairo
```
For 2.1+:
```sh
      $ sudo pacman -S python-pyusb python-setuptools python-gobject python-cairo python-future
```

On other distributions you need to install ``pyusb`` and ``pkg_resources`` using pip:
1. pkg_resources.
   You can install ``pkg_resources`` using the following command:
      ```sh
            $ pip install setuptools
      ```

2. pyusb >= 1.0.0b1.
   Note that your distribution may only provide ``the pre-1.0`` version of ``pyusb``. If
   this is the case, you can install ``pyusb 1.0`` using the 
   following command:
      ```sh
            $ pip install --pre pyusb
      ```
3. future.
   You can install ``future`` using the following command:
      ```sh
            $ pip install future
      ```
You can install all of these by running the command:

   ```sh
            $ pip install -r requirements.txt
   ```
      
And then install following packages using package manager:      
   
   On Debian/Ubuntu/Mint/Kali: 
   ```sh
            $ sudo apt install libcairo2-dev python-gi python-gi-cairo
   ```

   On Fedora: 
   ```sh
            $ sudo dnf install cairo-devel pygobject3 cairo-gobject
   ```

## Installation

On Arch Linux you can install package from AUR: [alienfx](https://aur.archlinux.org/packages/alienfx/)

For manual installation of AlienFX, use the following commands:

Please note, that the installer is still written in python 2.x while the application should already be python 3.x compatible.
So if you have python 2 and 3 installed, run the installer with python2 instead of python.
  
  ```sh
      $ sudo python setup.py install
  ```
  ```sh
      $ sudo python setup.py install_data
  ```

Note that the second invocation is required to ensure that icon files etc. are
properly installed.

The installation includes a udev rules file that allows AlienFX to access the 
AlienFX USB controller on your computer without needing root permissions. If 
you run the install commands without sudo, then the udev rules file will not 
be installed. 

## Usage

Lighting configurations are stored in "theme files", which are simple json
files stored in ``$XDG_CONFIG_HOME/alienfx``. If ``XDG_CONFIG_HOME`` is not set, then
``~/.config/alienfx`` is used. Both the CLI and GUI programs use these theme
files, and the GUI program allows you to create new themes as well.

See the man page of alienfx for the cli options supported.

If you run the CLI-version of alienfx on a currently unsupported device, the programm will ask you if you wish to perform a zonescan.
Please consider using this feature to determine the correct zone-codes for your device.
If you found the correct codes, please contribute to the project. - You'll find more information in Section [Contributing](#contributing) 

Supported models and adding support for new models:
--------------------------------------------------

Please have a look at [devicelist](https://github.com/trackmastersteve/alienfx/blob/master/docs/Knowledgebase/Devicelist.md)

## Contributing

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) Please read [CONTRIBUTING.md](https://github.com/trackmastersteve/alienfx/blob/master/CONTRIBUTING.md) for further details. 

## Further Information
If you look for further informations, have a look in docs/Knowledgebase

## Disclaimer and License
If you use this software, you use it ON YOUR OWN RISK.
I and the contributing developers DO NOT accept responsibility for frying your AlienFX controller chip with this code.
Not fried any yet, but this is just so we can sleep at night. ;)


This software is licenced under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)

This is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation.

This programm is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the [GNU GPL]((https://www.gnu.org/licenses/gpl-3.0.html)) for more detail.

