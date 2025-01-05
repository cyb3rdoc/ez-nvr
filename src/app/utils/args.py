import os
import argparse

def get_args():
    # First check environment variable, default to False
    debug_env = os.environ.get('DEBUG', '').lower() in ('true', '1', 'yes')

    # Then check command line args (allows override)
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug",
                       help="enable debug logging",
                       action="store_true",
                       default=False)

    # If environment variable is True, override the default
    if debug_env:
        parser.set_defaults(debug=True)

    return parser.parse_args()
