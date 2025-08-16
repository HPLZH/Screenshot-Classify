import re
from typing import TypeVar, Iterable
from debug import interactive

_T = TypeVar("_T", int, float)

type Pos[_T] = tuple[_T, _T]
type Rect[_T] = tuple[_T, _T, _T, _T]
type OcrItem = tuple[Rect[int | float], str, float]
type OcrRange = tuple[str, Rect[int | float]]


def isSorted(*values: _T, desc: bool = False):
    cmp = (lambda a, b: a >= b) if desc else (lambda a, b: a <= b)
    for i in range(1, len(values)):
        if not cmp(values[i - 1], values[i]):
            return False
    return True


def pointsToRect(point0: Pos[_T], *points: Pos[_T]) -> Rect[_T]:
    xmin, ymin = point0
    xmax, ymax = point0
    for x, y in points:
        xmin = min(xmin, x)
        ymin = min(ymin, y)
        xmax = max(xmax, x)
        ymax = max(ymax, x)
    return (xmin, ymin, xmax, ymax)


def correctRect(rect: Rect[_T]) -> Rect[_T]:
    x1, y1, x2, y2 = rect
    return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))


def pointInRect(point: Pos[int | float], rect: Rect[int | float]):
    x, y = point
    x1, y1, x2, y2 = correctRect(rect)
    return isSorted(x1, x, x2) and isSorted(y1, y, y2)


def rectInRect(rect: Rect[int | float], bound: Rect[int | float]):
    x1, y1, x2, y2 = rect
    return pointInRect((x1, y1), bound) and pointInRect((x2, y2), bound)


def absPos(point: Pos[_T], rect: tuple[int, int], type: str) -> Pos[_T]:
    if type == "relative":
        return absPos((point[0] * rect[0], point[1] * rect[1]), rect, "px")
    elif type == "px":
        return (
            point[0] % rect[0] if point[0] < 0 else point[0],
            point[1] % rect[1] if point[1] < 0 else point[1],
        )
    else:
        raise Exception()


def absRect(rect: Rect[_T], rect1: tuple[int, int], type: str) -> Rect[_T]:
    mp0 = absPos(rect[0:2], rect1, type)
    mp1 = absPos(rect[2:4], rect1, type)
    return correctRect(mp0 + mp1)


def posMap(
    point: Pos[_T],
    from_ltpos: Pos[int],
    to_ltpos: Pos[int] = (0, 0),
) -> Pos[_T]:
    return (
        point[0] + from_ltpos[0] - to_ltpos[0],
        point[1] + from_ltpos[1] - to_ltpos[1],
    )


def rectMap(
    rect: Rect[_T], from_ltpos: Pos[int], to_ltpos: Pos[int] = (0, 0)
) -> Rect[_T]:
    mp0 = posMap(rect[0:2], from_ltpos, to_ltpos)
    mp1 = posMap(rect[2:4], from_ltpos, to_ltpos)
    return correctRect(mp0 + mp1)


class ClassifyRule:
    name = ""
    value = 0
    accept = 0.9
    rect: OcrRange = ("relative", (0.0, 0.0, 1.0, 1.0))
    pattern: re.Pattern = re.compile("")

    def __init__(self):
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
    ocrRange: list[OcrRange] = []

    def _load_1_0_(self, data: dict):
        content = data["content"]
        if "ocr_range" in data:
            ocrange = data["ocr_range"]
            for rg in ocrange:
                rga = rg["range"]
                self.ocrRange.append((rg["type"], tuple(rga[0:4])))
        for cl in content:
            self.classes[cl] = content[cl]["min_value"]
            for rule in content[cl]["rules"]:
                rc: ClassifyRule = ClassifyRule()
                rc.name = cl
                rc.value = rule["value"]
                if "accept" in rule:
                    rc.accept = rule["accept"]
                if "rect" in rule:
                    rrtype = rule["rect"]["type"]
                    rrrect = rule["rect"]["range"]
                    rc.rect = (rrtype, tuple(rrrect[0:4]))
                rc.pattern = re.compile(rule["pattern"])
                self.rules.append(rc)
                pass
        pass

    def __init__(self, data: dict):
        self.classes = {}
        self.rules = []
        self.ocrRange = []

        version = "1.0"
        loaders = {"1.0": self._load_1_0_}
        if "version" in data and data["version"] in loaders:
            version = data["version"]
        loaders[version](data)
        pass

    def _classify_data(
        self,
        ocrResult: Iterable[OcrItem] | None,
        imgSize: tuple[int, int],
        ltpos: tuple[int, int] = (0, 0),
        score: dict | None = None,
    ):
        if score == None:
            score = {}

        if ocrResult == None:
            return score

        for rect, text, rel in ocrResult:
            gRect = rectMap(rect, ltpos)
            #interactive(globals(), locals())
            for rule in self.rules:
                if rel < rule.accept:
                    continue
                rectc = absRect(rule.rect[1], imgSize, rule.rect[0])
                #interactive(globals(), locals())
                if rectInRect(gRect, rectc):
                    mcount = len(rule.pattern.findall(text))
                    if mcount > 0:
                        if not rule.name in score:
                            score[rule.name] = 0
                        score[rule.name] += mcount * rule.value
                    pass
            pass

        return score

    def classify(
        self,
        ocrResult: Iterable[OcrItem],
        imgSize: tuple[int, int],
        ltpos: Pos[int] = (0, 0),
    ):
        sc = self._classify_data(ocrResult, imgSize, ltpos)
        ret = []
        for name in sc:
            if sc[name] >= self.classes[name]:
                ret.append(name)
        ret.sort(key=lambda n: sc[n] / self.classes[n], reverse=True)
        return ret

    def multiRectClassify(
        self,
        ocrResultList: Iterable[tuple[Iterable[OcrItem], Pos[int]]],
        imgSize: tuple[int, int],
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
