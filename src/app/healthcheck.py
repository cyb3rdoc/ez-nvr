#!/usr/bin/env python

import subprocess

def eznvr_health():
    cmd_nvr = "ps aux | grep 'nvr.py' | grep -v grep"
    cmd_ffmpeg = "ps aux | grep 'ffmpeg' | grep -v grep"
    try:
        output_nvr = subprocess.check_output(cmd_nvr, shell=True)
        output_ffmpeg = subprocess.check_output(cmd_ffmpeg, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    if eznvr_health():
        return "OK"
    else:
        return "ERROR"

if __name__ == "__main__":
    main()
