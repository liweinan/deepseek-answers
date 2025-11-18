# Using ImageMagick to Crop Images

To crop an image to 150 x 150 pixels (px), you can use ImageMagick's `convert` or `magick` command (depending on your ImageMagick version). Here are the specific commands:

### 1. **Basic Crop (Center Crop)**
```bash
convert input.jpg -resize 150x150^ -gravity center -extent 150x150 output.jpg
```
Or (ImageMagick 7+):
```bash
magick input.jpg -resize 150x150^ -gravity center -extent 150x150 output.jpg
```
#### Parameter Explanation:
- `-resize 150x150^`: Scale the image proportionally, with at least one side being 150px (`^` means fill the entire area).
- `-gravity center`: Set center alignment for cropping.
- `-extent 150x150`: Final crop to 150x150 pixels.

---

### 2. **Direct Crop (No Scaling, From Top-left)**
If you only want to crop the top-left 150x150 area of the original image (without adjusting proportions):
```bash
convert input.jpg -crop 150x150+0+0 output.jpg
```
Or:
```bash
magick input.jpg -crop 150x150+0+0 output.jpg
```
#### Parameter Explanation:
- `-crop 150x150+0+0`: Crop a 150x150 area starting from coordinates `(0,0)`.

---

### 3. **Scale Proportionally Then Crop**
If you want to first scale the image so the shorter side matches 150px, then crop the longer side (maintaining proportions):
```bash
convert input.jpg -resize 150x150^ -gravity center -extent 150x150 output.jpg
```
(Same as the first method, this is the most commonly used approach.)

---

### Notes:
- Replace `input.jpg` with your input file, `output.jpg` with the output filename.
- Supports all common formats (such as PNG, JPG, GIF, etc.).
- If the image is already square, you can directly use `-resize 150x150`.

If you need further adjustments (like background fill), you can add the `-background` parameter. For example, to fill with white background:
```bash
convert input.jpg -resize 150x150 -background white -gravity center -extent 150x150 output.jpg
```

Hope this helps!