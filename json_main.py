import json
import os

def unpack_manifest(json_path: str, output_dir: str = None):
    """
    从整合的 JSON 清单中批量解压出单个软件 JSON 文件
    
    :param json_path: 整合后的 all_manifest.json 文件路径
    :param output_dir: 输出目录，默认为 json_path 目录下的 scr 文件夹
    """
    # 1. 获取 JSON 文件所在目录
    base_dir = os.path.dirname(json_path)
    
    # 2. 设置默认输出目录：scr 文件夹
    if output_dir is None:
        output_dir = os.path.join(base_dir, "bucket")
    
    # 3. 自动创建输出目录（不存在则创建）
    os.makedirs(output_dir, exist_ok=True)
    
    # 4. 读取整合清单
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 5. 批量生成 JSON
    for item in data:
        filename = item["filename"]
        content = item["content"]
        
        # 最终文件路径
        file_path = os.path.join(output_dir, filename)
        
        # 写入文件
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        
        print(f"✅ 已生成: {filename}")

    print(f"\n🎉 全部完成！文件保存在：\n{output_dir}")

def pack_manifest(input_dir: str, output_file: str = "all_manifest.json"):
    """
    合并文件夹内所有 JSON 文件 → 生成一个整合清单
    格式：[{"filename":"xxx.json", "content": {...}}, ...]

    :param input_dir: 存放单个 JSON 文件的目录
    :param output_file: 输出的合并文件名
    """
    # 最终清单
    manifest = []

    # 遍历目录下所有 .json 文件
    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(input_dir, filename)

            # 读取每个 JSON 内容
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = json.load(f)
            except Exception as e:
                print(f"❌ 读取失败 {filename}: {e}")
                continue

            # 按你需要的格式加入清单
            manifest.append({
                "filename": filename,
                "content": content
            })
            print(f"✅ 已加入: {filename}")

    # 写入合并后的 JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=4)

    print(f"\n🎉 合并完成！文件保存在: {output_file}")


# ====================== 使用示例 ======================
if __name__ == "__main__":
    # 你只需要改这一行
    unpack_manifest("soft.json")
    
    # 如需自定义输出目录，用下面这行
    # unpack_manifest("github.json", output_dir="my_output_folder")

    # 执行合并
    # pack_manifest("bucket", "all_manifest.json")