#!/usr/bin/env python

import subprocess
import os

def process_health():
    cmd_nvr = "ps aux | grep 'nvr.py' | grep -v grep"
    cmd_ffmpeg = "ps aux | grep 'ffmpeg' | grep -v grep"
    try:
        output_nvr = subprocess.check_output(cmd_nvr, shell=True)
        output_ffmpeg = subprocess.check_output(cmd_ffmpeg, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def nvr_health():
    health_state = os.environ.get('HEALTH_STATE', 'false')
    if health_state.lower() == 'true':
        return True
    else:
        return False

def main():
    if process_health() and nvr_health():
        return "OK"
    else:
        return "ERROR"

if __name__ == "__main__":
    main()
