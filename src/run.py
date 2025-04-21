if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("src_path", type=str)
    parser.add_argument("--recursive", "-r", action="store_true")

    parser.add_argument("classify_config", type=str)
    parser.add_argument("--filter", type=str, default="png|jpg|jpeg|bmp")

    parser.add_argument("dst_path_format", type=str)
    parser.add_argument("--date-format", "-d", type=str, default="%F")
    parser.add_argument("--default-class", "-D", type=str, default="")

    parser.add_argument("--logging-level", "-L", type=str, default="WARNING")

    args = parser.parse_args()

    import filescan
    import filemove
    import ocrClassify
    import logging

    logging.getLogger().setLevel(getattr(logging, str(args.logging_level).upper()))
    classifier = ocrClassify.buildClassifier(args.classify_config)
    ext_filter = (
        "*"
        if args.filter == "*"
        else tuple("." + fmt for fmt in str(args.filter).split("|"))
    )

    success = 0
    failed = 0

    def ls_callback(fn: str):
        global success, failed
        if ext_filter == "*" or fn.endswith(ext_filter):
            classify_result = ocrClassify.getResult(fn, classifier)
            move_result, newfn = filemove.classifiedMove(
                fn,
                cls=classify_result,
                pathFormat=args.dst_path_format,
                defaultClass=args.default_class,
                dateFormat=args.date_format,
            )
            if move_result:
                print("Moved: %s -> %s class=%s" % (fn, newfn, classify_result))
                success += 1
            else:
                print("Not moved: %s class=%s" % (fn, classify_result))
                failed += 1
            return move_result
        else:
            return False

    filescan.listdir(args.src_path, args.recursive, ls_callback)
    print("%d file(s) moved. %d file(s) not." % (success, failed))
