import os
import requests
from bs4 import BeautifulSoup

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3:14b"

def should_translate(text):
    """判断是否需要翻译"""
    parent = text.parent
    return parent.name not in ["script", "style"] and text.strip() != ""

def translate_with_ollama(text, src_lang, dest_lang):
    """
    使用 Ollama 模型翻译文本
    :param text: 待翻译的文本
    :param src_lang: 源语言（如 'zh'）
    :param dest_lang: 目标语言（如 'en'）
    :return: 翻译后的文本
    """
    prompt = f"/no_think 请将以下{src_lang}文翻译成{dest_lang}文：\n\n{text} "
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["response"].strip()
    except Exception as e:
        print(f"翻译失败: {e}")
        return text  # 若翻译失败，返回原文本

def translate_html_file(input_path, output_path, src_lang, dest_lang):
    try:
        # 读取 HTML 文件
        with open(input_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, "lxml")

        # 提取可翻译的文本节点
        text_nodes = [text for text in soup.find_all(string=True) if should_translate(text)]

        # 翻译文本，注意需要去除翻译后文本中的<think>标签
        translated_texts = []
        for text in text_nodes:
            translated_text = translate_with_ollama(text, src_lang, dest_lang)
            translated_text = translated_text.split("</think>\n\n")[1]
            print(f"原文：{text}\n翻译结果: {translated_text}")
            translated_texts.append(translated_text)

        # 替换原文本
        for original, translated in zip(text_nodes, translated_texts):
            try:
                # 防止分割错误，先检查是否存在 "toEn"
                parts = translated.split("toEn")
                final_text = parts[1] if len(parts) > 1 else translated
                original.replace_with(final_text)
            except Exception as e:
                print(f"替换文本失败: {e}")
                continue  # 跳过该段落继续执行

        # 保存翻译后的 HTML，如果文件已经存在，则会被覆盖
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(soup.prettify())

        return True  # 成功返回 True

    except Exception as e:
        print(f"翻译任务失败: {e}")
        return False  # 失败返回 False

# 示例调用
# translate_html_file("example.html", "translated_example.html", src_lang="zh", dest_lang="ar")
# translate_html_file("./danglive-thy.github.io/试了几周在电脑上保留了3个大模型/index.html", "./danglive-thy.github.io/试了几周在电脑上保留了3个大模型/index_en.html", src_lang="zh", dest_lang="en")


# if __name__ == "__main__":
#     translate_html_file(
#         "./danglive-thy.github.io/试了几周在电脑上保留了3个大模型/index.html",
#         "./danglive-thy.github.io/试了几周在电脑上保留了3个大模型/index_en.html",
#         src_lang="zh",
#         dest_lang="en"
#     )