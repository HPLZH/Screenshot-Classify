# 基于 OCR 的屏幕截图分类工具

## 功能简介

借助 OCR 工具识别图片中的文本，然后根据预设的规则依据图片中的文本对图片进行分类，最后依据分类结果将图片移动到不同的目录中

## 依赖项

### [python](https://www.python.org)

3.8+

使用 Microsoft Store 版本时，需要启用 Windows 长路径支持

### [PaddlePaddle](https://github.com/paddlepaddle/paddle)

[快速安装指南](https://www.paddlepaddle.org.cn/install/quick)

本项目使用 PaddleOCR，需要安装 PaddlePaddle

### [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)

[快速安装指南](https://paddlepaddle.github.io/PaddleOCR/latest/quick_start.html)

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

## 其他文档

- [分类配置文件](/docs/Classify.md)
- [替换 OCR 工具](/docs/OcrReplace.md)
