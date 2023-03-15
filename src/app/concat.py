#!/usr/bin/env python

import os
import sys
import time
from datetime import datetime, timedelta
import yaml
import subprocess
import logging

CONFIG_FILE = "/config/config.yaml"
LOG_FILE = "/var/log/nvr.log"
OUTPUT_DIR = "/storage"

def setup_logging():
    logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s [%(levelname)s]: %(message)s')

def concat_videos(cam_name):
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    cam_path = os.path.join(OUTPUT_DIR, cam_name)
    concat_path = os.path.join(cam_path, yesterday)
    if not os.path.exists(concat_path):
        logging.info(f"Concat: Directory {concat_path} unavailable.")
        logging.info(f"Concat: No videos found for {yesterday}...Cancelling concatenation.")
        sys.exit()
    input_file = os.path.join(concat_path, "files.txt")
    files = [f for f in os.listdir(concat_path) if f.endswith(".mkv")]
    mkv_files = sorted(files, key=lambda x: datetime.strptime(x, '%Y-%m-%dT%H-%M-%S.mkv'))
    try:
        with open(input_file, "w") as f:
            for file in mkv_files:
                f.write("file '{}'\n".format(os.path.join(concat_path, file)))

        cmd = f"ffmpeg -hide_banner -y -loglevel warning -f concat -safe 0 -i {input_file} -c copy {concat_path}/{cam_name}_{yesterday}.mkv"
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            logging.info(f"Concat: Video clips of {yesterday} for {cam_name} concatenated.")
        else:
            logging.error(f"Concat: Error while concatenating video of {yesterday} for {cam_name}: {result.stderr}")
    except Exception as e:
        logging.error(f"Concat: Error while opening input file: {e}")

    try:
        with open(input_file, "r") as f:
            for line in f:
                os.remove(line.strip().split("'")[1])
            logging.info(f"Concat: Source videos of {yesterday} for {cam_name} removed.")
    except Exception as e:
        logging.error(f"Concat: Error while removing source videos of {yesterday} for {cam_name}: {e}")


if __name__ == "__main__":
    setup_logging()
    with open(CONFIG_FILE, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
            cameras = config['cameras']
        except yaml.YAMLError as exc:
            logging.error(exc)

    logging.info(f"Concat: Starting video concatenation for {len(cameras)} camera(s).")

    for camera in cameras:
        cam_name = camera['camera_name']
        concat_videos(cam_name)
