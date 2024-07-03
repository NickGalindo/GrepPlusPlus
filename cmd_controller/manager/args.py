import argparse

def readArguments():
    """
    Read all command line arguments
    """

    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Grep++ commandline utility")
    subparsers: argparse.Action = parser.add_subparsers(dest="command")

    parser_find: argparse.ArgumentParser = subparsers.add_parser("find", help="finding at it's finest")
    __build_parser_find(parser_find)

    args = vars(parser.parse_args())

    return args

def __build_parser_find(parser_find: argparse.ArgumentParser) -> None:
    parser_find.add_argument(
        "find_str",
        type=str,
        help="string to search for"
    )

    parser_find.add_argument(
        "--number",
        "-n",
        type=int,
        default=5,
        help="number of results to return default is 5"
    )

    parser_find.add_argument(
        "--project",
        "-p",
        required=False,
        type=str,
        help="search for the string only within a specific project (if the project hasn't been indexed by grep++ recently results may be outdated)"
    )
    parser_find.add_argument(
        "--all",
        "-a",
        required=False,
        action="store_true",
        help="show everything that grep++ has indexed, find string will be ignored (may be outdated if projects haven't been recently indexed by grep++)"
    )
