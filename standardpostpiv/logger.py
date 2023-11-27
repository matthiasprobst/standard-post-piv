import logging
import pathlib
from logging.handlers import RotatingFileHandler

import appdirs

# see https://realpython.com/python-logging/
DEFAULT_LOGGING_LEVEL = logging.INFO

logdir = pathlib.Path(appdirs.user_log_dir('standardpostpiv'))
logdir.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger('standardpostpiv')
logger.setLevel(logging.INFO)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(logdir / 'standardpostpiv.log')
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)
#
# __formatter = logging.Formatter(
#     '%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
#     datefmt='%Y-%m-%d_%H:%M:%S')
# __file_handler = RotatingFileHandler(logdir / 'standardpostpiv.log')
# __file_handler.setLevel(logging.DEBUG)  # log everything to file!
# __file_handler.setFormatter(__formatter)
#
# __stream_handler = logging.StreamHandler()
# __stream_handler.setLevel(DEFAULT_LOGGING_LEVEL)
# __stream_handler.setFormatter(__formatter)
#
# logger.addHandler(__file_handler)
# logger.addHandler(__stream_handler)
