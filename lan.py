import requests
import re
import json
from jsonpath import JSONPath

# ===================== 1. 核心请求函数（只需要 url） =====================
def fetch_data(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"请求失败：{e}")
        return None

# ===================== 2. 变量提取函数（适配你的精简格式） =====================
def extract_variables(data, items):
    variables = {}
    for var_name, (jpath, regex) in items.items():
        try:
            matches = [str(m.value) for m in parse(jpath).find(data)]
            for text in matches:
                match = re.search(regex, text)
                if match:
                    variables[var_name] = match.group("v") if "v" in match.groupdict() else match.group(1)
                    break
        except Exception as e:
            print(f"{var_name} 提取失败：{e}")
    return variables

# ===================== 3. 总执行函数（一行调用） =====================
def run_checkver(checkver_list):
    result = {}
    for config in checkver_list:
        data = fetch_data(config["url"])
        if data:
            vars = extract_variables(data, config["items"])
            result.update(vars)
    return result

# ===================== 测试（你的格式） =====================
if __name__ == "__main__":
    config = {
        "checkver": [
            {
                "url": "https://api.github.com/repos/chenhb23/lanzouyun-disk/releases/latest",
                "items": {
                    "version": ["$.tag_name", "(?<v>.+)"],
                    "filename": ["$..browser_download_url", "([^/]+\\.zip)$"]
                }
            }
        ]
    }

    variables = run_checkver(config["checkver"])
    print("提取结果：")
    print(json.dumps(variables, indent=2))
