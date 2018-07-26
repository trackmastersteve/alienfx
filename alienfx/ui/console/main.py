#
# main.py
#
# Copyright (C) 2013-2014 Ashwin Menon <ashwin.menon@gmail.com>
# Copyright (C) 2015-2018 Track Master Steve <trackmastersteve@gmail.com>
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
# along with alienfx.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#

""" Command line interface to alienfx. """


import argparse
import logging
import pkg_resources
import alienfx.common
from alienfx.core.prober import AlienFXProber
import alienfx.core.themefile as alienfx_themefile
import alienfx.core.logger as alienfx_logger
import alienfx.core.zonescanner as alienfx_zonescanner
import sys


def askuser(question):
    while "Your answer was invalid.":
        # Python 2.x => raw_input / python 3.x => input
        if sys.version_info < (3, 0):
            # Python 2.x
            reply = raw_input((question+' (y/n): ').lower().strip())
        else:
            # Python 3.x
            reply = input((question + ' (y/n): ').lower().strip())
        if reply.__len__() > 0:
            if reply[0] == 'y':
                return True
            if reply[0] == 'n':
                return False

def start():
    """ Main entry point for the alienfx cli."""
    print("You are running alienfx under Python-Version: "+sys.version)

    # You may switch the commenting of the following 2 lines to force zonescan-execution
    controller = AlienFXProber.get_controller()  # DEBUG: you may comment this out for development of zonescanner
    # controller = None  # DEBUG: you may uncomment this out for development of zonescanner

    if controller is None:
        logging.error("No Alien FX controller, defined by a supported model, found!")
        logging.info("Asking user for zone probing...")
        # print("No Alien FX controller, defined by a supported model, found.")
        if askuser("Would you like to perform a zonescan?"):
            # User answered yes: Zonescan should be performed
            print("Performing zonescan...")
            # Call Zonescanning here...
            zonescan=alienfx_zonescanner.Zonescanner("0x187c")
            zonescan.scan()
            print("Zonescan finished")
            logging.info("Zonescan finished")
        else:
            # No Zonescan should be performed
            print("OK. Bye.")
            logging.info("Zonescanning not performed")
        quit()  # Finish
        
    themefile = alienfx_themefile.AlienFXThemeFile(controller)
    try:
        argparser = argparse.ArgumentParser(
            description="""AlienFX is a utility to control the lighting effects 
                of your Alienware computer. 
                Lighting effect configurations are stored in theme files."""
        )
        argparser.add_argument(
            "-l", "--log", help="write detailed logging information to LOG"
        )
        argparser.add_argument(
            "-t", "--theme",
            help="set the lighting theme to THEME."
        )
        argparser.add_argument(
            "-s", "--list", action="store_const", const=1, 
            help="list all available lighting themes"
        )
        argparser.add_argument(
            "-v", "--version", action="version", 
            version="%(prog)s {}".format(alienfx.common.get_version())
        )
        args = argparser.parse_args()
        if args.log is not None:
            alienfx_logger.set_logfile(args.log)
        if args.list is not None:
            print("Available themes:")
            themes = themefile.get_themes()
            for t in themes:
                print(("\t{}").format(t))
        elif args.theme is not None:
            themefile.load(args.theme)
            controller.set_theme(themefile)
            themefile.applied()
            
    except Exception as e:
        logging.error(e)
