import os
import logging
import threading

# read environment variables
LOG_FILE = os.environ.get('LOG_FILE', '/var/log/nvr.log')

# Create a global lock
log_lock = threading.Lock()


def setup_logging(debug=False):
    if debug:
        logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s [%(levelname)s]: %(message)s')
    else:
        logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')


def log_info(message):
    with log_lock:
        logging.info(message)


def log_error(message):
    with log_lock:
        logging.error(message)


def log_debug(message):
    with log_lock:
        logging.debug(message)
