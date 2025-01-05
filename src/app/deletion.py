#!/usr/bin/env python

import os
import shutil
from datetime import datetime, timedelta

# read environment variables
CONFIG_FILE = os.environ.get('CONFIG_FILE', '/config/config.yaml')
LOG_FILE = os.environ.get('LOG_FILE', '/var/log/nvr.log')
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', '/storage')

# import eznvr modules and utilities
from utils.args import get_args
from utils.logger import setup_logging, log_info, log_debug
from utils.config import load_config


def delete_old_folders(config):
    days_to_subtract = config.get("video_store", 15)
    cameras = config.get("cameras", [])

    for camera in cameras:
        camera_name = camera["camera_name"]
        folder_path = os.path.join(OUTPUT_DIR, camera_name)

        # Calculate the date to look for
        date_to_check = datetime.now() - timedelta(days=days_to_subtract)
        date_folder_name = date_to_check.strftime("%Y-%m-%d")

        # Check if the date folder exists for this camera and delete it
        camera_folder_path = os.path.join(folder_path, date_folder_name)
        if os.path.exists(camera_folder_path):
            shutil.rmtree(camera_folder_path)
            log_info(f"Deletion: {camera_folder_path} found and removed")
        else:
            log_info(f"Deletion: {camera_folder_path} not found")


def main():
    # parse command line arguments
    args = get_args()
    # set up logging
    setup_logging(debug=args.debug)
    # load user configuration from config.yaml file
    config = load_config()
    log_debug("Deletion: Initializing deletion of old directories")
    delete_old_folders(config)


if __name__ == "__main__":
    main()
