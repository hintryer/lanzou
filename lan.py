import requests
import re
import json
import jsonpath

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
def extract_value(data, jsonpath_str: str= None, regex: str = None):
    try:
        # 1. JSONPath 提取
        if jsonpath_str:
            data = jsonpath.findall(jsonpath_str, data)
        print("JSONPath提取结果：", data)         
        # 2. 正则提取
        match = None
        if regex:
            match = re.search(regex, str(data))

        return match
    except Exception as e:
        return None

    return None

# ===================== 3. 总执行函数（一行调用） =====================
def run_checkver(checkver_list):
    result = {}
    for config in checkver_list:
        data = fetch_data(config["url"])
        if data:
            for key, (jp, reg) in config["items"].items():
                val = extract_value(data, jp, reg)
                if val:
                    result[key] = val.groups()[0] if val.groups() else val.group()
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
    data = fetch_data("https://api.github.com/repos/chenhb23/lanzouyun-disk/releases/latest")
    print("提取结果：", data)
    txt = extract_value(data, "$..browser_download_url", ".*\.zip")
    print("下载结果：", txt)
    print(jsonpath.findall( "$.checkver[0].~",config))
