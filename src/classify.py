import re


def pointInRect(
    point: tuple[int | float, int | float], rect: list[tuple[int | float, int | float]]
):
    return (
        point[0] >= rect[0][0]
        and point[1] >= rect[0][1]
        and point[0] <= rect[1][0]
        and point[1] <= rect[1][1]
    )


def absPos(point: tuple[int | float, int | float], rect: tuple[int, int], type: str):
    if type == "relative":
        return absPos((point[0] * rect[0], point[1] * rect[1]), rect, "px")
    elif type == "px":
        return (
            point[0] % rect[0] if point[0] < 0 else point[0],
            point[1] % rect[1] if point[1] < 0 else point[1],
        )
    else:
        raise Exception()


def posMap(
    point: tuple[float, float],
    from_ltpos: tuple[int, int],
    to_ltpos: tuple[int, int] = (0, 0),
):
    return (
        point[0] + from_ltpos[0] - to_ltpos[0],
        point[1] + from_ltpos[1] - to_ltpos[1],
    )


def isOcrResultList(data: list):
    try:
        ocr = data[0]
        rect = ocr[0]
        text = ocr[1][0]
        rel = ocr[1][1]
        return (
            isinstance(rect, list)
            and len(rect) == 4
            and isinstance(text, str)
            and isinstance(rel, float)
        )
    except:
        return False


class ClassifyRule:
    name = ""
    value = 0
    accept = 0.9
    rect = ["relative", (0.0, 0.0), (1.0, 1.0)]
    pattern: re.Pattern = ""

    def __init__(self):
        self.rect = self.rect[:]
        pass

    def __repr__(self):
        return (
            'ClassifyRule{name="%s", value="%s", accept="%s", rect="%s", pattern="%s"}'
            % (
                self.name,
                self.value,
                self.accept,
                repr(self.rect),
                self.pattern.pattern,
            )
        )


class Classifier:

    classes = {}
    rules: list[ClassifyRule] = []
    ocrRange = []

    def _load_1_0_(self, data: dict):
        content = data["content"]
        if "ocr_range" in data:
            ocrange = data["ocr_range"]
            for rg in ocrange:
                rga = rg["range"]
                self.ocrRange.append([rg["type"], tuple(rga[0:2]), tuple(rga[2:4])])
        for cl in content:
            self.classes[cl] = content[cl]["min_value"]
            for rule in content[cl]["rules"]:
                rc: ClassifyRule = ClassifyRule()
                rc.name = cl
                rc.value = rule["value"]
                if "accept" in rule:
                    rc.accept = rule["accept"]
                if "rect" in rule:
                    rc.rect[0] = rule["rect"]["type"]
                    range = rule["rect"]["range"]
                    rc.rect[1] = (range[0], range[1])
                    rc.rect[2] = (range[2], range[3])
                rc.pattern = re.compile(rule["pattern"])
                self.rules.append(rc)
                pass
        pass

    def __init__(self, data: dict):
        version = "1.0"
        loaders = {"1.0": self._load_1_0_}
        if "version" in data and data["version"] in loaders:
            version = data["version"]
        loaders[version](data)
        pass

    def _classify_data(
        self,
        ocrResult: list,
        imgSize: tuple[int, int],
        ltpos: tuple[int, int] = (0, 0),
        score: dict = None,
    ):
        if score == None:
            score = {}

        if ocrResult == None or len(ocrResult) == 0:
            return score
        
        ocrResultCpy = []
        list(map(ocrResultCpy.extend, filter(None, ocrResult)))

        for ocr in ocrResultCpy:
            rect = ocr[0]
            text = ocr[1][0]
            rel = ocr[1][1]

            for rule in self.rules:
                if rel < rule.accept:
                    continue
                rectc = [absPos(p, imgSize, rule.rect[0]) for p in rule.rect[1:3]]
                for p in rect:
                    if not pointInRect(posMap(p, ltpos), rectc):
                        break
                else:
                    mcount = len(rule.pattern.findall(text))
                    if mcount > 0:
                        if not rule.name in score:
                            score[rule.name] = 0
                        score[rule.name] += mcount * rule.value
                    pass
            pass

        return score

    def classify(
        self, ocrResult: list, imgSize: tuple[int, int], ltpos: tuple[int, int] = (0, 0)
    ):
        sc = self._classify_data(ocrResult, imgSize, ltpos)
        ret = []
        for name in sc:
            if sc[name] >= self.classes[name]:
                ret.append(name)
        ret.sort(key=lambda n: sc[n] / self.classes[n], reverse=True)
        return ret

    def multiRectClassify(
        self, ocrResultList: list[list, tuple[int, int]], imgSize: tuple[int, int]
    ):
        sc = {}
        for result, ltpos in ocrResultList:
            sc = self._classify_data(result, imgSize, ltpos, sc)
        pass
        ret = []
        for name in sc:
            if sc[name] >= self.classes[name]:
                ret.append(name)
        ret.sort(key=lambda n: sc[n] / self.classes[n], reverse=True)
        return ret

    pass
