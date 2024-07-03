from manager.args import readArguments
import colorama

import atexit

def main():
    colorama.init(autoreset=True)
    args = readArguments()

    if args["command"] == "find":
        from find import find # Lazy import to avoid slowness

        if args["all"]:
            find.findAll()
        elif args["project"]:
            find.projectFind(args["find_str"], args["number"], args["project"])
        else:
            find.baseFind(args["find_str"], args["number"])

    return

if __name__ == '__main__':
    main()
