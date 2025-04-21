import os


def listdir(path: str, recursive: bool, callback=print):

    files = os.listdir(path)
    for file in files:
        file_path = os.path.join(path, file)

        if os.path.isfile(file_path):
            callback(os.path.join(path, file))

        elif recursive and os.path.isdir(file_path):
            listdir(file_path, recursive, callback)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--recursive", "-r", action="store_true")
    parser.add_argument("path", type=str)
    args = parser.parse_args()
    listdir(args.path, args.recursive)
    pass
