import os
import signal
import logging
import sys
import platform
import argparse
from rich.traceback import install as rich_traceback_install
from rich.logging import RichHandler

from src.general.constants import DATASTORE_ROOT, PROJECT_ROOT
from src.general._low_level import sigint_handler
from src.lab1_pendulum.constants import datapath_log


# parsing arguments
parser = argparse.ArgumentParser(description='lab1_pendulum')
parser.add_argument("-v", "--verbose", action="store_true", help="print logs to console")
args = parser.parse_args()


# configuring logger
logging.basicConfig(
	filename=datapath_log,
	filemode='w',
	level=logging.DEBUG,
	format='%(asctime)s.%(msecs)03d - %(levelname)s: %(message)s'
)
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)
if args.verbose:
	logging.getLogger().addHandler(RichHandler(log_time_format="[%d/%m/%Y %T.%f]"))
rich_traceback_install(width=300, show_locals=True)  # will be removed in production


# ctrl-c handler
signal.signal(signal.SIGINT, sigint_handler)  # noqa

# python version check
if platform.python_version_tuple()[:2] != ('3', '10'):
	msg = f"Python version check failed! Found incompatible version {''.join(platform.python_version_tuple())}, leaving"
	logging.critical(msg)
	raise OSError(msg)

# creating required folders
if not os.path.exists(DATASTORE_ROOT):
	print('creating DATASTORE_ROOT')
	os.mkdir(DATASTORE_ROOT)
if not os.path.exists(os.path.join(DATASTORE_ROOT, "lab1_pendulum")):
	os.mkdir(os.path.join(DATASTORE_ROOT, "lab1_pendulum"))

# adding project root to PYTHONPATH
sys.path.insert(1, PROJECT_ROOT)

from src.lab1_pendulum import start
if __name__ == '__main__':
	try:
		start()
	except Exception as e:
		logging.exception(e)
		raise
