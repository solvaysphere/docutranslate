import pypandoc
import base64
import tempfile
import os

def html_to_docx_base64(html_base64_content):
    """
    接收base64格式的HTML内容，返回base64格式的Word文档

    Args:
        html_base64_content (str): base64编码的HTML内容

    Returns:
        str: base64编码的Word文档内容

    Raises:
        ValueError: 当输入内容为空时
        Exception: 转换过程中的其他异常
    """
    # 验证输入参数
    if not html_base64_content:
        raise ValueError("HTML内容不能为空")

    try:
        # 解码base64 HTML内容
        html_bytes = base64.b64decode(html_base64_content)
        html_content = html_bytes.decode('utf-8')
    except Exception as e:
        raise Exception(f"解析base64 HTML内容时发生错误: {str(e)}")

    # 创建临时文件用于处理
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as html_temp:
        html_temp.write(html_content)
        html_temp_path = html_temp.name

    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as docx_temp:
        docx_temp_path = docx_temp.name

    try:
        # 使用pypandoc将HTML转换成Word文件
        pypandoc.convert_text(html_content, 'docx', format='html', outputfile=docx_temp_path)

        # 读取生成的Word文件并转换为base64
        with open(docx_temp_path, 'rb') as docx_file:
            docx_bytes = docx_file.read()
            docx_base64 = base64.b64encode(docx_bytes).decode('utf-8')

        return docx_base64

    except Exception as e:
        raise Exception(f"HTML转换为DOCX时发生错误: {str(e)}")
    finally:
        # 清理临时文件
        if os.path.exists(html_temp_path):
            os.unlink(html_temp_path)
        if os.path.exists(docx_temp_path):
            os.unlink(docx_temp_path)

def html_to_docx(html_file_path, docx_file_path):
    # 验证输入参数
    if not html_file_path or not docx_file_path:
        raise ValueError("文件路径不能为空")

    try:
        # 读取HTML文件
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"找不到HTML文件: {html_file_path}")
    except PermissionError:
        raise PermissionError(f"没有权限读取文件: {html_file_path}")
    except Exception as e:
        raise Exception(f"读取HTML文件时发生错误: {str(e)}")

    try:
        # 使用pypandoc将HTML直接转换成Word文件
        pypandoc.convert_text(html_content, 'docx', format='html', outputfile=docx_file_path)
        print(f"转换完成，文件已保存为: {docx_file_path}")
    except Exception as e:
        raise Exception(f"HTML转换为DOCX时发生错误: {str(e)}")

if __name__ == '__main__':
    # 自动下载并安装 Pandoc，避免手动安装
    try:
        version = pypandoc.get_pandoc_version()
    except OSError:
        pypandoc.download_pandoc()

    # 使用函数
    html_file_path = 'D:\WorkSpace\DotnetCode\TranslateTool\PN319726_Demo01.html'
    docx_file_path = 'D:\WorkSpace\DotnetCode\TranslateTool\PN319726_Demo01_From_Html.docx'
    html_to_docx(html_file_path, docx_file_path)