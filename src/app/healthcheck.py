#!/usr/bin/env python

import subprocess
import os


def process_state(process_name):
    try:
        output = subprocess.check_output(["pgrep", process_name])
        return len(output.strip()) > 0
    except subprocess.CalledProcessError:
        return False


def nvr_health():
    health_state = os.environ.get('HEALTH_STATE', 'false')
    if health_state.lower() == 'false':
        return False
    else:
        return True


def main():
    nvr_process = process_state("python")
    ffmpeg_process = process_state("ffmpeg")
    if nvr_process and ffmpeg_process and nvr_health():
        return "OK"
    else:
        return "ERROR"


if __name__ == "__main__":
    main()
