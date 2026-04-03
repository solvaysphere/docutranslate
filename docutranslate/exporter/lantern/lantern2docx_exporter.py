# SPDX-FileCopyrightText: 2025 QinHan
# SPDX-License-Identifier: MPL-2.0

from docutranslate.exporter.lantern.base import LanternExporter
from docutranslate.ir.document import Document


class Lantern2DocxExporter(LanternExporter):
    def export(self, document: Document) -> Document:
        return document.copy()
