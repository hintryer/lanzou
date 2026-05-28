import os
import json
import requests
from tqdm import tqdm  # 下载进度条（需安装）

def load_json(file_path: str = "config.json") -> list | dict:
    """
    加载 JSON 配置文件
    :param file_path: JSON 文件路径
    :return: 解析后的列表/字典，加载失败返回空列表
    """
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
    """
    保存数据到 JSON 文件
    :param data: 要保存的数据
    :param file_path: 保存路径
    :return: 保存成功返回 True，失败返回 False
    """
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
    带进度条下载文件
    :param url: 下载链接
    :param save_dir: 保存目录
    :param filename: 文件名
    :return: 下载成功返回 True，失败返回 False
    """
    if not all([url, save_dir, filename]):
        print("[错误] 下载参数不完整（链接/目录/文件名）")
        return False

    try:
        # 创建保存目录
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)

        # 流式请求 + 获取文件大小
        response = requests.get(url, stream=True, timeout=180)
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))

        print(f"[开始] {filename}")
        # 带进度条写入文件
        with open(save_path, "wb") as f, tqdm(
            total=total_size, unit="B", unit_scale=True, unit_divisor=1024
        ) as progress:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    progress.update(len(chunk))

        print(f"[完成] {filename}\n")
        return True

    except requests.exceptions.RequestException as e:
        print(f"[下载失败] {filename} | 网络错误：{str(e)}")
    except Exception as e:
        print(f"[下载失败] {filename} | 未知错误：{str(e)}")
    return False

def main():
    # 配置
    json_path = "./setting/result.json"
    
    # 加载软件列表
    app_list = load_json(json_path)
    if not app_list:
        print("[退出] 未加载到任何软件信息")
        return

    print("=" * 50)
    print("🚀 开始批量下载软件")
    print("=" * 50)

    # 批量下载
    success_count = 0
    fail_count = 0

    for app in app_list:
        # 安全获取字段
        url = app.get("url", "").strip()
        category = app.get("category", "未分类").strip()
        name = app.get("name", "未知文件").strip()

        if download_file(url, category, name):
            success_count += 1
        else:
            fail_count += 1

    # 下载统计
    print("=" * 50)
    print(f"🎉 下载任务完成 | 成功：{success_count} 个 | 失败：{fail_count} 个")
    print("=" * 50)

if __name__ == "__main__":
    main()