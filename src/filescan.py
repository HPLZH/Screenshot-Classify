import os
from ref import Reference
from typing import Callable, Any


def listdir(path: str, recursive: bool, callback: Callable[[str], Any] = print):

    files = os.listdir(path)
    for file in files:
        file_path = os.path.join(path, file)

        if os.path.isfile(file_path):
            callback(os.path.join(path, file))

        elif recursive and os.path.isdir(file_path):
            listdir(file_path, recursive, callback)


def listdirL(path: str, recursive: bool, callback: Callable[[list[str]], Any] = print):

    files = os.listdir(path)
    paths = list(map(lambda s: os.path.join(path, s), files))
    fs = filter(os.path.isfile, paths)
    callback(list(fs))
    dirs = filter(os.path.isdir, paths)
    if recursive:
        for d in dirs:
            listdirL(d, recursive, callback)


def ls(path: str, recursive: bool):
    result: Reference[list[str]] = Reference([])
    listdirL(
        path=path, recursive=recursive, callback=lambda x: result.set(result.value + x)
    )
    return result.value


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--recursive", "-r", action="store_true")
    parser.add_argument("path", type=str)
    args = parser.parse_args()
    listdir(args.path, args.recursive)
    pass
