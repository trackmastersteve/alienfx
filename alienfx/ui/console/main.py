#
# main.py
#
# Copyright (C) 2013-2014 Ashwin Menon <ashwin.menon@gmail.com>
# Copyright (C) 2015-2024 Track Master Steve <trackmastersteve@gmail.com>
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
from alienfx.core.colorutil import parse_rgb_string
import json
from alienfx import Alienware, Zone
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


def doZonescan():
    if sys.version_info < (3, 0):
        # Python 2.x
        print("Zonescan might not run correctly under Python 2."
              "If you experience issues, try running under Python 3 instead.")
    print("Performing zonescan...")
    # Call Zonescanning here...
    zonescan = alienfx_zonescanner.Zonescanner("0x187c")
    zonescan.scan()


def start():
    """ Main entry point for the alienfx cli."""

    # You may switch the commenting of the following 2 lines to force zonescan-execution
    controller = AlienFXProber.get_controller()  # DEBUG: you may comment this out for development of zonescanner
    # controller = None  # DEBUG: you may uncomment this out for development of zonescanner

    if controller is None:
        logging.error("No Alien FX controller, defined by a supported model, found!")
        logging.info("Asking user for zone probing...")
        # print("No Alien FX controller, defined by a supported model, found.")
        if askuser("Would you like to perform a zonescan?"):
            # User answered yes: Zonescan should be performed
            doZonescan()
            print("Zonescan finished")
            logging.info("Zonescan finished")
            return True
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
        argparser.add_argument(
            "-z", "--zonescan", action="store_true", help="starts a zonescan"
        )
        argparser.add_argument(
            "-c", "--connector", action="store_true", help="show HDMI connector state"
        )
        argparser.add_argument(
            "-e", "--led-state", action="store_true", help="show LED state"
        )
        argparser.add_argument(
            "-H", "--head", help="set head LED (name or 'R G B')"
        )
        argparser.add_argument(
            "-L", "--left", help="set left LED (name or 'R G B')"
        )
        argparser.add_argument(
            "-R", "--right", help="set right LED (name or 'R G B')"
        )
        argparser.add_argument(
            "-j", "--json", action="store_true", help="output JSON for machine readability"
        )
        args = argparser.parse_args()
        if args.zonescan is not None:
            if args.zonescan:
                doZonescan()
                return True

        # New sysfs-based quick commands (use the Alienware helper)
        if any([args.connector, args.led_state, args.head, args.left, args.right]):
            aw = Alienware()
            json_data = {}
            if args.connector:
                try:
                    hdmi = aw.get_hdmi()
                    if args.json:
                        json_data['hdmi'] = {
                            'exists': hdmi.exists,
                            'input': str(hdmi.cable_state),
                            'output': str(hdmi.source),
                        }
                    else:
                        print("HDMI passthrough state:", "present" if hdmi.exists else "not present")
                        if hdmi.exists:
                            print("    Input HDMI is {}".format(hdmi.cable_state))
                            print("    Output HDMI is connected to {}".format(hdmi.source))
                        print()
                except PermissionError:
                    print("You do not have permission to run this command (sudo required.)")

            if args.led_state:
                try:
                    leds = aw.get_rgb_zones()
                    if args.json:
                        leds_data: dict = {'exists': leds.exists}
                        for zone, val in leds.zones.items():
                            leds_data[str(zone)] = {'red': val.red, 'green': val.green, 'blue': val.blue}
                        json_data['leds'] = leds_data
                    else:
                        print("LED state:", "present" if leds.exists else "not present")
                        if leds.exists:
                            for zone, val in leds.zones.items():
                                print("    {}:".format(zone))
                                print("        red: {}".format(val.red))
                                print("        green: {}".format(val.green))
                                print("        blue: {}".format(val.blue))
                        print()
                except PermissionError:
                    print("You do not have permission to run this command (sudo required.)")


            for arg_name, zone in [(args.head, Zone.Head), (args.left, Zone.Left)]:
                if arg_name is not None:
                    rgb = parse_rgb_string(arg_name)
                    if rgb is not None:
                        try:
                            aw.set_rgb_zone(zone, rgb[0], rgb[1], rgb[2])
                        except PermissionError:
                            print("You do not have permission to run this command (sudo required.)")

            if args.json:
                print(json.dumps(json_data))
            return True

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
        logging.error(str(e) + "\n Python-Version: "+sys.version) 
