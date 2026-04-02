# SPDX-FileCopyrightText: 2025 QinHan
# SPDX-License-Identifier: MPL-2.0
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from docutranslate.exporter.base import ExporterConfig
from docutranslate.exporter.lantern.lantern2docx_exporter import Lantern2DocxExporter
from docutranslate.exporter.lantern.lantern2html_exporter import Lantern2HTMLExporterConfig, Lantern2HTMLExporter
from docutranslate.glossary.glossary import Glossary
from docutranslate.ir.document import Document
from docutranslate.translator.ai_translator.lantern_translator import LanternTranslatorConfig, LanternTranslator
from docutranslate.workflow.base import Workflow, WorkflowConfig
from docutranslate.workflow.interfaces import LanternExportable, LanternHtmlExportable


@dataclass(kw_only=True)
class LanternWorkflowConfig(WorkflowConfig):
    translator_config: LanternTranslatorConfig
    html_exporter_config: Lantern2HTMLExporterConfig


class LanternWorkflow(Workflow[LanternWorkflowConfig, Document, Document], LanternHtmlExportable[Lantern2HTMLExporterConfig],
                   LanternExportable[ExporterConfig]):
    def __init__(self, config: LanternWorkflowConfig):
        super().__init__(config=config)
        if config.logger:
            for sub_config in [self.config.translator_config]:
                if sub_config:
                    sub_config.logger = config.logger

    def _pre_translate(self, document_original: Document):
        suffix = document_original.suffix.lower() if document_original.suffix else ""
        if suffix != ".docx" or suffix != ".html":
            raise ValueError(f"该工作流不支持{suffix}格式，请转为.docx格式或者.html格式")
        document = document_original.copy()
        translate_config = self.config.translator_config
        translator = LanternTranslator(translate_config)
        return document, translator

    def translate(self) -> Self:
        # 同步版本
        self.progress_tracker.update(percent=10, message="正在准备翻译...")
        document, translator = self._pre_translate(self.document_original)
        translator.translate(document)
        if translator.glossary.glossary_dict:
            self.progress_tracker.update(percent=95, message="正在保存术语表...")
            self.attachment.add_document("glossary", Glossary.glossary_dict2csv(translator.glossary.glossary_dict))
        self.progress_tracker.update(percent=100, message="翻译完成")
        self.document_translated = document
        return self

    async def translate_async(self) -> Self:
        # 准备阶段
        self.progress_tracker.update(percent=10, message="正在准备翻译...")
        document, translator = self._pre_translate(self.document_original)

        # 翻译阶段 - 由 agent 更新细粒度进度
        await translator.translate_async(document)

        # 保存术语表阶段
        if translator.glossary.glossary_dict:
            self.progress_tracker.update(percent=95, message="正在保存术语表...")
            self.attachment.add_document("glossary", Glossary.glossary_dict2csv(translator.glossary.glossary_dict))

        self.progress_tracker.update(percent=100, message="翻译完成")
        self.document_translated = document
        return self

    def export_to_html(self, config: Lantern2HTMLExporterConfig = None) -> str:
        config = config or self.config.html_exporter_config
        start_time = time.time()
        docu = self._export(Lantern2HTMLExporter(config))
        end_time = time.time()
        duration = end_time - start_time
        self.logger.info(f"导出Html完成，用时 {duration:.2f} 秒。")
        return docu.content.decode()

    def export_to_docx(self, _: ExporterConfig | None = None) -> bytes:
        docu = self._export(Lantern2DocxExporter())
        return docu.content

    def save_as_html(self, name: str = None, output_dir: Path | str = "./output",
                     config: Lantern2HTMLExporter | None = None) -> Self:
        config = config or self.config.html_exporter_config
        self._save(exporter=Lantern2HTMLExporter(config), name=name, output_dir=output_dir)
        return self

    def save_as_docx(self, name: str = None, output_dir: Path | str = "./output",
                     _: ExporterConfig | None = None) -> Self:
        self._save(exporter=Lantern2DocxExporter(), name=name, output_dir=output_dir)
        return self