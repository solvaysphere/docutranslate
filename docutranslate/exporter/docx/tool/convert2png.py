import sys
from io import BytesIO
from pathlib import Path
import base64
import tempfile
import uuid
import os
import time
import subprocess

def find_development_root():
    """在开发环境中探测项目根目录"""
    # 推荐：使用标识文件
    markers = ['.git', 'requirements.txt', 'pyproject.toml', '.project-root']
    current = os.path.abspath(os.path.dirname(__file__))
    while current != os.path.dirname(current):
        if any(os.path.exists(os.path.join(current, m)) for m in markers):
            return current
        current = os.path.dirname(current)
    return os.path.abspath(".")  # fallback

def get_bundle_root():
    """返回当前环境下的资源根路径"""
    if getattr(sys, 'frozen', False):
        # 打包后：使用 PyInstaller 提供的临时目录
        return sys._MEIPASS
    else:
        # 开发时：用标识文件探测（更健壮）
        return find_development_root()


def convert_wmf_emf_to_png_async(image):
    """单个图片转换函数，用于多进程处理"""
    content_type = image.content_type
    if image.content_type in ["image/wmf", "image/emf", "image/x-wmf", "image/x-emf"]:
        encoded_src = convert_wmf_emf_to_png(image)
        content_type = "image/png"
    else:
        with image.open() as image_bytes:
            encoded_src = base64.b64encode(image_bytes.read()).decode("ascii")
    return content_type, encoded_src

# Wmf 和 Emf 转换 Png 工具
def convert_wmf_emf_to_png(image) -> str:
    # 获取当前文件所在目录
    current_dir = os.path.join(get_bundle_root(), 'tools')
    if image.content_type == "image/wmf" or image.content_type == "image/x-wmf":
        file_ext = '.wmf'
    else:
        file_ext = '.emf'
    unique_id = str(uuid.uuid4())[:8]
    # 1. 读取上传文件到内存 (BytesIO)
    with image.open() as input_bytes:
        input_stream = BytesIO(input_bytes.read())
    # 2. 创建临时文件（必须，供 exe 使用）
    temp_dir = Path(tempfile.gettempdir())
    tmp_file_path = temp_dir / f"file_{unique_id}_{int(time.time())}{file_ext}"
    tmp_png_path = temp_dir / f"png_{unique_id}_{int(time.time())}.png"
    try:
        # 3. 创建输出路径（也在临时目录）
        with open(tmp_file_path, 'wb') as f:
            f.write(input_stream.getvalue())

        # 4. 构建命令
        tool_path = os.path.join(current_dir, "WmfToPngTool.exe")
        if file_ext == '.emf':
            tool_path = os.path.join(current_dir, "EmfToPngTool.exe")
        cmd = [tool_path, str(tmp_file_path)]

        cmd += ['-crop', '-fastcrop', '-transparent']
        cmd += ['-o', str(tmp_png_path)]

        # 5. 执行转换
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            raise Exception(f"工具转换异常: {error_msg}")

        if not tmp_png_path.exists():
            raise Exception("工具转换失败")

        # 6. 读取生成的 PNG 到内存
        with open(tmp_png_path, 'rb') as image_bytes:
            encoded_src = base64.b64encode(image_bytes.read()).decode("ascii")
        return encoded_src
    except FileNotFoundError:
        raise Exception("工具未找到")
    except subprocess.TimeoutExpired:
        raise Exception("链接超时")
    except Exception as e:
        raise Exception(str(e))
    finally:
        # 8. 清理临时文件（关键）
        try:
            if tmp_file_path.exists():
                os.unlink(tmp_file_path)  # 删除临时文件
        except:
            pass
        try:
            if tmp_png_path and tmp_png_path.exists():
                os.unlink(tmp_png_path)  # 删除 .png
        except:
            pass



if __name__ == '__main__':
    print(getRootPath())
    print(resource_path('lib'))