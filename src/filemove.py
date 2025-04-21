import datetime
import shutil
import os
import logging


def classifiedMove(
    fn: str, cls: list[str], pathFormat: str, defaultClass="", dateFormat: str = "%F"
):
    t = datetime.datetime.fromtimestamp(os.path.getmtime(fn)).strftime(dateFormat)
    target = pathFormat.format(t, defaultClass if len(cls) == 0 else cls[0])
    tgf = os.path.join(target, os.path.basename(fn))
    if len(cls) == 0 and defaultClass == "":
        logging.info("Cannot match any class: %s", fn)
        return False, fn
    if not os.path.exists(target):
        os.mkdir(target)
    if not os.path.exists(tgf):
        shutil.move(fn, target)
        logging.info("Moved: %s -> %s", fn, tgf)
        return True, tgf
    elif os.path.abspath(tgf) == os.path.abspath(
        fn
    ):
        logging.info(
            "Skipped: %s -> %s (same)",
            fn,
            tgf,
        )
        return False, fn
    else:
        logging.warning(
            "Move failed: %s -> %s (exist)",
            fn,
            tgf,
        )
        return False, fn


def classifiedMoveDict(
    data: dict, pathFormat: str, defaultClass="", dateFormat: str = "%F"
):
    success = 0
    fail = 0
    for fn in data:
        if classifiedMove(
            fn,
            data[fn],
            pathFormat=pathFormat,
            defaultClass=defaultClass,
            dateFormat=dateFormat,
        )[0]:
            success += 1
        else:
            fail += 1
    return success, fail


if __name__ == "__main__":
    import argparse
    import sys
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("path_format", type=str)
    parser.add_argument("--date-format", "-d", type=str, default="%F")
    parser.add_argument("--default-class", "-D", type=str, default="")
    parser.add_argument("--python-input", "-py", action="store_true")
    parser.add_argument("--single-line-input", "-1", action="store_true")
    parser.add_argument("--file", "-f", type=str, default="-")
    parser.add_argument("--encoding", type=str, default="utf-8")
    parser.add_argument("--logging-level", "-L", type=str, default="WARNING")
    args = parser.parse_args()
    logging.getLogger().setLevel(getattr(logging, str(args.logging_level).upper()))
    instream = sys.stdin if args.file == "-" else open(args.file, "r", args.encoding)

    if args.single_line_input:
        ln = instream.readline()
        while len(ln) > 0:
            data = {}
            if args.python_input:
                data = eval(ln)
            else:
                data = json.loads(ln)
            success, fail = classifiedMoveDict(
                data,
                pathFormat=args.path_format,
                defaultClass=args.default_class,
                dateFormat=args.date_format,
            )
            sys.stderr.write("%d file(s) moved, %d file(s) not.\n" % (success, fail))
            sys.stderr.flush()
            ln = instream.readline()
    else:
        data = {}
        if args.python_input:
            data = eval(instream.read())
        else:
            data = json.load(instream)
        success, fail = classifiedMoveDict(
            data,
            pathFormat=args.path_format,
            defaultClass=args.default_class,
            dateFormat=args.date_format,
        )
        sys.stderr.write("%d file(s) moved, %d file(s) not.\n" % (success, fail))
    instream.close()
