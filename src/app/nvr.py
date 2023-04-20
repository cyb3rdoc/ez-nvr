#!/usr/bin/env python

import os
import logging
import time

# set environment variables
os.environ['CONFIG_FILE'] = "/config/config.yaml"
os.environ['LOG_FILE'] = "/var/log/nvr.log"
os.environ['OUTPUT_DIR'] = "/storage"

# read environment variables
CONFIG_FILE = os.environ['CONFIG_FILE']
LOG_FILE = os.environ['LOG_FILE']
OUTPUT_DIR = os.environ['OUTPUT_DIR']

# import eznvr modules and utilities
from utils.args import get_args
from utils.logger import setup_logging
from utils.config import load_config
from modules.recording import start_recording
from utils.filesystem import get_raw_path, move_completed_file

def main():
    # parse command line arguments
    args = get_args()
    # set up logging
    setup_logging(debug=args.debug)
    logging.info(f"NVR: Initializing EZ-NVR...")
    # load user configuration from config.yaml file
    logging.debug(f"NVR: Loading configuration file...")
    config = load_config()
    # initialize camera stream recording
    camera_processes = {}
    for cam_config in config['cameras']:
        cam_name = cam_config['camera_name']
        logging.info(f"NVR: Connecting to {cam_name} at {cam_config['camera_ip']}.")
        process = start_recording(cam_config)
        if process:
            camera_processes[cam_name] = process

    while True:
        for cam_name, process in list(camera_processes.items()):
            if process.poll() is not None:
                del camera_processes[cam_name]
                logging.error(f"NVR: Recording for camera {cam_name} has stopped unexpectedly!")
                cam_config = next((c for c in config['cameras'] if c.get('camera_name') == cam_name), None)
                if cam_config:
                    process = start_recording(cam_config)
                    logging.info(f"NVR: Recording restarted for camera {cam_name}.")
                    if process:
                        camera_processes[cam_name] = process
                else:
                    logging.error(f"NVR: Could not find configuration for camera {cam_name}.")
            # Move completed video files to date folder
            raw_path = get_raw_path(cam_name)
            for filename in os.listdir(raw_path):
                if filename.endswith(".mkv"):
                    move_completed_file(cam_name, filename)

        time.sleep(60)

if __name__ == '__main__':
    main()
