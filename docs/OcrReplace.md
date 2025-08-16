# 替换 OCR 工具

本项目使用 PaddleOCR，若要更换 OCR 工具，可以参考本指南

## OCR 结果格式

OCR 结果需要转换为统一的格式：

```python
type Rect[_T] = tuple[_T, _T, _T, _T]
type OcrItem = tuple[Rect[int | float], str, float]

def ocr_func(img) -> Iterable[OcrItem]: ...

```

若要替换 OCR 工具，需要把输出转换为正确的格式

若无相关输出，可靠程度可以使用 `1.0` 代替

## 代码修改指南

### 移除 PaddleOCR 加载

从 `ocrClassify.py` 删除以下代码行

```python
def _paddleOcrLoad():
    ...

ocr = MultiThread(_paddleOcrLoad)
```

同时，你需要引入你使用的 OCR 库

### 改写 OCR 方法

`ocrClassify.py` 中使用 `ocr_func(img)` 方法包装具体的 OCR 方法，改写这个方法使其调用你指定的 OCR 工具并返回正确格式的结果

此方法只接受一个参数，参数类型为 `str` 或 `NDArray`，类型为 `str` 时表示文件路径

### 调试

调试你的程序，确保其能正常工作
