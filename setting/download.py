import os
import json
import requests
from datetime import datetime

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

# ======================= 【新增：生成下载 BAT 函数】 =======================
def generate_download_bat(app_list: list, bat_output: str = "download_release.bat"):
    """
    生成批量下载 BAT
    - 文件名与原 JSON 一致
    - 下载地址自动替换为当天 Release 地址：v年月日-时分
    """
    # 生成当天版本号：v20260529
    today_tag = datetime.now().strftime("v%Y%m%d")

    bat_lines = [
        "@echo off",
        "chcp 65001 >nul",
        "cls",
        "echo ==============================================",
        "echo        从 GitHub Release 批量下载",
        f"echo        版本：{today_tag}",
        "echo ==============================================",
        "echo.",
        "md soft 2>nul",
    ]

    for app in app_list:
        name = app.get("name", "").strip()
        if not name:
            continue
        
        category = app.get("category", "未分类").strip()

        # 拼接新的下载地址（当天 Release）
        new_url = f"https://gh-proxy.com/https://github.com/hintryer/lanzou/releases/download/{today_tag}/{name}"

        # ✅ 关键修复：先创建目录，再下载！解决 系统找不到指定文件
        save_path = f"soft\\{category}\\{name}"
        
        bat_lines.append(f"echo 📥 下载：{name}")
        bat_lines.append(f'md "soft\\{category}" 2>nul')  # 自动创建分类文件夹
        bat_lines.append(f'curl -L -# -o "{save_path}" "{new_url}"')
        bat_lines.append("echo.")

    bat_lines.extend([
        "echo ==============================================",
        "echo                ✅ 下载完成",
        "echo ==============================================",
        "pause",
    ])

    # 写入 BAT（UTF-8 保证中文不乱码）
    with open(bat_output, "w", encoding="utf-8") as f:
        f.write("\n".join(bat_lines))

    print(f"✅ 已生成下载 BAT：{bat_output}")
    print(f"ℹ️ 下载地址已自动替换为：{today_tag}\n")

# =========================================================================

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
        category = "./soft"
        original_name = app.get("name", "未知文件").strip()

        save_name = original_name

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

    # ======================= 【新增：调用生成 BAT】 =======================
    generate_download_bat(app_list, "download_release.bat")

if __name__ == "__main__":
    main()