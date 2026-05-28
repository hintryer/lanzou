import os
import json
import requests
import subprocess

# ===================== 配置区域 =====================
JSON_PATH = "./setting/result.json"  # 软件列表路径
SAVE_BASE_DIR = "soft"                # 统一下载到这个文件夹
# ====================================================

def load_json(file_path: str = "config.json") -> list | dict:
    """加载 JSON 配置文件"""
    if not os.path.exists(file_path):
        print(f"[错误] 文件不存在：{file_path}")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, (list, dict)) else []
    except json.JSONDecodeError:
        print(f"[错误] JSON 格式错误：{file_path}")
        return []
    except Exception as e:
        print(f"[错误] 读取文件失败：{str(e)}")
        return []

def download_file(url: str, save_dir: str, filename: str) -> bool:
    """下载文件到指定目录（无进度条）"""
    if not all([url, save_dir, filename]):
        print("[错误] 下载参数不完整（链接/目录/文件名）")
        return False

    try:
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)

        print(f"[开始下载] {filename}")
        with requests.get(url, stream=True, timeout=300) as response:
            response.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        print(f"[下载完成] {filename}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"[下载失败] {filename} | 网络错误：{str(e)}")
    except Exception as e:
        print(f"[下载失败] {filename} | 错误：{str(e)}")
    return False

def upload_files_to_release(upload_dir: str):
    """上传文件夹内所有文件到 GitHub Release"""
    print("\n" + "="*50)
    print("📤 开始上传文件到 Releases...")
    print("="*50)

    try:
        # 1. 创建 TAG
        tag = f"v{os.popen('date +%Y%m%d').read().strip()}"
        print(f"📌 Release 版本号：{tag}")

        # 2. 创建 Release（已存在则跳过）
        subprocess.run(
            f"gh release create \"{tag}\" --title \"{tag}\" --notes \"自动构建\" --latest || true",
            shell=True, check=False
        )

        # 3. 上传 soft 目录下所有文件
        files = os.listdir(upload_dir)
        if not files:
            print("⚠️ soft 目录为空，无需上传")
            return

        for file in files:
            file_path = os.path.join(upload_dir, file)
            if os.path.isfile(file_path):
                print(f"⏫ 正在上传：{file}")
                subprocess.run(
                    f"gh release upload \"{tag}\" \"{file_path}\" --clobber",
                    shell=True, check=False
                )

        print("\n✅ 所有文件上传完成！")

    except Exception as e:
        print(f"❌ 上传失败：{str(e)}")

def main():
    # 加载软件列表
    app_list = load_json(JSON_PATH)
    if not app_list:
        print("[退出] 未加载到任何软件信息")
        return

    print("=" * 50)
    print("🚀 开始批量下载软件（全部保存到 soft 目录）")
    print("=" * 50)

    success_files = []
    failed_files = []

    # 统一下载到 soft 目录
    for app in app_list:
        url = app.get("url", "").strip()
        filename = app.get("name", "unknown_file").strip()

        if download_file(url, SAVE_BASE_DIR, filename):
            success_files.append(filename)
        else:
            failed_files.append(filename)

    # 下载统计
    print("\n" + "="*50)
    print(f"✅ 下载成功：{len(success_files)} 个")
    print(f"❌ 下载失败：{len(failed_files)} 个")
    if failed_files:
        print("失败列表：", failed_files)
    print("="*50)

    # 自动上传 soft 目录所有文件
    upload_files_to_release(SAVE_BASE_DIR)

if __name__ == "__main__":
    main()