import os
import yaml
import re
import unicodedata
from utils.logger import log_error

# read environment variables
CONFIG_FILE = os.environ.get('CONFIG_FILE', '/config/config.yaml')


def sanitize_input(input_value):
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


def sanitize_config(config):
    sanitized_config = config.copy()
    for camera_config in sanitized_config.get('cameras', []):
        # Sanitize user inputs in camera configurations
        camera_config['camera_name'] = sanitize_input(camera_config.get('camera_name', ''))
        camera_config['camera_ip'] = sanitize_input(camera_config.get('camera_ip', ''))
        camera_config['camera_rtsp'] = sanitize_input(camera_config.get('camera_rtsp', ''))
        camera_config['camera_codec'] = sanitize_input(camera_config.get('camera_codec', ''))
        camera_config['camera_interval'] = sanitize_input(camera_config.get('camera_interval', ''))
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
