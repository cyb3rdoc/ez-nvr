#!/usr/bin/env python

import os
import logging
import time

# set environment variables
os.environ['CONFIG_FILE'] = "/config/config.yaml"
os.environ['LOG_FILE'] = "/var/log/nvr.log"
os.environ['OUTPUT_DIR'] = "/storage"
os.environ['HEALTH_STATE'] = "false"

# read environment variables
CONFIG_FILE = os.environ.get('CONFIG_FILE', '/config/config.yaml')
LOG_FILE = os.environ.get('LOG_FILE', '/var/log/nvr.log')
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', '/storage')

# import eznvr modules and utilities
from utils.args import get_args
from utils.logger import setup_logging
from utils.config import load_config
from modules.recording import start_recording, stop_recording
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
            raw_path = get_raw_path(cam_name)
            # move completed video files to date folder
            for filename in os.listdir(raw_path):
                if filename.endswith(".mkv"):
                    move_completed_file(cam_name, filename)
            # check for presence of new video files
            raw_files = os.listdir(raw_path)
            if len(raw_files) == 0 or raw_files[-1].endswith(".part"):
                os.environ['HEALTH_STATE'] = "false"
                logging.error(f"NVR: Recording for camera {cam_name} has stopped unexpectedly!")
                stop_recording(process)
                del camera_processes[cam_name]
                cam_config = next((c for c in config['cameras'] if c.get('camera_name') == cam_name), None)
                if cam_config:
                    process = start_recording(cam_config)
                    logging.info(f"NVR: Recording restarted for camera {cam_name}.")
                    if process:
                        camera_processes[cam_name] = process
                else:
                    logging.error(f"NVR: Could not find configuration for camera {cam_name}.")
            else:
                os.environ['HEALTH_STATE'] = "true"
        time.sleep(60)

if __name__ == '__main__':
    main()
