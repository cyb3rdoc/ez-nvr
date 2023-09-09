import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="enable debug logging", action="store_true")
    return parser.parse_args()
