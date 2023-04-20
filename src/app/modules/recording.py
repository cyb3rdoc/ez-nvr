import os
import time
import logging
import subprocess
import signal
from utils.filesystem import get_output_path, get_raw_path, mkdir_dest, mkdir_raw

def start_recording(cam_config):
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

    while True:
        response = os.system("ping -c 1 " + cam_ip)
        if response == 0:
            cmd = f"ffmpeg -hide_banner -y -loglevel error -rtsp_transport tcp -use_wallclock_as_timestamps 1 -i {rtsp_url} -c {codec} -f segment -reset_timestamps 1 -segment_time {interval} -segment_format mkv -segment_atclocktime 1 -strftime 1 {raw_path}/%Y-%m-%dT%H-%M-%S.mkv"
            try:
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                logging.info(f"NVR: Camera {cam_name} initialized.")
                break
            except subprocess.CalledProcessError as e:
                logging.error(f"NVR: Error starting recording: {e.output}")
            except Exception as e:
                logging.error(f"NVR: Error starting recording: {e}")
        else:
            netcheck = netcheck + 1
            if netcheck == 1:
                logging.error(f"NVR: No network connection to {cam_name} at {cam_ip}")
            if netcheck == 5:
                logging.info(f"NVR: Waiting for network connection to {cam_name} at {cam_ip}")
            if netcheck == 99:
                netcheck = 5
        time.sleep(60)
    return process

def stop_recording(process):
    process.send_signal(signal.SIGINT)
    process.wait()
