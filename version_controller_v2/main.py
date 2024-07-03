from manager.args import readArguments

import time
from watchdog.observers import Observer

from file_handler.version_control_handler import VersionControlHandler

import colorama

import atexit

def main():
    colorama.init(autoreset=True)

    args = readArguments()

    event_handler = VersionControlHandler(args.dir, verbose=True)

    atexit.register(event_handler.handle_exit)
    
    observer = Observer()
    observer.schedule(event_handler, args.dir, recursive=True)
    observer.start()
    print(f"Monitoring Directory: {args.dir}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

    return

if __name__ == '__main__':
    main()
