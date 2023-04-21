import os
import logging

# read environment variables
LOG_FILE = os.environ.get('LOG_FILE', '/var/log/nvr.log')

def setup_logging(debug=False):
    if debug:
        logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s [%(levelname)s]: %(message)s')
    else:
        logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')
