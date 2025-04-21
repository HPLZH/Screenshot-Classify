from classify import Classifier, absPos
from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
import json
import logging

logging.getLogger("ppocr").setLevel(logging.WARNING)

ocr = PaddleOCR()

def printr(obj, **kwargs):
    print(obj, **kwargs)
    return obj

def ocr_func(img):
    return (ocr.ocr(img=img, cls=False))


def buildClassifier(config: str):
    with open(config, "r", encoding="utf-8") as f:
        return Classifier(json.load(f))


def getResult(img: str, classifier: Classifier):
    with Image.open(img) as imgobj:
        size = imgobj.size
        if len(classifier.ocrRange) == 0:
            return classifier.classify(ocr_func(img), size)
        else:
            data = []
            for ocrg in classifier.ocrRange:
                pos1 = absPos(ocrg[1], size, ocrg[0])
                pos2 = absPos(ocrg[2], size, ocrg[0])
                box = list(int(x) for x in pos1 + pos2)
                box = tuple(
                    box[i] if box[i] <= size[i % 2] else size[i % 2] for i in range(4)
                )
                cropimg = imgobj.crop(box).convert("RGB")
                ocrr = ocr_func(np.array(cropimg))
                data.append((ocrr, pos1))
                pass
            return classifier.multiRectClassify(data, size)


def getSingleResult(img: str, classifier: Classifier):
    return [img, getResult(img, classifier)]


def getListResult(imgs: list[str], classifier: Classifier):
    ret = {}
    for img in imgs:
        if not img in ret:
            ret[img] = getResult(img, classifier)
    return ret


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("classify_config", type=str)
    parser.add_argument("--filter", type=str, default="png|jpg|jpeg|bmp")
    parser.add_argument("--python-output", "-py", action="store_true")
    parser.add_argument("--wait", "-w", action="store_true")
    parser.add_argument("--file", "-f", type=str, default="-")
    parser.add_argument("--encoding", type=str, default="utf-8")
    parser.add_argument("--logging-level", "-L", type=str, default="WARNING")
    args = parser.parse_args()
    logging.getLogger().setLevel(getattr(logging, str(args.logging_level).upper()))
    instream = sys.stdin if args.file == "-" else open(args.file, "r", args.encoding)
    cls = buildClassifier(args.classify_config)
    flt = (
        "*"
        if args.filter == "*"
        else tuple("." + fmt for fmt in str(args.filter).split("|"))
    )
    inputs = []
    fn = instream.readline()
    while len(fn) > 0:
        fn = fn.strip()
        logging.debug("Input: %s", fn)
        if flt == "*" or fn.endswith(flt):
            logging.debug("Input accepted: %s", fn)
            if args.wait:
                inputs.append(fn)
            else:
                result = getSingleResult(fn, cls)
                logging.debug("Classify: %s : %s", *result)
                if args.python_output:
                    print(result, flush=True)
                else:
                    result = {result[0]: result[1]}
                    print(json.dumps(result, ensure_ascii=False), flush=True)
            pass
        pass
        sys.stdout.flush()
        fn = instream.readline()
    if args.wait:
        result = getListResult(inputs, cls)
        if args.python_output:
            print(result, flush=True)
        else:
            print(json.dumps(result, ensure_ascii=False), flush=True)

    instream.close()
