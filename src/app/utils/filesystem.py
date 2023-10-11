import os
import time
import shutil
from datetime import datetime
from utils.logger import log_error, log_debug

# read environment variables
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', '/storage')


def get_camera_path(cam_name):
    cam_path = os.path.join(OUTPUT_DIR, cam_name)
    return cam_path


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
            log_debug(f"NVR: Camera directory {output_path} created.")
    except Exception as e:
        log_error(f"NVR: Error creating directory {output_path}: {e}")


def mkdir_raw(raw_path):
    try:
        if not os.path.exists(raw_path):
            os.makedirs(raw_path, exist_ok=True)
            log_debug(f"NVR: RAW directory {raw_path} created.")
    except Exception as e:
        log_error(f"NVR: Error creating directory {raw_path}: {e}")


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
            log_debug(f"NVR: Video section {filename} moved to {dest_path}.")
        except Exception as e:
            log_error(f"NVR: Error moving {filename} to {dest_path}: {e}")
