# Supporting Library
# Log output library for log storage and printing
import sys
import threading
import time


class Logger:
    def __init__(self, filename: str) -> None:
        sys.__stdout__.write(f"[DEV {time.strftime('%Y-%m-%d %H:%M:%S')}] Logger created\n")
        self.__filename = filename
        self.__cache = []
        self.__running = False

    def __task(self):
        while self.__running:
            if len(self.__cache):
                with open(self.__filename, 'a') as f:
                    f.writelines(self.__cache)
                self.__cache = []
            time.sleep(5)

    def run(self) -> None:
        self.__running = True
        threading.Thread(target=self.__task).start()

    def log(self, type_: str, *args: str) -> None:
        if self.__running:
            content = []
            for arg in args:
                content.append(str(arg))
            content = " ".join(content)
            sys.__stdout__.write(f"[{type_.upper()} {time.strftime('%Y-%m-%d %H:%M:%S')}] {content}\n")
            self.__cache.append(f"[{type_.upper()} {time.strftime('%Y-%m-%d %H:%M:%S')}] {content}\n")
        else:
            raise RuntimeError("Logger is not running but log() has been executed")

    def terminate(self) -> None:
        self.__running = False

    def write(self, string: str) -> None:
        self.log("STDOUT", string)
