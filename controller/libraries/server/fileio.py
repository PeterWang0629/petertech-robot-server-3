# Supporting Library
# File I/O Control Library for monitoring and limiting file I/O Operations.
# Also for preventing I/O conflicts during handling high traffic.
import threading
import time, sys


class FileIO:
    def __init__(self):
        sys.__stdout__.write(f"[DEV {time.strftime('%Y-%m-%d %H:%M:%S')}] Fileio created\n")
        self.__files = {}
        self.__modify = {}
        self.__running = False

    def register_file_(self, filename: str, read_type: str) -> None:
        if filename in self.__files:
            return
        with open(filename, "r" + read_type) as f:
            content = f.read()
        self.__files[filename] = {"content": content, "read_type": read_type}

    def register_file(self, files: list | tuple) -> None:
        for file in files:
            self.register_file_(file[0], file[1])

    def remove_file(self, filename: str) -> None:
        self.__files.pop(filename)

    def read(self, filename: str) -> bytes | str:
        return self.__files[filename]["content"]

    def write(self, filename : str, content : str | bytes) -> None:
        self.__files[filename]["content"] = content
        self.__modify[filename] = content

    def __task(self):
        while self.__running:
            if len(self.__files):
                for filename in self.__files:
                    if filename not in self.__modify:
                        with open(filename, "r" + self.__files[filename]["read_type"]) as f:
                            self.__files[filename]["content"] = f.read()
            if len(self.__modify):
                for filename in self.__modify:
                    with open(filename, "w" + self.__files[filename]["read_type"]) as f:
                        f.write(self.__modify[filename])
                self.__modify = {}

            time.sleep(5)

    def run(self) -> None:
        self.__running = True
        threading.Thread(target=self.__task).start()

    def terminate(self) -> None:
        self.__running = False
