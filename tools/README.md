# WMF转PNG工具（支持自动裁剪，带耗时统计）
```text
用法: WmfToPngTool.exe <wmf文件> [选项]
选项:
  -dpi <数值>     输出DPI（默认300）
  -crop          自动裁剪空白部分
  -tolerance <数值>  裁剪容差（0-255，默认10）
  -transparent      保持透明背景
  -o <输出路径>    指定输出文件路径
  -fastcrop          使用快速不安全模式裁剪（性能极高，需信任输入文件）
示例:
  WmfToPngTool.exe input.wmf
  WmfToPngTool.exe input.wmf -dpi 300 -crop
  WmfToPngTool.exe input.wmf -crop -tolerance 20 -o output.png
  WmfToPngTool.exe input.wmf -transparent -crop
  WmfToPngTool.exe input.wmf -dpi 600 -transparent -fastcrop
```

# 用法: EmfToPngTool.exe <emf文件> [选项]
```text
选项:
  -dpi <数值>        输出DPI（默认300）
  -crop             自动裁剪空白部分
  -tolerance <数值>   裁剪容差（0-255，默认10）
  -transparent      保持透明背景
  -o <输出路径>       指定输出文件路径
  -fastcrop          使用快速不安全模式裁剪（性能极高，需信任输入文件）
示例:
  EmfToPngTool.exe input.emf
  EmfToPngTool.exe input.emf -dpi 300 -crop
  EmfToPngTool.exe input.emf -crop -tolerance 20 -o output.png
  EmfToPngTool.exe input.emf -transparent -crop
```
