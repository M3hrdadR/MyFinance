import os
import utils
import platform
import sys

assert platform.system() == 'Windows', 'This program only works on Windows.'
assert len(sys.argv) > 0, 'Please specify the linux home dir as the first parameter.'

PATH = utils.find_path(sys.argv[1])
utils.start(PATH)
