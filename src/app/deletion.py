#!/usr/bin/env python

import os
from datetime import datetime, timedelta
import shutil
import yaml
import logging

CONFIG_FILE = "/config/config.yaml"
LOG_FILE = "/var/log/nvr.log"
OUTPUT_DIR = "/storage"

def setup_logging():
    logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s [%(levelname)s]: %(message)s')

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logging.error(f"Deletion: Error loading configuration: {e}")
    return config

def delete_old_folders(config):
    days_to_subtract = config.get("video_store", 21)
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
            logging.info(f"Deletion: {camera_folder_path} found and removed.")
        else:
            logging.info(f"Deletion: {camera_folder_path} not found.")

def main():
    setup_logging()
    config = load_config()
    logging.info(f"Deletion: Initializing deletion of old directories...")
    delete_old_folders(config)

if __name__ == "__main__":
    main()
