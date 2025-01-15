#!/usr/bin/env python

import os
import time
from threading import Thread
import threading

# set environment variables
os.environ['CONFIG_FILE'] = "/config/config.yaml"
os.environ['OUTPUT_DIR'] = "/storage"
os.environ['HEALTH_STATE'] = "false"

# read environment variables
CONFIG_FILE = os.environ.get('CONFIG_FILE', '/config/config.yaml')
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', '/storage')

# import eznvr modules and utilities
from utils.args import get_args
from utils.logger import setup_logging, log_info, log_error, log_debug
from utils.config import load_config
from utils.filesystem import get_raw_path, move_completed_file
from utils.common import stop_flags, stop_flags_lock
from modules.recording import start_recording, stop_recording

def main():
    # parse command line arguments
    args = get_args()
    # set up logging
    setup_logging(debug=args.debug)
    log_info("NVR: Initializing EZ-NVR...")
    # load user configuration from config.yaml file
    log_debug("NVR: Loading configuration file...")
    config = load_config()
    # initialize camera stream recording
    camera_threads = {}
    for cam_config in config['cameras']:
        cam_name = cam_config['camera_name']
        log_info(f"NVR: Connecting to {cam_name} at {cam_config['camera_ip']}.")
        stop_flag = threading.Event()
        thread = Thread(target=start_recording, args=(cam_config, stop_flag))
        thread.start()
        camera_threads[cam_name] = thread
        # Store the stop flag in the global dictionary
        with stop_flags_lock:
            stop_flags[cam_name] = stop_flag

    while True:
        for cam_name, thread in list(camera_threads.items()):
            raw_path = get_raw_path(cam_name)
            # move completed video files to date folder
            for filename in os.listdir(raw_path):
                if filename.endswith(".mkv"):
                    move_completed_file(cam_name, filename)
            # check for presence of new video files
            raw_files = os.listdir(raw_path)
            if len(raw_files) == 0 or raw_files[-1].endswith(".part"):
                os.environ['HEALTH_STATE'] = "false"
                log_error(f"NVR: Recording for camera {cam_name} has stopped unexpectedly!")
                stop_recording(cam_name)
                del camera_threads[cam_name]
                cam_config = next((c for c in config['cameras'] if c.get('camera_name') == cam_name), None)
                if cam_config:
                    stop_flag = threading.Event()
                    thread = Thread(target=start_recording, args=(cam_config, stop_flag))
                    thread.start()
                    camera_threads[cam_name] = thread
                    with stop_flags_lock:
                        stop_flags[cam_name] = stop_flag
                    log_info(f"NVR: Recording restarted for camera {cam_name}.")
                else:
                    log_error(f"NVR: Could not find configuration for camera {cam_name}.")
            else:
                os.environ['HEALTH_STATE'] = "true"
        time.sleep(60)

if __name__ == '__main__':
    main()
