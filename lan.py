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
        if "application/json" in response.headers.get("Content-Type", ""):
            return resp.json()
        else:
            return resp.text
    except Exception as e:
        print(f"请求失败：{e}")
        return None

# ===================== 2. 变量提取函数（自动识别 JSONPath / 正则） =====================
def extract_value(data, expr: str = None):
    try:
        # 如果表达式为空
        if not expr:
            return None

        # ======================================
        # 自动判断：如果以 $ 开头 → 按 JSONPath 处理
        # 否则 → 按正则处理
        # ======================================
        if expr.startswith("$"):
            # JSONPath 提取
            data = jsonpath.findall(expr, data)
            # 列表转字符串
            if isinstance(data, (list, tuple)):
                data = data[0] if len(data) > 0 else ""

        # 正则提取（无论是否走了JSONPath，最后都可以用正则过滤）
        match = None
        if not expr.startswith("$"):
            # 直接当正则
            match = re.search(expr, str(data))
        else:
            # 已经JSONPath提取过，不做正则
            return data

        # 返回匹配到的内容，不是match对象
        if match:
            return match.group(1) if match.groups() else match.group()

        return None

    except Exception as e:
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

    # variables = run_checkver(config["checkver"])
    data = fetch_data("https://api.github.com/repos/chenhb23/lanzouyun-disk/releases/latest")
    # print("提取结果：", data)
    txt = extract_value(data, "<b>(.*?)</b>")
    print("下载结果：", txt)
    txt = extract_value(data, "$.assets[?(@.browser_download_url =~  /.*zip/)].name")
    print("下载结果：", txt)
    # print(jsonpath.findall( "$.checkver[0].~",config))
    
    data = fetch_data("https://geekuninstaller.com/download")
    print("提取结果：", data)
    txt = extract_value(data, "$.assets[?(@.browser_download_url =~  /.*zip/)].browser_download_url")
    print("下载结果：", txt)
    txt = extract_value(data, "$.assets[?(@.browser_download_url =~  /.*zip/)].name")
    print("下载结果：", txt)
    # print(jsonpath.findall( "$.checkver[0].~",config))
