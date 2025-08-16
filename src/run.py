import filescan
import filemove
import logging
import classify
import ocrClassify
from typing import Callable
from debug import interactive, println


def execute(
    fn: str,
    classifier: classify.Classifier,
    dst_path_format: str,
    default_class: str,
    date_format: str,
):
    classify_result = ocrClassify.getResult(fn, classifier)
    move_result, newfn = filemove.classifiedMove(
        fn,
        cls=classify_result,
        pathFormat=dst_path_format,
        defaultClass=default_class,
        dateFormat=date_format,
    )
    #interactive(globals(), locals())
    if move_result:
        print("Moved: %s -> %s class=%s" % (fn, newfn, classify_result))
    else:
        print("Not moved: %s class=%s" % (fn, classify_result))
    return move_result


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

    parser.add_argument("--parallel", "-p", action="store_true")
    parser.add_argument("--parallel-threads", "-P", type=int, default=0)

    parser.add_argument("--logging-level", "-L", type=str, default="WARNING")

    args = parser.parse_args()

    logging.getLogger().setLevel(getattr(logging, str(args.logging_level).upper()))
    classifier = ocrClassify.buildClassifier(args.classify_config)
    print("Classes:", *classifier.classes.keys())

    ext_filter = (
        "*"
        if args.filter == "*"
        else tuple("." + fmt for fmt in str(args.filter).split("|"))
    )
    print("Filter:", ext_filter)

    ffilter: Callable[[str], bool] = lambda fn: ext_filter == "*" or fn.endswith(
        ext_filter
    )

    proc = int(args.parallel_threads)
    assert proc >= 0
    parallel = bool(args.parallel) or proc > 1

    success = 0
    failed = 0

    def execw(fn: str):
        return execute(
            fn,
            classifier,
            args.dst_path_format,
            args.default_class,
            args.date_format,
        )

    def ls_callback(fn: str):
        global success, failed
        if ffilter(fn):
            r = execw(fn)
            if r == True:
                success += 1
            elif r == False:
                failed += 1
            return r
        else:
            return None
    try:
        if parallel:
            from concurrent.futures import ThreadPoolExecutor, Future
            from threading import Lock

            logger = logging.getLogger()

            print("Parallel enabled.")
            if proc > 0:
                print("Thread count:", proc)

            with ThreadPoolExecutor(None if proc == 0 else proc) as pool:
                PL = Lock()

                def future_callback(fn: Future[bool]):
                    global success, failed
                    r = False
                    try:
                        r = fn.result()
                    except Exception as ex:
                        r = False
                        logger.exception(ex)
                    finally:
                        with PL:
                            if r == True:
                                success += 1
                            elif r == False:
                                failed += 1

                def ls_callback_parallel(fn: str):
                    if ffilter(fn):
                        pool.submit(execw, fn).add_done_callback(future_callback)

                filescan.listdir(args.src_path, args.recursive, ls_callback_parallel)

        else:
            filescan.listdir(args.src_path, args.recursive, ls_callback)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    except Exception as ex:
        logging.exception(ex)
    finally:
        print("%d file(s) moved. %d file(s) not." % (success, failed))
