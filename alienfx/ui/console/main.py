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

def start():
    """ Main entry point for the alienfx cli."""
    
    controller = AlienFXProber.get_controller()
    if controller is None:
        logging.error("No supported Alien FX controllers found!")
        quit()
        
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
            print ("Available themes:")
            themes = themefile.get_themes()
            for t in themes:
                print(("\t{}").format(t))
        elif args.theme is not None:
            themefile.load(args.theme)
            controller.set_theme(themefile)
            themefile.applied()
            
    except Exception as e:
        logging.error(e)
