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

def get_file_size_mb(file_path):
    if not os.path.isfile(file_path):
        return 0.0
    return round(os.path.getsize(file_path) / (1024**2), 2)


def check_and_update(old_info, new_info):
    old_version = old_info.get("version", "")
    new_version = new_info.get("version", "")
    download_url = new_info.get("url", "")
    category = new_info.get("category", "./soft")
    save_dir =f"./soft/{category}"
    filename = new_info.get("name", "")
    old_filename = old_info.get("name") or filename
    old_file_path = os.path.join(save_dir, old_filename)
    current_file_path = os.path.join(save_dir, filename)
    
    MAX_SIZE_MB = 100

    print(f"当前版本: {old_version} → 最新版本: {new_version}")

    if new_version == old_version:
        if os.path.exists(old_file_path):
            print("✅ 已是最新版本")
            return False
        else:
            print("⚠️ 文件丢失，重新下载...")
            return download_file(download_url, save_dir, filename)
    else:
        print(f"📦 开始更新：{filename}")

        # 先下载
        dl_ok = download_file(download_url, save_dir, filename)
        
        # 再获取文件大小
        file_mb = get_file_size_mb(current_file_path)
        is_file_too_big = file_mb > MAX_SIZE_MB

        if dl_ok:
            if not is_file_too_big:
                # 文件不大 → 删除旧文件
                if os.path.exists(old_file_path) and old_file_path != current_file_path:
                    try:
                        os.remove(old_file_path)
                        print("🗑️ 已删除旧文件")
                    except Exception:
                        pass
                print("✅ 更新成功")
            else:
                print(f"⚠️ 文件过大({file_mb:.2f}MB)")

        return dl_ok
    
def main():
        # 1. 加载云端最新软件列表（你的配置）
    new_apps = load_json("./setting/result.json")
    
    # 2. 加载本地历史版本
    old_apps = load_json("./setting/local_result.json")

    print("🚀 开始检查软件更新...\n")

    # 2. 从 0 遍历到 new_list 长度，按索引 i 对比
    for i in range(len(new_apps)):
        new_app = new_apps[i]
        
        # 安全判断：local 不够长就用空对象
        old_app = old_apps[i] if i < len(old_apps) else {}
        
        # 对比 new[i] 和 local[i]
        check_and_update(new_app, old_app)

    # 3. 保存最新结果到本地（下次对比）
    save_json(new_apps, "./setting/local_result.json")
    print("\n🎉 全部检查完成！")
if __name__ == "__main__":
    main()