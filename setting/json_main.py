import json
import os

def unpack_json(json_path="./setting/allsoftset.json", output_dir = "./bucket"):
    """
    从整合的 JSON 清单中批量解压出单个软件 JSON 文件
    
    :param json_path: 整合后的json文件路径 如："./setting/github.json"
    :param output_dir: 输出目录，默认为 目录下的bucket文件夹 如："./bucket"
    """

    os.makedirs(output_dir, exist_ok=True)
    
    # 读取整合清单
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 批量生成 JSON
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

def pack_json(input_dir="./bucket", output_file= "./setting/allsoftset.json"):
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

def merge_json(input_folder="./bucket", output_file="./setting/result.json"):
    """
    合并文件夹下所有 JSON 只保留指定字段
    :param input_folder: 输入文件夹，默认 ./bucket
    :param output_file: 输出文件路径，默认 ./result.json
    """
    # ====================== 字段已移入函数内 ======================
    REQUIRED_FIELDS = [
        "name",
        "category",
        "version",
        "description",
        "homepage",
        "url"
    ]
    # ============================================================
    
    merged_list = []

    # 遍历文件夹所有文件
    for filename in os.listdir(input_folder):
        # 只处理 .json 文件
        if filename.lower().endswith(".json"):
            file_path = os.path.join(input_folder, filename)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 如果是列表，遍历；如果是单对象，直接处理
                items = data if isinstance(data, list) else [data]

                for item in items:
                    # 只保留需要的字段
                    filtered = {key: item.get(key, "") for key in REQUIRED_FIELDS}
                    merged_list.append(filtered)

                print(f"✅ 已处理：{filename}")

            except Exception as e:
                print(f"❌ 处理失败 {filename}：{str(e)}")

    # 写入最终文件
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged_list, f, ensure_ascii=False, indent=4)

    print(f"\n🎉 合并完成！共 {len(merged_list)} 条数据")
    #print(f"📁 输出文件：{output_file}")
    return merged_list

def json_to_markdown2(json_file="./setting/result.json", md_file="./setting/result.md"):
    """
    JSON转MD表格 + 按分类排序 + 主页、下载统一为链接格式
    """
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 按分类排序
    data = sorted(data, key=lambda x: x.get("category", "").lower())

    md_content = """# 软件清单

| 名称 | 分类 | 版本 | 描述 | 主页 | 下载 |
| ---- | ---- | ---- | ---- | ---- | ---- |
"""

    for item in data:
        name = item.get("name", "")
        category = item.get("category", "")
        version = item.get("version", "")
        desc = item.get("description", "")
        homepage = item.get("homepage", "")
        url = item.get("url", "")

        # 主页：有地址就 [主页](链接)，否则空
        home_str = f"[主页]({homepage})" if homepage.strip() else ""
        # 下载：有地址就 [下载](链接)，否则空
        down_str = f"[下载]({url})" if url.strip() else ""

        md_content += f"| {name} | {category} | {version} | {desc} | {home_str} | {down_str} |\n"

    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"✅ 转换完成！Markdown 文件已保存：{md_file}")


def json_to_markdown(json_file="./setting/result.json", md_file="./README.md"):
    """
    JSON转MD
    1. 自动按分类分组
    2. 分类生成二级标题
    3. 每个分类独立表格
    4. 主页、下载统一为链接格式
    """
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 按分类排序
    data = sorted(data, key=lambda x: x.get("category", "").lower())

    # 分组字典
    group_dict = {}
    for item in data:
        cat = item.get("category", "未分类").strip()
        if cat not in group_dict:
            group_dict[cat] = []
        group_dict[cat].append(item)

    # 开始拼接MD
    md_content = "# 软件清单\n\n"

    # 遍历分组
    for category, item_list in group_dict.items():
        # 二级分类标题
        md_content += f"## {category}\n\n"
        # 表格表头
        md_content += "| 名称 | 版本 | 描述 | 主页 | 下载 |\n"
        md_content += "| ---- | ---- | ---- | ---- | ---- |\n"

        for item in item_list:
            name = item.get("name", "")
            version = item.get("version", "")
            desc = item.get("description", "")
            homepage = item.get("homepage", "")
            url = item.get("url", "")

            home_str = f"[主页]({homepage})" if homepage.strip() else ""
            down_str = f"[下载]({url})" if url.strip() else ""

            md_content += f"| {name} | {version} | {desc} | {home_str} | {down_str} |\n"
        md_content += "\n"

    # 保存文件
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"✅ 分组转换完成！Markdown 文件已保存：{md_file}")

if __name__ == "__main__":
    
    #unpack_json("./setting/github.json")
    # unpack_json("./setting/dotnet.json")
    # unpack_json("./setting/soft.json")
    #unpack_json("./setting/crx.json")
    # unpack_json("./setting/crack.json")
    # unpack_json()

    # pack_json()

    merge_json()
    json_to_markdown()