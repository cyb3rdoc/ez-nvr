#!/usr/bin/env python

import subprocess

def check_nvr_process():
    cmd = "ps aux | grep 'nvr.py' | grep -v grep"
    try:
        output = subprocess.check_output(cmd, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    if check_nvr_process():
        return "OK"
    else:
        return "ERROR"

if __name__ == "__main__":
    main()
