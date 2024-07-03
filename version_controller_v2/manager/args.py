import argparse
import os

def readArguments():
    """
    Read all command line arguments
    """

    parser = argparse.ArgumentParser(description="parse arguments to version controller")
    parser.add_argument(
        "--dir",
        "-d",
        required=False,
        type=str,
        help="the directory where the project is going to be instantiated"
    )

    args = parser.parse_args()

    if args.dir is None:
        args.dir = os.getcwd()

    return args
