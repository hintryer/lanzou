import requests
import re
import os
import json
import jsonpath

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

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

# ===================== 1. 核心请求函数（只需要 url） =====================
def fetch_data(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Authorization": f"token {GITHUB_TOKEN}",  # 👈 这一行就是加入 Token
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

def run_update(json_path):
    config = load_json(json_path)
    final_result = {}

    item_list=jsonpath.findall("$.autoupdate..~", config)
    for item in item_list:
        value=jsonpath.findall(f"$.autoupdate..{item}", config)
        final_result[item] = value[0].format(**config)
    config.update(final_result)
    save_json(config,json_path)   
    return final_result                

def run_all(bucket_dir="bucket"):
    # 遍历 bucket 文件夹
    for filename in os.listdir(bucket_dir):
        # 只处理 .json 文件
        if filename.endswith(".json"):
            file_path = os.path.join(bucket_dir, filename)
            print(f"正在处理：{filename}")
            # 对每个文件执行 run_checkver
            run_checkver(file_path)
            run_update(file_path)
            update_url(file_path)
    print("\n🎉 所有文件检查完成！")

def update_url(json_path):
    config = load_json(json_path)
    
    # 提取 url
    url_list = jsonpath.findall("$.url", config)
    
    # 安全判断：防止空、防止 None
    if not url_list or url_list[0] is None:
        return {}

    url = url_list[0].strip()
    
    # ==============================================
    # 只有 Github 才处理：添加 oldurl + 替换代理
    # ==============================================
    if "github" in url.lower():
        oldurl = url
        real_down_url = "https://gh-proxy.com/" + url
        
        final_result = {
            "url": real_down_url,
            "oldurl": oldurl
        }
        
        config.update(final_result)
        save_json(config, json_path)   
        return final_result

    # ==============================================
    # 非 Github：什么都不做，直接返回空
    # ==============================================
    return {}          

def ceshi():
    item = "url"
    final_result ={}
    final_result[item]="ddd"
    print(final_result)
# ===================== 测试（你的格式） =====================
if __name__ == "__main__":
    # ceshi()
    #run_update("./bucket/donet9.json")
    # print(fetch_data("https://api.github.com/repos/WEIFENG2333/VideoCaptioner/releases/"))
    run_all()


