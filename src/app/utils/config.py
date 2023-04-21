import os
import yaml

# read environment variables
CONFIG_FILE = os.environ.get('CONFIG_FILE', '/config/config.yaml')

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logging.error(f"NVR: Error loading configuration: {e}")
            return None
    return config
