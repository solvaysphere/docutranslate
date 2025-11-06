# SPDX-FileCopyrightText: 2025 QinHan
# SPDX-License-Identifier: MPL-2.0

from docutranslate.exporter.base import ExporterConfig
from docutranslate.exporter.html.base import HtmlExporter
from docutranslate.ir.document import Document
import pypandoc
import tempfile
import os

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
            # 将 content 解码为字符串再传入 convert_text
            html_content = document.content.decode('utf-8') if isinstance(document.content, bytes) else document.content
            pypandoc.convert_text(html_content, 'docx', format='html', outputfile=docx_temp_path)
            return Document.from_path(docx_temp_path)
        except Exception as e:
            raise Exception(f"HTML转换为DOCX时发生错误: {str(e)}")
        finally:
            # 清理临时文件
            if os.path.exists(docx_temp_path):
                os.unlink(docx_temp_path)
