import os
import logging
import threading
import sys

# Create a global lock
log_lock = threading.Lock()

def setup_logging(debug=False):
    if debug:
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s]: %(message)s'
        )
    else:
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s]: %(message)s'
        )

def log_info(message):
    with log_lock:
        logging.info(message)

def log_error(message):
    with log_lock:
        logging.error(message)

def log_debug(message):
    with log_lock:
        logging.debug(message)
