# 替换 OCR 工具

本项目使用 PaddleOCR，若要更换 OCR 工具，可以参考本指南

## OCR 结果格式

分类模块接受 PaddleOCR 的文本检测+文本识别输出，格式如下：

```python
[
    [
        [
            # 文本检测结果，矩形的4个顶点坐标
            [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
            # 文本识别结果，识别出的文本与可靠程度
            [("text", 1.0)]
        ],
        [
            [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
            [("text", 1.0)]
        ],
        "..."
    ],
    "..."
]
```

若要替换 OCR 工具，需要把输出转换为此格式

若无相关输出，矩形坐标可以使用空列表以跳过文本位置检测，可靠程度可以使用 `1.0` 代替

## 代码修改指南

### 移除 PaddleOCR 加载

从 `ocrClassify.py` 删除以下代码行

```python
from paddleocr import PaddleOCR
logging.getLogger("ppocr").setLevel(logging.WARNING)
ocr = PaddleOCR()
```

同时，你需要引入你使用的 OCR 库

### 改写 OCR 方法

`ocrClassify.py` 中使用 `ocr_func(img)` 方法包装具体的 OCR 方法，改写这个方法使其调用你指定的 OCR 工具并返回正确格式的结果

此方法只接受一个参数，参数类型为 `str` 或 `NDArray`，类型为 `str` 时表示文件路径

### 调试

调试你的程序，确保其能正常工作
