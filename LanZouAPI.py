import re
import requests
import random
import json

# 关闭 SSL 警告
requests.packages.urllib3.disable_warnings()

# 随机生成IP（防封）
def Rand_IP():
    arr_1 = ["218","218","66","66","218","218","60","60","202","204","66","66","66","59","61","60","222","221","66","59","60","60","66","218","218","62","63","64","66","66","122","211"]
    ip1 = random.choice(arr_1)
    ip2 = round(random.randint(600000, 2550000) / 10000)
    ip3 = round(random.randint(600000, 2550000) / 10000)
    ip4 = round(random.randint(600000, 2550000) / 10000)
    return f"{ip1}.{ip2}.{ip3}.{ip4}"

# acw_sc__v2 解密
def acw_sc_v2_simple(arg1):
    posList = [15,35,29,24,33,16,1,38,10,9,19,31,40,27,22,23,25,13,6,11,39,18,20,8,14,21,32,26,2,30,7,4,17,5,3,28,34,37,12,36]
    mask = '3000176000856006061501533003690027800375'
    outPutList = [''] * 40
    for i, char in enumerate(arg1):
        for j, pos in enumerate(posList):
            if pos == i + 1:
                outPutList[j] = char
    arg2 = ''.join(outPutList)
    result = ''
    length = min(len(arg2), len(mask))
    for i in range(0, length, 2):
        strHex = arg2[i:i+2]
        maskHex = mask[i:i+2]
        xor = hex(int(strHex, 16) ^ int(maskHex, 16))[2:]
        result += xor.zfill(2)
    return result

# 解析主函数
def lanzou_zl(url, pwd=""):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "X-Forwarded-For": Rand_IP(),
        "Client-Ip": Rand_IP(),
        "Referer": "https://lanzoup.com/",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Upgrade-Insecure-Requests": "1"
    }

    session = requests.Session()
    session.verify = False
    session.timeout = 15

    # 自动识别域名
    match = re.search(r'https?://([a-z0-9]+\.lanzou[a-z]+\.com)/(.+)', url, re.I)
    if not match:
        return {"code": 400, "msg": "链接格式错误"}
    host = match.group(1)
    url = f"https://{host}/{match.group(2)}"

    try:
        resp = session.get(url, headers=headers)
        html = resp.text
    except:
        return {"code": 400, "msg": "网络请求失败"}

    if "文件取消分享了" in html:
        return {"code": 400, "msg": "文件取消分享了"}

    # 提取文件名
    soft_name = ""
    for pat in [
        r'style="font-size: 30px.*?">(.*?)</div>',
        r'<div class="n_box_3fn.*?">(.*?)</div>',
        r'var filename = \'(.*?)\';',
        r'div class="b"><span>(.*?)</span></div>'
    ]:
        res = re.search(pat, html, re.S)
        if res:
            soft_name = res.group(1).strip()
            break

    # 提取文件大小
    soft_size = ""
    for pat in [
        r'<div class="n_filesize.*?>大小：(.*?)</div>',
        r'<span class="p7">文件大小：</span>(.*?)<br>'
    ]:
        res = re.search(pat, html, re.S)
        if res:
            soft_size = res.group(1).strip()
            break

    # ============= 带密码 =============
    if "function down_p(){" in html:
        if not pwd:
            return {"code": 400, "msg": "请输入密码"}
        sign = re.search(r"'sign':'(.*?)'", html).group(1)
        ajaxm = re.search(r"(ajaxm\.php\?file=\d+)", html).group(1)
        api = f"https://{host}/{ajaxm}"

        data = {
            "action": "downprocess",
            "sign": sign,
            "p": pwd,
            "kd": 1
        }

        resp2 = session.post(api, data=data, headers=headers)
        try:
            res_json = resp2.json()
        except:
            return {"code": 400, "msg": "密码错误或页面已更新"}

    # ============= 无密码 =============
    else:
        iframe = re.search(r'<iframe.*?src="/([^"]+)"', html, re.S)
        if not iframe:
            return {"code": 400, "msg": "解析失败：未找到iframe"}

        ifurl = f"https://{host}/{iframe.group(1)}"
        if_html = session.get(ifurl, headers=headers).text

        try:
            wp_sign = re.search(r"wp_sign = '(.*?)'", if_html).group(1)
            ajaxm_list = re.findall(r"ajaxm\.php\?file=\d+", if_html)
            ajaxm = ajaxm_list[-1] if len(ajaxm_list) > 1 else ajaxm_list[0]
        except:
            return {"code": 400, "msg": "解析参数失败，蓝奏云已更新"}

        api = f"https://{host}/{ajaxm}"
        data = {
            "action": "downprocess",
            "websignkey": wp_sign,
            "signs": wp_sign,
            "sign": wp_sign,
            "websign": "",
            "kd": 1,
            "ves": 1
        }

        resp2 = session.post(api, data=data, headers=headers)
        
        # 关键修复：自动处理非JSON返回
        try:
            res_json = resp2.json()
        except json.decoder.JSONDecodeError:
            return {"code": 400, "msg": "蓝奏云接口返回非JSON数据，已触发反爬"}

    if res_json.get("zt") != 1:
        return {"code": 400, "msg": res_json.get("inf", "解析失败")}

    # 获取真实下载链接
    down_url1 = f"{res_json['dom']}/file/{res_json['url']}"
    resp_final = session.get(down_url1, headers=headers)

    try:
        arg1 = re.search(r"arg1='(.*?)'", resp_final.text).group(1)
        acw = acw_sc_v2_simple(arg1)
    except:
        real_url = down_url1
    else:
        headers_down = {
            **headers,
            "Cookie": f"down_ip=1; acw_sc__v2={acw}",
            "Referer": down_url1
        }
        resp_real = session.head(down_url1, headers=headers_down, allow_redirects=True)
        real_url = resp_real.url

    real_url = re.sub(r'pid=[^&]*&?', '', real_url)

    return {
        "code": 200,
        "msg": "解析成功",
        "name": soft_name,
        "filesize": soft_size,
        "downUrl": real_url
    }

# ==================== 测试 ====================
if __name__ == "__main__":
    # 无密码
    print(lanzou_zl("https://xyyx.lanzoub.com/ivYMM04hqlfe"))

    # 有密码
    # print(lanzou_zl("https://xyyx.lanzoub.com/ivYMM04hqlfe", pwd="1234"))