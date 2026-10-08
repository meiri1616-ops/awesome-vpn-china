import os
import re
import requests

# 目标语种配置与本地化指令
TARGET_LANGS = {
    "zh-TW": {
        "filename": "README_zh-TW.md",
        "name": "繁體中文",
        "current_label": "🇭🇰/🇹🇼 繁體中文 (目前)",
        "prompt": "Translate this Markdown text into Traditional Chinese (Taiwan/Hong Kong convention). Use local terms: 網路 instead of 网络, 伺服器 instead of 服务器, 用戶端 instead of 客户端, 翻牆/跨區 instead of 翻墙."
    },
    "en": {
        "filename": "README_en.md",
        "name": "English",
        "current_label": "🇺🇸 English (Current)",
        "prompt": "Translate this Markdown text into fluent, professional English tailored for cybersecurity, privacy advocates, and remote developers."
    },
    "ja": {
        "filename": "README_ja.md",
        "name": "日本語",
        "current_label": "🇯🇵 日本語 (現在)",
        "prompt": "Translate this Markdown text into natural, professional Japanese with technical terminology (e.g. 難読化プロトコル, ノーログポリシー, リモートワーク)."
    },
    "de": {
        "filename": "README_de.md",
        "name": "Deutsch",
        "current_label": "🇩🇪 Deutsch (Aktuell)",
        "prompt": "Translate this Markdown text into precise, professional German, emphasizing data privacy (Datenschutz), audits, and no-log compliance."
    },
    "es": {
        "filename": "README_es.md",
        "name": "Español",
        "current_label": "🇪🇸 Español (Actual)",
        "prompt": "Translate this Markdown text into neutral, professional Spanish (Español neutro) suitable for Latin America and Spain."
    }
}

def build_lang_bar(current_code):
    """动态生成多语言导航条，并高亮当前语言"""
    links = [
        "[ 🇨🇳 简体中文 ](./README.md)" if current_code != "zh-CN" else "[ 🇨🇳 简体中文 (当前) ](./README.md)",
        "[ 🇭🇰/🇹🇼 繁體中文 ](./README_zh-TW.md)" if current_code != "zh-TW" else "[ 🇭🇰/🇹🇼 繁體中文 (目前) ](./README_zh-TW.md)",
        "[ 🇺🇸 English ](./README_en.md)" if current_code != "en" else "[ 🇺🇸 English (Current) ](./README_en.md)",
        "[ 🇯🇵 日本語 ](./README_ja.md)" if current_code != "ja" else "[ 🇯🇵 日本語 (現在) ](./README_ja.md)",
        "[ 🇩🇪 Deutsch ](./README_de.md)" if current_code != "de" else "[ 🇩🇪 Deutsch (Aktuell) ](./README_de.md)",
        "[ 🇪🇸 Español ](./README_es.md)" if current_code != "es" else "[ 🇪🇸 Español (Actual) ](./README_es.md)"
    ]
    return f"**Language / 语言切换**:\n" + " · ".join(links)

def translate_with_gemini(text, target_conf):
    """调用 Gemini 3.5 Flash-Lite 进行格式保真翻译"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise Exception("未检测到 GEMINI_API_KEY")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    system_instruction = (
        f"{target_conf['prompt']}\n"
        "CRITICAL RULES:\n"
        "1. Do NOT translate or modify any URLs, affiliate links, image links, or badges.\n"
        "2. Keep the exact Markdown table structure, pipes '|', and spacing.\n"
        "3. Keep code blocks, backticks `...`, and tags untouched.\n"
        "4. Output ONLY the translated Markdown directly, with NO conversational filler."
    )

    payload = {
        "contents": [{
            "parts": [
                {"text": system_instruction},
                {"text": text}
            ]
        }],
        "generationConfig": {
            "temperature": 0.2  # 低温保证翻译严谨不幻觉
        }
    }

    res = requests.post(url, json=payload, headers=headers, timeout=60)
    if res.status_code == 200:
        data = res.json()
        candidates = data.get("candidates", [])
        if candidates:
            return candidates[0]["content"]["parts"][0]["text"].strip()
    
    raise Exception(f"Gemini 翻译失败 (HTTP {res.status_code}): {res.text}")

def main():
    if not os.path.exists("README.md"):
        print("未找到 README.md，退出。")
        return

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    # 正则提取语言导航条之后的正文主体，避免重复翻译顶部导航
    content_clean = re.sub(r"\*\*Language / 语言切换\*\*.*?(?=\n\n|\r\n\r\n)", "", content, flags=re.DOTALL)

    for lang_code, conf in TARGET_LANGS.items():
        print(f"正在自动化生成 {conf['name']} ({conf['filename']})...")
        try:
            translated_body = translate_with_gemini(content_clean, conf)
            
            # 将该语言专属的导航条插入在标题下方
            lang_bar = build_lang_bar(lang_code)
            
            # 组装最终文档：将导航条插入到第一个标题后面
            if "# 🌐" in translated_body:
                parts = translated_body.split("# 🌐", 1)
                final_content = parts[0] + "# 🌐" + parts[1].split("\n", 1)[0] + f"\n\n{lang_bar}\n" + parts[1].split("\n", 1)[1]
            else:
                final_content = f"{lang_bar}\n\n" + translated_body

            with open(conf["filename"], "w", encoding="utf-8") as out_f:
                out_f.write(final_content)
                
            print(f"✅ {conf['filename']} 生成成功！")
        except Exception as e:
            print(f"❌ 翻译 {lang_code} 出错: {e}")

if __name__ == "__main__":
    main()
