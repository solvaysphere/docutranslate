# SPDX-FileCopyrightText: 2025 QinHan
# SPDX-License-Identifier: MPL-2.0
import base64
import hashlib
import os
from dataclasses import dataclass
from io import BytesIO

import httpx
import mammoth
from docutranslate.exporter.base import ExporterConfig
from docutranslate.exporter.docx.base import DocxExporter
from docutranslate.ir.document import Document
from docutranslate.exporter.docx.tool.convert2png import convert_wmf_emf_to_png, convert_wmf_emf_to_png_async
from concurrent.futures import ThreadPoolExecutor

@dataclass
class Docx2HTMLExporterConfig(ExporterConfig):
    cdn: bool = True

class Docx2HTMLExporter(DocxExporter):
    def __init__(self, config: Docx2HTMLExporterConfig = None):
        config = config or Docx2HTMLExporterConfig()
        super().__init__(config=config)
        self.cdn = config.cdn

    def export(self, document: Document) -> Document:
        def convert_single_image(image):
            """单个图片转换函数，用于多进程处理"""
            content_type = image.content_type
            if image.content_type in ["image/wmf", "image/emf", "image/x-wmf", "image/x-emf"]:
                encoded_src = convert_wmf_emf_to_png(image)
                content_type = "image/png"
            else:
                with image.open() as image_bytes:
                    encoded_src = base64.b64encode(image_bytes.read()).decode("ascii")
            return content_type, encoded_src

        def convert_image(image):
            """图片转换包装函数"""
            content_type, encoded_src = convert_single_image(image)
            return {
                "src": "data:{0};base64,{1}".format(content_type, encoded_src)
            }

        html_content = mammoth.convert_to_html(
            BytesIO(document.content),
            convert_image=mammoth.images.img_element(convert_image)
        ).value

        return Document.from_bytes(content=html_content.encode("utf-8"), suffix=".html", stem=document.stem)

    def export_async(self, document: Document) -> Document:
        # 收集所有需要转换的图片
        images_to_convert = []

        def collect_images(image):
            """收集需要转换的图片"""
            images_to_convert.append(image)
            # 返回默认值以继续处理
            return {
                "src": "data:{0};base64,placeholder".format(image.content_type)
            }

        # 先收集所有图片
        mammoth.convert_to_html(
            BytesIO(document.content),
            convert_image=mammoth.images.img_element(collect_images)
        )

        # 使用多进程池并行处理所有图片
        converted_images = {}
        # 控制最大并发数量，防止资源耗尽
        max_workers = min(30, (os.cpu_count() or 1) + 4)

        def get_image_identifier(image):
            """生成图片的稳定标识符"""
            try:
                # 优先使用内容哈希
                with image.open() as f:
                    content = f.read()
                return hashlib.sha256(content).hexdigest()
            except:
                # 回退到属性哈希
                attrs = (image.content_type, getattr(image, 'src', ''), getattr(image, 'alt', ''))
                return hash(attrs)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有转换任务并保持顺序一致
            tasks = [executor.submit(convert_wmf_emf_to_png_async, image) for image in images_to_convert]
            # 按照提交顺序依次获取结果
            for idx, future in enumerate(tasks):
                image = images_to_convert[idx]
                try:
                    content_type, encoded_src = future.result()
                    # 使用稳定标识符代替 id(image)，此处假设 image 对象具有 hashable 属性
                    converted_images[get_image_identifier(image)] = (content_type, encoded_src)
                except Exception as e:
                    print(f"图片转换失败: {e}")
                    converted_images[get_image_identifier(image)] = (image.content_type, "")

        # 重新处理文档，使用缓存的结果
        def convert_image_with_cache(image):
            content_type, encoded_src = converted_images.get(get_image_identifier(image), (image.content_type, ""))
            return {
                "src": "data:{0};base64,{1}".format(content_type, encoded_src)
            }

        html_content = mammoth.convert_to_html(
            BytesIO(document.content),
            convert_image=mammoth.images.img_element(convert_image_with_cache)
        ).value

        return Document.from_bytes(content=html_content.encode("utf-8"), suffix=".html", stem=document.stem)

    def export_with_fish(self, document: Document) -> Document:
        # 调用第三方接口 word 转 html
        try:
            url = "http://135.135.2.92:8081/convert_word_html"
            json_data = {
                "src_base64": base64.b64encode(document.content).decode('utf-8'),
                "ext": document.suffix.lstrip('.')
            }
            response = httpx.post(url, json=json_data)
            if response.status_code != 200:
                raise Exception(f"响应内容:{response.text[:200]}")
            if response.json()["state"] != "1":
                raise Exception(f"响应内容:{response.json()['state_desc']}")
            return Document.from_bytes(content=base64.b64decode(response.json()["target_base64"]), suffix=".html",
                                       stem=document.stem)
        except httpx.HTTPStatusError as e:
            raise Exception(
                f"HTTP 错误 (httpx): {e.response.status_code} - {e.request.url}\n响应内容: {e.response.text[:200]}...")
        except httpx.RequestError as e:
            raise Exception(f"下载ZIP文件时发生错误 (httpx): {e}")
        except Exception as e:
            import traceback
            traceback.print_exc()  # 打印完整的堆栈跟踪，便于调试
            raise Exception(f"发生未知错误: {e}")
