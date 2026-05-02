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
            print('表达式为空')
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

    
def load_json(file_path="config.json"):

    if not os.path.exists(file_path):
        print(f"文件不存在：{file_path}")
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except (json.JSONDecodeError, ValueError):
        return []

def save_json(config_list, file_path="config.json"):
    """保存配置到 JSON 文件"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config_list, f, ensure_ascii=False, indent=2)

def run_checkver(json_path):
    config = load_json(json_path)
    final_result = {}

    matches = jsonpath.finditer("$.checkver", config)
    for match in matches:
        item_list=jsonpath.findall(f"{match.path}..~", config)
        for item in item_list:
            if item != "apiurl":
                expr=jsonpath.findall(f"{match.path}..{item}", config)
                apiurl=jsonpath.findall(f"{match.path}..apiurl", config)
                data=fetch_data(apiurl[0])
                
                final_result[item] = extract_value(data,expr[0])
    config.update(final_result)
    save_json(config,json_path)   
    return final_result

def run_all_checkver(bucket_dir="bucket"):
    # 遍历 bucket 文件夹
    for filename in os.listdir(bucket_dir):
        # 只处理 .json 文件
        if filename.endswith(".json"):
            file_path = os.path.join(bucket_dir, filename)

            # 对每个文件执行 run_checkver
            run_checkver(file_path)

    print("\n🎉 所有文件检查完成！")

def ceshi():
    item = "url"
    final_result ={}
    final_result[item]="ddd"
    print(final_result)
# ===================== 测试（你的格式） =====================
if __name__ == "__main__":
    # ceshi()
    run_all_checkver()

