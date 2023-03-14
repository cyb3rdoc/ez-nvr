#!/usr/bin/env python

import os
import time
from datetime import datetime, timedelta
import logging
import subprocess
import yaml
import signal
import shutil

CONFIG_FILE = "/config/config.yaml"
LOG_FILE = "/var/log/nvr.log"
OUTPUT_DIR = "/storage"

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
    return config

def setup_logging():
    logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s [%(levelname)s]: %(message)s')
    logging.info(f"EZ-NVR initializing...")

def get_camera_path(cam_name):
    return os.path.join(OUTPUT_DIR, cam_name)

def get_raw_path(cam_name):
    cam_path = get_camera_path(cam_name)
    raw_path = os.path.join(cam_path, "raw")
    return raw_path

def get_output_path(cam_name):
    current_date = datetime.now().strftime("%Y-%m-%d")
    cam_path = get_camera_path(cam_name)
    output_path = os.path.join(cam_path, current_date)
    return output_path

def mkdir_dest(output_path):
    try:
        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)
            logging.info(f"Camera directory {output_path} created.")
    except Exception as e:
        logging.error(f"Error creating directory {output_path}: {e}")

def mkdir_raw(raw_path):
    try:
        if not os.path.exists(raw_path):
            os.makedirs(raw_path, exist_ok=True)
            logging.info(f"RAW directory {raw_path} created.")
    except Exception as e:
        logging.error(f"Error creating directory {raw_path}: {e}")

def start_recording(cam_config):
    cam_name = cam_config['camera_name']
    cam_ip = cam_config['camera_ip']
    rtsp_url = cam_config['camera_rtsp']
    codec = cam_config['camera_codec']
    interval = cam_config['camera_interval']
    output_path = get_output_path(cam_name)
    raw_path = get_raw_path(cam_name)

    mkdir_dest(output_path)
    mkdir_raw(raw_path)

    cmd = f"ffmpeg -hide_banner -y -loglevel error -rtsp_transport tcp -use_wallclock_as_timestamps 1 -i {rtsp_url} -c {codec} -f segment -reset_timestamps 1 -segment_time {interval} -segment_format mkv -segment_atclocktime 1 -strftime 1 {raw_path}/%Y-%m-%dT%H-%M-%S.mkv"

    try:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info(f"Camera {cam_name} initialized...")
        return process
    except subprocess.CalledProcessError as e:
        logging.error(f"Error starting recording: {e.output}")
    except Exception as e:
        logging.error(f"Error starting recording: {e}")

def stop_recording(process):
    process.send_signal(signal.SIGINT)
    process.wait()

def move_completed_file(cam_name, filename):
    src_path = os.path.join(get_raw_path(cam_name), filename)
    modified_time = os.path.getmtime(src_path)
    current_time = time.time()
    if current_time - modified_time > 60:
        date_str = filename.split("T")[0]
        output_path = os.path.join(get_camera_path(cam_name), date_str)
        mkdir_dest(output_path)
        dest_path = os.path.join(output_path, filename)
        try:
            shutil.move(src_path, dest_path)
        except Exception as e:
            logging.error(f"Error moving {filename} to {dest_path}: {e}")

def main():
    setup_logging()
    config = load_config()

    camera_processes = {}
    for cam_config in config['cameras']:
        cam_name = cam_config['camera_name']
        logging.info(f"Connecting to {cam_name} at {cam_config['camera_ip']}...")
        process = start_recording(cam_config)
        if process:
            camera_processes[cam_name] = process

    while True:
        for cam_name, process in camera_processes.items():
            if process.poll() is not None:
                logging.error(f"Recording for camera {cam_name} has stopped unexpectedly!")
                cam_config = next((c for c in config['cameras'] if c['camera_name'] == cam_name), None)
                if cam_config:
                    process = start_recording(cam_config)
                    logging.info(f"Camera recording restarted for {cam_name}")
                    if process:
                        camera_processes[cam_name] = process
                else:
                    logging.error(f"Could not find configuration for camera {cam_name}")
            # Move completed video files to date folder
            raw_path = get_raw_path(cam_name)
            for filename in os.listdir(raw_path):
                if filename.endswith(".mkv"):
                    move_completed_file(cam_name, filename)

        time.sleep(60)

if __name__ == '__main__':
    main()
