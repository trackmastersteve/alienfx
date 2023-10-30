#
# zonescanner.py
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
#
# Zonescanner-class which should test different zone codes. - This could make adding new devices easier.
# initial development by derco0n <https://github.com/derco0n> (July/2018)

from alienfx.core.prober import AlienFXProber
from builtins import str,hex
import alienfx.core.controller as alienfx_controller
import os
import sys
import logging



class Zonescanner:
    def __init__(self, vendorid):
        self.vendorid=vendorid
        self.maxzone=0x8000  # Greatest possible zone address
        self.blinkcolor=[0xF, 0xF, 0xF]  # In which color should the zones blink while searching?
        self.staticcolor=[0xF, 0xF, 0xF]  # In which color should the zones light, when zone is found?
        self.speed = 200  # Which speed (for loop/blink) should be used?
        # self.slot1command = [2, 8, 1, 0, 0, 0, 0, 0, 0]
        self.zonesfound = {}  # A Dictionary of all zones found

    def askuser(self, question):
        while "Your answer was invalid.":
            # Python 2.x => raw_input / python 3.x => input
            if sys.version_info < (3, 0):
                # Python 2.x
                reply = raw_input((question + ' (y/n): ').lower().strip())
            else:
                # Python 3.x
                reply = input((question + ' (y/n): ').lower().strip())
            if reply.__len__() > 0:
                if reply[0] == 'y':
                    return True
                if reply[0] == 'n':
                    return False

    def askzonename(self):
        question = "Please enter a name for this zone."
        # Python 2.x => raw_input / python 3.x => input
        if sys.version_info < (3, 0):
            # Python 2.x
            reply = raw_input((question + ' : ').lower().strip())
        else:
            # Python 3.x
            reply = input((question + ' : ').lower().strip())
        if reply.__len__() > 0:
            return reply.lower().strip()

    def scanzone(self, zone, controllertype, vid, pid):
        myctr=alienfx_controller.AlienFXController(controllertype)

        myctr.vendor_id = vid
        myctr.product_id = pid
        myctr.reset_types = {3: 'all-lights-off', 4: 'all-lights-on'}

        try:
            # Make controller ready
            myctr._driver.acquire()
            myctr._ping()
            myctr._reset('all-lights-off')
            myctr._wait_controller_ready()

            # Make commands
            cmds = []

            # Set current zone to color white blink for initial (boot) state...

            # Step 1: Set things first
            # cmds.append(self.slot1command)  # Save to Slot 1
            cmds.append(myctr.cmd_packet.make_cmd_save_next(1))  # Save next to Slot 1 (boot)
            cmds.append(myctr.cmd_packet.make_cmd_set_blink_colour(1, zone, self.blinkcolor))
            cmds.append(myctr.cmd_packet.make_cmd_save_next(1))  # Save next to Slot 1 (boot)
            cmds.append(myctr.cmd_packet.make_cmd_loop_block_end())  # loop
            cmds.append(myctr.cmd_packet.make_cmd_save())  # save permanent
            myctr._send_cmds(cmds)

            # Step 2: Set speed
            cmds = []
            cmds.append(myctr.cmd_packet.make_cmd_set_speed(self.speed))  # Set speed
            myctr._send_cmds(cmds)

            # Step 3: Set things again, as we are setting for zone 1 (boot)
            cmds = []
            cmds.append(myctr.cmd_packet.make_cmd_set_blink_colour(1, zone, [0xF, 0xF, 0xF]))
            cmds.append(myctr.cmd_packet.make_cmd_loop_block_end())  # loop
            cmds.append([2, 3, 2, 255, 130, 16, 0, 0, 0, 0])  # Don't know exactly what this does... 2,3,2 setting color for second sequence or something like that...
            cmds.append(myctr.cmd_packet.make_cmd_loop_block_end())  # loop
            myctr._send_cmds(cmds)

            # Step 4: Set the execute command.
            cmds = []
            cmds.append(myctr.cmd_packet.make_cmd_transmit_execute())  # Execute...
            myctr._send_cmds(cmds)

        except:
            logging.error("Error while testing current zone...")

        finally:
            myctr._driver.release()
        if self.askuser("Is anything blinking now?"):
            # User saw something blinking
            return True
        return False

    def scan(self):
        print("Welcome. This will help you to scan for alienfx-controllers and their lighting zones.")
        afxcontroldevs=AlienFXProber.find_controllers(self.vendorid)  # Get a list of all usb-devices with the given vendor-id
        for controller in afxcontroldevs:
            # Perform zone scanning for each controller found...
            zone = 1  # initial zone from which we start iterating
            vendorstring = "0x" + format(controller.idVendor, '04x')
            devicestring = "0x" + format(controller.idProduct, '04x')
            print("Found device \""+vendorstring + " / " + devicestring + "\". ")
            if self.askuser("Would you like to test a newer controller? Default=Y\r\n"
                            "Note that choosing a wrong controller will result in packet-errors.\r\n"
                            "In this case you might choose another one instead."):
                crev=2  # newer controller revision
            else:
                crev=1  # old controller revision
            print("- Testing zones...")
            while zone <= self.maxzone:
                # Iterate all possible zone codes (have a look at reverse-engineering-knowledgebase.txt for possible codes...)
                print("Testing zone \"0x"+format(zone, '04x')+"\"")
                if self.scanzone(zone, crev, controller.idVendor, controller.idProduct):
                    # Zone found
                    print("Zone found :)")
                    # Ask user for a name, store name and zonecode
                    zonename = self.askzonename()
                    self.zonesfound[zonename] = zone  # Store name an zone code in Dictionary
                zone = zone*2
            print("")
            print("These are your " + str(len(self.zonesfound.items())) + " zonecodes for the current controller (\"VID: "+vendorstring + " / DEV: " + devicestring + "\"):")
            for z in self.zonesfound.items():
                print(z[0]+": 0x"+format(z[1], '04x'))  # Print out each zone found
            print("")
            print("Current controller finished.")

        print("All controllers done. I hope this was helpful.")
