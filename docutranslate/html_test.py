# HtmlWorkflow
from docutranslate.translator.ai_translator.html_translator import HtmlTranslatorConfig
from docutranslate.workflow.html_workflow import HtmlWorkflowConfig, HtmlWorkflow

def main():
    # 1. 构建翻译器配置
    translator_config = HtmlTranslatorConfig(
        base_url="https://openai.lanternfish.cn/v1/",
        api_key="sk-gpzroMP0Al7sPDmd94C1EfAbB17e411aB61c8218Eb55Ac5c",
        model_id="Qwen2_72B_pqtq",
        # to_lang="Chinese",
        to_lang="English",
        insert_mode="replace",  # 备选项 "replace", "append", "prepend"
        separator="\n",  # "append", "prepend"模式时使用的分隔符
    )

    # 2. 构建主工作流配置
    workflow_config = HtmlWorkflowConfig(
        translator_config=translator_config,
    )
    workflow_html = HtmlWorkflow(config=workflow_config)

    # 4. Read the file and execute translation
    workflow_html.read_path("D:/WorkSpace/DotnetCode/TranslateTool/PN319726_Demo01.html")
    # await workflow.translate_async()
    # Or use the synchronous method
    workflow_html.translate()

    # 5. Save the result
    workflow_html.save_as_html(name="translated_html_notes.html")

    print("HTML file saved.")

    # You can also export the translated DOCX as bytes
    # text_bytes = workflow.export_to_docx()


if __name__ == "__main__":
    main()