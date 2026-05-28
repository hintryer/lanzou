import os
import json
import requests

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

def download_file(url, save_dir, filename):
    if not url or not filename:
        print("下载失败：未获取到有效链接或文件名")
        return False

    try:
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)
        
        print(f"开始下载: {filename}")
        with requests.get(url, stream=True, timeout=60) as response:
            response.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

        print(f"下载完成: {filename}\n")
        return True

    except Exception as e:
        print(f"下载失败: {filename} | 错误: {str(e)}")
        return False
    
def main():
        # 1. 加载云端最新软件列表（你的配置）
    new_apps = load_json("./setting/result.json")

    print("🚀 开始下载...\n")

    # 2. 从 0 遍历到 new_list 长度，按索引 i 对比
    for i in range(len(new_apps)):
        new_app = new_apps[i]
        download_file(new_app[url],new_app[category],new_app[name])

    print("\n🎉 全部检查完成！")

if __name__ == "__main__":
    main()