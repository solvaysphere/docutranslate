from docutranslate.exporter.docx.docx2html_exporter import Docx2HTMLExporterConfig
from docutranslate.translator.ai_translator.docx_translator import DocxTranslatorConfig
from docutranslate.workflow.docx_workflow import DocxWorkflowConfig, DocxWorkflow


def main():
    # 1. Build translator configuration
    translator_config = DocxTranslatorConfig(
        base_url="https://openai.lanternfish.cn/v1/",
        api_key="sk-gpzroMP0Al7sPDmd94C1EfAbB17e411aB61c8218Eb55Ac5c",
        model_id="Qwen2_72B_pqtq",
        # to_lang="Chinese",
        to_lang="English",
        insert_mode="replace",  # Options: "replace", "append", "prepend"
        separator="\n",  # Separator used in "append" and "prepend" modes
    )

    # 2. Build main workflow configuration
    workflow_config = DocxWorkflowConfig(
        translator_config=translator_config,
        html_exporter_config=Docx2HTMLExporterConfig(cdn=False)
    )

    # 3. Instantiate the workflow
    workflow = DocxWorkflow(config=workflow_config)

    # 4. Read the file and execute translation
    workflow.read_path("D:/WorkSpace/DotnetCode/TranslateTool/PN319726_Demo01.docx")
    # await workflow.translate_async()
    # Or use the synchronous method
    workflow.translate()

    # 5. Save the result
    workflow.save_as_docx(name="translated_notes.docx")
    html_config = Docx2HTMLExporterConfig(cdn=False)
    workflow.save_as_html(name="translated_notes.html", output_dir="./output", config=html_config)
    print("DOCX file saved.")

    # You can also export the translated DOCX as bytes
    # text_bytes = workflow.export_to_docx()

if __name__ == "__main__":
    main()