import os
import json
import requests

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

def save_json(data: list | dict, file_path: str = "config.json") -> bool:
    """保存数据到 JSON 文件"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[错误] 保存 JSON 失败：{str(e)}")
        return False

def download_file(url: str, save_dir: str, filename: str) -> bool:
    """
    下载文件（无进度条）
    :param url: 下载链接
    :param save_dir: 保存目录
    :param filename: 保存的文件名（可自定义修改）
    """
    if not all([url, save_dir, filename]):
        print("[错误] 下载参数不完整（链接/目录/文件名）")
        return False

    try:
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)

        print(f"[开始下载] {filename}")
        # 流式下载
        with requests.get(url, stream=True, timeout=180) as response:
            response.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        print(f"[下载完成] {filename}\n")
        return True

    except requests.exceptions.RequestException as e:
        print(f"[下载失败] {filename} | 网络错误：{str(e)}\n")
    except Exception as e:
        print(f"[下载失败] {filename} | 错误：{str(e)}\n")
    return False

def main():
    json_path = "./setting/result.json"
    app_list = load_json(json_path)

    if not app_list:
        print("[退出] 未加载到任何软件信息")
        return

    print("=" * 50)
    print("🚀 开始批量下载软件")
    print("=" * 50)

    success = []
    failed = []

    for app in app_list:
        url = app.get("url", "").strip()
        category = app.get("category", "未分类").strip()
        original_name = app.get("name", "未知文件").strip()

        # ====================== 在这里自定义文件名 ======================
        # 示例 1：直接使用原文件名（默认）
        save_name = original_name

        # 示例 2：自定义重命名（解开下面注释即可使用）
        # save_name = "自定义_" + original_name

        # 示例 3：固定名称
        # save_name = "mytool.exe"
        # ==============================================================

        if download_file(url, category, save_name):
            success.append(save_name)
        else:
            failed.append(save_name)

    # 最终统计
    print("=" * 50)
    print(f"✅ 下载成功：{len(success)} 个")

    print(f"\n❌ 下载失败：{len(failed)} 个")
    if failed:
        for name in failed:
            print(f"  - {name}")
    print("=" * 50)

if __name__ == "__main__":
    main()