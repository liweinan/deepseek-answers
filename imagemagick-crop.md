# 使用ImageMagick对图片进行剪裁 

要将一张图片剪裁为 150 x 150 像素（px），可以使用 ImageMagick 的 `convert` 或 `magick` 命令（取决于你的 ImageMagick 版本）。以下是具体指令：

### 1. **基本剪裁（居中剪裁）**
```bash
convert input.jpg -resize 150x150^ -gravity center -extent 150x150 output.jpg
```
或（ImageMagick 7+）：
```bash
magick input.jpg -resize 150x150^ -gravity center -extent 150x150 output.jpg
```
#### 参数说明：
- `-resize 150x150^`：将图片按比例缩放，至少一边为 150px（`^` 表示填充整个区域）。
- `-gravity center`：设置剪裁的中心对齐。
- `-extent 150x150`：最终剪裁为 150x150 像素。

---

### 2. **直接剪裁（不缩放，从左上角开始）**
如果只想剪裁原图的左上角 150x150 区域（不调整比例）：
```bash
convert input.jpg -crop 150x150+0+0 output.jpg
```
或：
```bash
magick input.jpg -crop 150x150+0+0 output.jpg
```
#### 参数说明：
- `-crop 150x150+0+0`：从坐标 `(0,0)` 开始剪裁 150x150 区域。

---

### 3. **按比例缩放后剪裁**
如果希望先缩放图片，使短边匹配 150px，然后剪裁长边（保持比例）：
```bash
convert input.jpg -resize 150x150^ -gravity center -extent 150x150 output.jpg
```
（与第一种方法相同，这是最常用的方式。）

---

### 注意事项：
- 替换 `input.jpg` 为你的输入文件，`output.jpg` 为输出文件名。
- 支持所有常见格式（如 PNG、JPG、GIF 等）。
- 如果图片已经是正方形，可以直接用 `-resize 150x150`。

如果需要进一步调整（如背景填充），可以添加 `-background` 参数。例如，填充白色背景：
```bash
convert input.jpg -resize 150x150 -background white -gravity center -extent 150x150 output.jpg
```

希望这对你有帮助！