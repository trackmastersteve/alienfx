#
# logger.py
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

""" Provides logging facilities for alienfx. """

import logging
import os.path

# By default, only ERRORS and above are enabled, and they are printed to the 
# console
logging.disable(logging.WARNING)

def set_logfile(path):
    """ Set a log file to print logs to. By default, no logs are printed to 
    file. If a log file is set, then all levels of log messages are enabled 
    and sent to it.
    """
    logging.disable(logging.NOTSET)
    logging.basicConfig(
        filename=os.path.expanduser(path), 
        filemode="w",
        level=logging.NOTSET, 
        )#format="%(levelname)s:%(module)s:%(lineno)d:%(message)s")
