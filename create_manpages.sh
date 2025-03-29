#!/bin/bash
#
# This script creates the man pages for alienfx using help2man.
# alienfx must already be installed and in the path for this to work. You can
# use "python setup.py develop --install-dir <test dir>" and add <test dir> to
# the path to achive this.
#

help2man --no-discard-stderr -N -i docs/man/alienfx.supplemental.groff alienfx > docs/man/alienfx.1
