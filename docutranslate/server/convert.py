from pathlib import Path
from typing import (
    Optional,
)

from docutranslate.exporter.lantern.lantern2docx_exporter import Lantern2DocxExporter
from docutranslate.exporter.lantern.lantern2html_exporter import Lantern2HTMLExporter, Lantern2HTMLExporterConfig
from docutranslate.ir.document import Document


class ConvertService:

    def read_path(self, path: Path | str):
        document = Document.from_path(path)
        return document

    def read_bytes(self, content: bytes, stem: str, suffix: str):
        document = Document.from_bytes(content=content, stem=stem, suffix=suffix)
        return document


    def convert_to_html(self, document: Document):
        config = Lantern2HTMLExporterConfig(cdn=True)
        exporter = Lantern2HTMLExporter(config)
        docu = exporter.export(document)
        return docu.content.decode()

    def convert_to_html_async(self, document: Document):
        config = Lantern2HTMLExporterConfig(cdn=True)
        exporter = Lantern2HTMLExporter(config)
        docu = exporter.export_async(document)
        return docu.content.decode()

    def convert_to_word(self, document: Document):
        exporter = Lantern2DocxExporter()
        docu = exporter.export(document)
        return docu.content


# Global singleton instance
_convert_service: Optional[ConvertService] = None


def get_convert_service() -> ConvertService:
    """Get the global convert service instance (singleton)."""
    global _convert_service
    if _convert_service is None:
        _convert_service = ConvertService()
    return _convert_service