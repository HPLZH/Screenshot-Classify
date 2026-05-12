# 基于 OCR 的屏幕截图分类工具

## 功能简介

借助 OCR 工具识别图片中的文本，然后根据预设的规则依据图片中的文本对图片进行分类，最后依据分类结果将图片移动到不同的目录中

## 依赖项

### [python](https://www.python.org)

3.8+

使用 Microsoft Store 版本时，需要启用 Windows 长路径支持

### 推理引擎（二选一）

#### [PaddlePaddle](https://github.com/paddlepaddle/paddle)

[快速安装指南](https://www.paddlepaddle.org.cn/install/quick)

如果你使用的 Python 版本较高，在安装时可能会遇到以下问题：

```log
Looking in indexes: https://www.paddlepaddle.org.cn/packages/stable/cpu/
ERROR: Could not find a version that satisfies the requirement paddlepaddle==3.3.0 (from versions: none)
ERROR: No matching distribution found for paddlepaddle==3.3.0
```

遇到此问题时，改用 Transformers 即可。

#### [Transformers](https://github.com/huggingface/transformers)

[安装文档](https://huggingface.co/docs/transformers/installation)

[上面那个看不了可以看这个](https://hugging-face.cn/docs/transformers/installation)

使用 Transformers 作为推理引擎时，还需要安装 `torchvision`：

```shell
pip install torchvision
```

#### 推理引擎配置

推理引擎配置在 [`src/ocrClassify.py`](src/ocrClassify.py)：

```python
def _paddleOcrLoad():
    import paddleocr

    r = paddleocr.PaddleOCR(
        # ......
        engine="transformers",  # Line 21
    )
    return r
```

当前配置的推理引擎为 Transformers，使用 PaddlePaddle 请删除/注释对应的行。

### [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)

[快速安装指南](https://paddlepaddle.github.io/PaddleOCR/latest/quick_start.html)

屏幕截图分类只需要基础的 OCR 功能，安装时可以只安装 `paddleocr` 而不是 `paddleocr[all]`。

## 快速开始

1. 安装[依赖项](#依赖项)
2. 将整个仓库 clone 到你的计算机上，然后 cd 到 `src` 目录
3. 编写[分类配置文件](/docs/Classify.md)
4. 设计[目标路径模板](#目标路径模板)
5. 用正确的[命令行参数](#命令行参数)启动 `run.py`
6. 只需等待

### 命令行参数
``` bash
python run.py src_path classify_config dst_path_format [-r] [-f filter] [-d date_format] [-D default_class] [-L logging_level]
```

#### 源目录路径

`src_path` 是存放图片的目录的路径，使用 `-r` 以包含子目录中的文件

#### 后缀筛选器

`filter` 用于根据文件后缀名筛选文件，默认值为 `png|jpg|jpeg|bmp`，格式参照默认值即可

特殊：单独的 `*` 用于关闭筛选（接受所有文件）

#### 分类配置文件

`classify_config` 用于指定[分类配置文件](/docs/Classify.md)的路径

#### 目标路径模板

`dst_path_format` 是目标路径的模板，在模板中 `{0}` 表示文件的修改日期，`{1}` 表示首选分类结果（注：程序中使用 `str.format` 方法进行格式化）

`-d date_format` 用于指定模板中文件修改日期的格式，默认值为 `%F`，效果为 `2025-04-26`（注：程序中使用 `datetime.strftime` 方法进行格式化）

#### 默认分类

`-D default_class` 用于指定默认分类

当图片没有任何分类结果时，将默认分类作为首选分类结果

若不指定默认分类，则当图片没有任何分类结果时，图片不会被移动

#### 日志级别

`-L logging_level` 用于指定日志级别，默认为 `WRANING`

#### 多线程并行

实验性功能，预计未来将删除此功能

## 其他文档

- [分类配置文件](/docs/Classify.md)
- [替换 OCR 工具](/docs/OcrReplace.md)
