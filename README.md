
AlienFX is a Linux utility to control the lighting effects of your Alienware computer.
============
At present there is a CLI version (alienfx) and a gtk GUI version (alienfx-gtk). And 
has been tested on Debian/Ubuntu/Kali, Fedora and Arch Linux.

Dependencies:
------------

AlienFX is written in python and has been tested on python 2.7. It requires
the following python packages to run:

1. pyusb >= 1.0.0b1
   Note that your distribution may only provide the pre-1.0 version of pyusb. If
   this is the case, you can install the 1.0 version of pyusb using the 
   following command:
      - pip install --pre pyusb

2. pkg_resources
   You can install using the following command:
      - pip install setuptools

3. cairo
   On Debian/Ubuntu/Kali you can install using the following command:
      - sudo apt install libcairo2-dev

   or Fedora:
      - sudo dnf install cairo-devel
      
   or Arch:
      - sudo pacman -S cairo

4. gi
   On Debian/Ubuntu/Kali you can install using the following command:
      - sudo apt install python-gi python-gi-cairo
   
   or Fedora:
      - sudo dnf install pygobject3 cairo-gobject
      
   or Arch:
      - sudo pacman -S python-gobject python-cairo 

Installation:
------------

Install AlienFX using these commands:
  
  - sudo python setup.py install
  - sudo python setup.py install_data

Note that the second invocation is required to ensure that icon files etc. are
properly installed.

The installation includes a udev rules file that allows AlienFX to access the 
AlienFX USB controller on your computer without needing root permissions. If 
you run the install commands without sudo, then the udev rules file will not 
be installed. Currently you have to run the command 'cp /etc/udev/rules.d/10-alienfx.rules 
/usr/lib/udev/rules.d/' in order for this application to work on Fedora and Arch.

Usage:
-----

Lighting configurations are stored in "theme files", which are simple json
files stored in `$XDG_CONFIG_HOME/alienfx`. If `XDG_CONFIG_HOME` is not set, then
`~/.config/alienfx` is used. Both the CLI and GUI programs use these theme
files, and the GUI program allows you to create new themes as well.

See the man page of alienfx for the cli options supported.

Supported models and adding support for new models:
--------------------------------------------------

At present, AlienFX supports and has been tested on the following Alienware models:

1. M11xR1   Laptop - support by [trackmastersteve](https://github.com/trackmastersteve)
2. M11xR2   Laptop - support by [trackmastersteve](https://github.com/trackmastersteve)
3. M11xR3   Laptop - support by [trackmastersteve](https://github.com/trackmastersteve)
4. M13xR2   Laptop - support by [Simon Wood](https://github.com/mungewell)
5. M14xR1   Laptop - support by [Ashwin Menon](https://github.com/ashwinm76)
6. M15x     Laptop - support by [trackmastersteve](https://github.com/trackmastersteve)
7. M17x     Laptop - support by [trackmastersteve](https://github.com/trackmastersteve)
8. M17xR3   Laptop - support by [trackmastersteve](https://github.com/trackmastersteve)
9. M18xR2   Laptop - support by [trackmastersteve](https://github.com/trackmastersteve)

To add support for a different model of Alienware computer, do the following:
----------------------------------------------------------------------------

1. Copy `alienfx/core/controller_m17x.py` to `controller_<your-computer-name>.py`
   in the same directory, and modify it using the original file as a reference.

2. At the top of `alienfx/core/prober.py`, add an import statement to import your
   new controller module created in step 1. This should be done at the docstring
   """ Import all subclasses of AlienFXController here. """. 

3. Modify `data/etc/udev/rules.d/10-alienfx.rules` to add a line for the VID and 
   PID corresponding to the AlienFX USB controller on your computer.

4. Test your modifications, and please submit a patch!

Disclaimer:
----------

I DO NOT accept responsibility for frying your AlienFX controller chip with my code.
Haven't fried any yet, but this is just so I can sleep at night. ;)
