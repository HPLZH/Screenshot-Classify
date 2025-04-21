if __name__ == "__main__":
    import sys
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="gbk")
    sys.stdout.write(sys.stdin.read())
