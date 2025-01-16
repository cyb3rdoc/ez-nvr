import os
import yaml
import re
import unicodedata
import ipaddress
from utils.logger import log_error

# Read environment variables
CONFIG_FILE = os.environ.get('CONFIG_FILE', '/config/config.yaml')

def sanitize_name(input_value):
    if isinstance(input_value, str):
        # Normalize the string to remove accents
        input_value = unicodedata.normalize('NFKD', input_value).encode('ascii', 'ignore').decode('ascii')
        # Replace any non-alphanumeric characters (including spaces) with underscores
        input_value = re.sub(r'[^a-zA-Z0-9_]', '_', input_value)
        return input_value
    elif isinstance(input_value, (int, float)):
        return str(input_value)
    else:
        return input_value

def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def validate_rtsp(url):
    return url.startswith('rtsp://')

def validate_codec(codec):
    supported_codecs = ['copy', 'libx264', 'h264', 'libx265']
    return codec if codec in supported_codecs else 'copy'

def validate_interval(interval):
    return interval if isinstance(interval, int) and interval > 0 else 300

def validate_store(days):
    return days if isinstance(days, int) and days > 0 else 15

def validate_concate(concate):
    return concate if isinstance(concate, bool) else True

def sanitize_config(config):
    sanitized_config = config.copy()
    sanitized_config["video_store"] = validate_store(config.get("video_store", 15))
    sanitized_config["concatenation"] = validate_concate(config.get("concatenation", True))
    for camera in sanitized_config.get('cameras', []):
        camera['camera_name'] = sanitize_name(camera.get('camera_name', ''))
        if not validate_ip(camera.get('camera_ip', '')):
            log_error(f"Invalid IP address for camera: {camera.get('camera_name', '')}")
        if not validate_rtsp(camera.get('camera_rtsp', '')):
            log_error(f"Invalid RTSP URL for camera: {camera.get('camera_name', '')}")
        camera['camera_codec'] = validate_codec(camera.get('camera_codec', 'copy'))
        camera['camera_interval'] = validate_interval(camera.get('camera_interval', 300))
    return sanitized_config

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            log_error(f"NVR: Error loading configuration: {e}")
            return None
    sanitized_config = sanitize_config(config)
    return sanitized_config
