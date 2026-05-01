import requests
import re
import os
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
        if "application/json" in resp.headers.get("Content-Type", ""):
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
def run_checkver(json_path):
    config = load_json(json_path)
    checkver_list=jsonpath.findall("$.checkver", config)
    final_result = []

    for item in checkver_list:
        # 🔥 用 ~ 取出当前层级所有 键名：url、version、name...
        keys = findall("[~]", item)
        print("提取到键名：", keys)

        # 获取 url
        url = item.get("url")
        api_data = fetch_data(url)
        if not api_data:
            continue

        # 🔥 自动遍历键名，动态生成 result
        res = {}
        for key in keys:
            # url 不参与提取
            if key == "url":
                continue

            # 取出对应 jsonpath 表达式
            jsonpath_expr = item.get(key)
            # 提取值
            value = extract_py_jsonpath(api_data, jsonpath_expr)
            # 🔥 键名直接作为 key，值为提取结果
            res[key] = value

        final_result.append(res)

    print(f"\n总 URL 数量：{len(config)}")
    return final_result
    
def load_json(file_path="config.json"):
    """加载配置文件，安全容错"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(base_dir, file_path)
    config_file_path=file_path
    if not os.path.exists(config_file_path):
        print(f"文件不存在：{config_file_path}")
        return {}

    try:
        with open(config_file_path, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except (json.JSONDecodeError, ValueError):
        return []

def save_json(config_list, file_path="config.json"):
    """保存配置到 JSON 文件"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config_list, f, ensure_ascii=False, indent=2)
        
# ===================== 测试（你的格式） =====================
if __name__ == "__main__":
    config =load_json("./bucket/lanzouyun.json")
    data = jsonpath.findall("$.checkver", config)
    print("结果：", data)
    # variables = run_checkver(config["checkver"])
    data = fetch_data("https://api.github.com/repos/chenhb23/lanzouyun-disk/releases/latest")
    # print("提取结果：", data)
    txt = extract_value(data, "$.assets[?(@.browser_download_url =~  /.*zip/)].browser_download_url")
    print("下载结果：", txt)
    txt = extract_value(data, "$.assets[?(@.browser_download_url =~  /.*zip/)].name")
    print("下载结果：", txt)
    # print(jsonpath.findall( "$.checkver[0].~",config))
    
    data = fetch_data("https://geekuninstaller.com/download")
    # print("提取结果：", data)
    txt = extract_value(data, "<b>(.*?)</b>")
    print("提取结果：=============================================================")
    data= run_checkver("./bucket/lanzouyun.json")
    print("提取结果：", data)

