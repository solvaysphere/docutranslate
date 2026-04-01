# SPDX-FileCopyrightText: 2025 QinHan
# SPDX-License-Identifier: MPL-2.0
import sys

from docutranslate.exporter.base import ExporterConfig
from docutranslate.exporter.html.base import HtmlExporter
from docutranslate.ir.document import Document
import pypandoc
import tempfile
import os

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

class Html2DocxExporter(HtmlExporter):
    def __init__(self, config: ExporterConfig|None = None):
        super().__init__(config=config)
        # 自动下载并安装 Pandoc，避免手动安装
        try:
            pypandoc.get_pandoc_version()
        except OSError:
            pypandoc.download_pandoc()

    def export(self, document: Document) -> Document:
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as docx_temp:
            docx_temp_path = docx_temp.name
        try:
            # 获取当前文件所在目录
            current_dir = os.path.join(get_bundle_root(), 'tools')
            template_path = os.path.join(current_dir, "download_template.docx")
            # 将 content 解码为字符串再传入 convert_text
            html_content = document.content.decode('utf-8') if isinstance(document.content, bytes) else document.content
            pypandoc.convert_text(html_content, 'docx', format='html', outputfile=docx_temp_path, extra_args=['--reference-doc='+template_path])
            return Document.from_path(docx_temp_path)
        except Exception as e:
            raise Exception(f"HTML转换为DOCX时发生错误: {str(e)}")
        finally:
            # 清理临时文件
            if os.path.exists(docx_temp_path):
                os.unlink(docx_temp_path)
