import re
import requests

# ==========================================
# 功能：根据 插件ID / 应用商店链接 自动获取 CRX 下载直链
# 完全复刻 lixian.online 仓库的核心逻辑
# ==========================================

def get_extension_id(input_str):
    """
    从链接或字符串中提取 32 位 Chrome 扩展 ID
    复刻仓库的正则逻辑
    """
    # 匹配商店URL最后的ID
    match = re.search(r'/([a-z0-9]{32})$', input_str.strip())
    if match:
        return match.group(1)
    
    # 直接判断是否是纯32位ID
    if re.match(r'^[a-z0-9]{32}$', input_str.strip()):
        return input_str.strip()
    
    return None


def get_crx_download_link(ext_id):
    """
    构造谷歌官方接口，获取真实CRX下载地址
    完全复刻 lixian.online 接口参数
    """
    api_url = "https://clients2.google.com/service/update2/crx"
    
    params = {
        "response": "redirect",
        "acceptformat": "crx2,crx3",  # 必须！新版Chrome必备
        "prodversion": "130.0.0.0",
        "x": f"id={ext_id}&uc"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    # 不自动跟随重定向，拿到真实下载地址
    resp = requests.get(
        api_url,
        params=params,
        headers=headers,
        allow_redirects=False
    )

    if resp.status_code == 302:
        return resp.headers.get("Location")  # 真实CRX直链
    return None


def download_crx(file_url, save_name="extension.crx"):
    """下载CRX文件"""
    resp = requests.get(file_url, stream=True, timeout=20)
    with open(save_name, "wb") as f:
        for chunk in resp.iter_content(8192):
            f.write(chunk)
    print(f"✅ 下载完成：{save_name}")


# ======================
# 你只需要改这里！
# ======================
if __name__ == "__main__":
    # 你要下载的插件ID / 商店链接
    user_input = "hdokiejnpimakedhajhdlcegeplioahd"  # LastPass

    ext_id = get_extension_id(user_input)
    if not ext_id:
        print("❌ 无法识别扩展ID")
        exit()

    print(f"🔍 提取到扩展ID：{ext_id}")

    crx_url = get_crx_download_link(ext_id)
    if crx_url:
        print(f"✅ 真实CRX直链：\n{crx_url}")
        download_crx(crx_url, f"{ext_id}.crx")
    else:
        print("❌ 获取直链失败")