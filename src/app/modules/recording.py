import os
import time
import subprocess
from utils.filesystem import get_output_path, get_raw_path, mkdir_dest, mkdir_raw
from utils.logger import log_info, log_error
from utils.common import stop_flags, stop_flags_lock

def start_recording(cam_config, stop_flag):
    cam_name = cam_config['camera_name']
    cam_ip = cam_config['camera_ip']
    rtsp_url = cam_config['camera_rtsp']
    codec = cam_config['camera_codec']
    interval = cam_config['camera_interval']
    output_path = get_output_path(cam_name)
    raw_path = get_raw_path(cam_name)
    netcheck = 0
    # create necessary directories
    mkdir_dest(output_path)
    mkdir_raw(raw_path)
    # check connectivity to camera
    while True:
        # Check the stop flag periodically and exit if it's set
        if stop_flag.is_set():
            break

        response = os.system(f"ping -c 1 {cam_ip} > /dev/null 2>&1")
        if response == 0:
            log_info(f"NVR: Connection established to {cam_name} at {cam_ip}")
            break
        else:
            netcheck = netcheck + 1
            if netcheck == 1:
                log_error(f"NVR: No connection to {cam_name} at {cam_ip}")
            if netcheck == 5:
                log_info(f"NVR: Waiting for connection to {cam_name} at {cam_ip}")
            if netcheck == 99:
                netcheck = 4
        time.sleep(60)
    # initialize camera and start recording
    cmd = f"ffmpeg -hide_banner -y -loglevel error -rtsp_transport tcp -use_wallclock_as_timestamps 1 -i \"{rtsp_url}\" -c {codec} -f segment -reset_timestamps 1 -segment_time {interval} -segment_format mkv -segment_atclocktime 1 -strftime 1 {raw_path}/%Y-%m-%dT%H-%M-%S.mkv"
    while not stop_flag.is_set():
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            log_info(f"NVR: Camera {cam_name} initialized.")
            return process
        except subprocess.CalledProcessError as e:
            log_error(f"NVR: Error starting recording: {e.output}")
        except Exception as e:
            log_error(f"NVR: Error starting recording: {e}")

def stop_recording(cam_name):
    with stop_flags_lock:
        if cam_name in stop_flags:
            stop_flags[cam_name].set()
        else:
            log_error(f"NVR: Camera {cam_name} not found in stop_flags.")
