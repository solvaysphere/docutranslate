# SPDX-FileCopyrightText: 2025 QinHan
# SPDX-License-Identifier: MPL-2.0
"""
Word 文档图片处理工具
提供图片占位符替换和还原功能
"""
import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any

import pythoncom
import win32com.client as win32

# 占位符格式
PLACEHOLDER = "[[IMG_{:03d}]]"


def replace_images_in_docx(document_content: bytes) -> tuple[bytes, List[Dict[str, Any]]]:
    """
    将 Word 文档中的图片替换为占位符，并缓存图片位置信息

    :param document_content: Word 文档的二进制内容
    :return: (替换占位符后的文档内容，图片缓存列表)
    """
    # 创建临时文件
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as original_file:
        original_docx = original_file.name
        original_file.write(document_content)

    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as placeholder_file:
        output_placeholder_docx = placeholder_file.name

    try:
        # 初始化 COM
        pythoncom.CoInitialize()
        word = win32.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        word.ScreenUpdating = False

        doc = word.Documents.Open(os.path.abspath(original_docx))
        image_cache = []
        img_idx = 1

        try:
            # 先收集所有图片（倒序，防止删除错乱）
            all_images = []

            # 收集内嵌图片
            for i in range(doc.InlineShapes.Count, 0, -1):
                try:
                    il = doc.InlineShapes(i)
                    all_images.append({
                        "type": "inline",
                        "range": il.Range,
                        "index": i  # 保存原文中的真实位置
                    })
                except:
                    continue

            # 收集浮动图片（Shape 对象）
            for i in range(doc.Shapes.Count, 0, -1):
                try:
                    shape = doc.Shapes(i)
                    all_images.append({
                        "type": "shape",
                        "anchor": shape.Anchor,
                        "index": i  # 保存原文中的真实位置
                    })
                except:
                    continue

            # 开始替换：按顺序生成 [[IMG_001]] [[IMG_002]]
            for img in all_images:
                ph = PLACEHOLDER.format(img_idx)

                # 缓存：占位符 + 原图索引
                image_cache.append({
                    "placeholder": ph,
                    "original_index": img["index"],
                    "type": img["type"]
                })

                # 删除图片，插入占位符
                if img["type"] == "inline":
                    img["range"].Delete()
                    img["range"].InsertAfter(ph)
                else:
                    shape = doc.Shapes(img["index"])
                    shape.Delete()
                    img["anchor"].InsertAfter(ph)

                img_idx += 1

            # 保存处理后的文档
            doc.SaveAs(os.path.abspath(output_placeholder_docx), 16)

            print(f"成功替换 {len(image_cache)} 张图片 一对一占位符")

        finally:
            doc.Close(SaveChanges=True)
            word.Quit()
            pythoncom.CoUninitialize()

        # 读取处理后的文档内容
        result_content = Path(output_placeholder_docx).read_bytes()

        return result_content, image_cache

    finally:
        # 清理临时文件
        for temp_file in [original_docx, output_placeholder_docx]:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


def restore_images_in_docx(
        translated_content: bytes,
        original_content: bytes,
        image_cache: List[Dict[str, Any]]
) -> bytes:
    """
    将翻译后文档中的图片占位符替换为原文档中的对应图片

    :param translated_content: 翻译后文档的二进制内容（包含占位符）
    :param original_content: 原文档的二进制内容（包含原图）
    :param image_cache: 图片缓存列表，由 replace_images_in_docx 返回
    :return: 还原图片后的文档二进制内容
    """
    if not image_cache:
        print("⚠️ 无图片缓存")
        return translated_content

    # 创建临时文件
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as translated_file:
        translated_docx = translated_file.name
        translated_file.write(translated_content)

    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as original_file:
        original_docx = original_file.name
        original_file.write(original_content)

    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as final_file:
        final_docx = final_file.name

    try:
        pythoncom.CoInitialize()
        word = win32.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        word.ScreenUpdating = False

        # 打开原文（取图）+ 译文（放回）
        doc_original = word.Documents.Open(os.path.abspath(original_docx), ReadOnly=True)
        doc_target = word.Documents.Open(os.path.abspath(translated_docx))

        success_count = 0

        # 一对一还原
        for item in image_cache:
            try:
                ph = item["placeholder"]
                original_index = item["original_index"]
                img_type = item["type"]

                # 查找占位符
                word.Selection.WholeStory()
                word.Selection.Find.ClearFormatting()
                word.Selection.Find.Text = ph
                word.Selection.Find.MatchWholeWord = True
                word.Selection.Find.Execute()

                if not word.Selection.Find.Found:
                    continue

                # 删除占位符
                word.Selection.Delete()

                # 从原文复制对应索引的那张图
                if img_type == "inline":
                    source_img = doc_original.InlineShapes(original_index)
                    source_img.Range.Copy()
                else:
                    source_img = doc_original.Shapes(original_index)
                    source_img.Copy()

                # 粘贴到占位符位置
                word.Selection.Paste()
                success_count += 1

            except Exception as e:
                print(f"❌ 还原失败 {ph}: {str(e)}")
                continue

        # 保存最终文档
        doc_target.SaveAs(os.path.abspath(final_docx), 16)
        doc_target.Close(SaveChanges=True)
        doc_original.Close(SaveChanges=False)
        word.Quit()
        pythoncom.CoUninitialize()

        print(f"\n✅ 成功一对一还原 {success_count} 张图片！")

        # 读取处理后的文档内容
        result_content = Path(final_docx).read_bytes()

        return result_content

    finally:
        # 清理临时文件
        for temp_file in [translated_docx, original_docx, final_docx]:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

