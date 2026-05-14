import requests
import re
from datetime import datetime

def parseLanzouUrl(targetUrl):
    logs = []

    def addLog(message, type='info'):
        logs.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": message,
            "type": type
        })

    addLog('开始解析蓝奏云链接', 'info')
    addLog(f'目标URL: {targetUrl}', 'info')

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "Referer": "https://www.lanzou.com/"
    }

    try:
        # ============= 步骤1：获取初始页面 =============
        addLog('步骤1: 获取初始页面', 'info')
        page1Response = requests.get(targetUrl, headers=headers, timeout=10)
        
        if not page1Response.ok:
            raise Exception(f'初始页面请求失败: {page1Response.status_code}')

        page1Html = page1Response.text
        addLog('初始页面获取成功', 'success')

        # 提取下载链接
        downUrlMatch = re.search(r'<a href="([^"]+)"[^>]*id="downurl"', page1Html, re.I)
        if not downUrlMatch:
            raise Exception("无法从页面提取下载链接")

        downUrl = "https://wwi.lanzoup.com" + downUrlMatch.group(1)
        addLog(f'提取到下载链接: {downUrl}', 'success')

        # ============= 步骤2：获取第二页内容 =============
        addLog('步骤2: 获取第二页内容', 'info')
        page2Response = requests.get(downUrl, headers=headers, timeout=10)
        
        if not page2Response.ok:
            raise Exception(f'第二页请求失败: {page2Response.status_code}')

        page2Html = page2Response.text
        addLog('第二页获取成功', 'success')

        # ============= 步骤3：提取URL参数 =============
        addLog('步骤3: 提取URL参数', 'info')
        
        part1Match = re.search(r"(?:var\s+)?vkjxld\s*=\s*['\"]([^'\"]+)", page2Html, re.I)
        part2Match = re.search(r"(?:var\s+)?hyggid\s*=\s*['\"]([^'\"]+)", page2Html, re.I)

        if not part1Match or not part2Match:
            raise Exception("无法提取URL参数")

        part1 = part1Match.group(1)
        part2 = part2Match.group(1)
        
        addLog(f'提取参数: vkjxld={part1[:20]}..., hyggid={part2[:20]}...', 'success')

        finalUrl = part1 + part2
        addLog(f'拼接最终URL: {finalUrl}', 'success')
        addLog('✅ 解析完成！', 'success')

        return {"finalUrl": finalUrl, "logs": logs}

    except Exception as error:
        addLog(f'解析失败: {str(error)}', 'error')
        raise error


def parseLanzouUrl2(targetUrl, pwd=""):
    logs = []

    def addLog(msg, typ="info"):
        logs.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": msg,
            "type": typ
        })

    addLog("开始解析蓝奏云链接", "info")
    addLog(f"目标URL: {targetUrl}", "info")
    if pwd:
        addLog(f"使用密码: {pwd}", "info")

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; Pixel 4) AppleWebKit/537.36",
        "Referer": "https://www.lanzou.com/"
    }

    try:
        # ========== 步骤1：获取页面 ==========
        addLog("步骤1: 获取初始页面", "info")
        r1 = requests.get(targetUrl, headers=headers, timeout=10)
        r1.raise_for_status()
        html = r1.text
        addLog("初始页面获取成功", "success")

        # ========== 判断是否需要密码 ==========
        if "请输入密码" in html or "password" in html:
            addLog("检测到链接需要密码", "warning")
            if not pwd:
                raise Exception("该文件需要密码，请传入 pwd")

            # 安全提取参数（不会报错）
            sign = ""
            vid = ""
            action = "/ajaxm.php"
            
            sign_match = re.search(r"'sign':'([^']+)'", html)
            if sign_match:
                sign = sign_match.group(1)
            
            vid_match = re.search(r"'vid':'([^']+)'", html)
            if vid_match:
                vid = vid_match.group(1)
            
            action_match = re.search(r'action="([^"]+?)"', html)
            if action_match:
                action = action_match.group(1)

            domain = re.match(r"https?://[^/]+", targetUrl).group(0)
            api = domain + action

            addLog("提交密码验证...", "info")
            data = {
                "action": "downprocess",
                "sign": sign,
                "p": pwd,
                "vid": vid
            }

            r2 = requests.post(api, data=data, headers=headers, timeout=10)
            res = r2.json()

            if res.get("zt") != 1:
                raise Exception(f"密码错误：{res.get('info')}")

            final_url = f"https://{res['dom']}/file/{res['url']}"
            addLog("✅ 密码验证通过，解析完成！", "success")
            return {"finalUrl": final_url, "logs": logs}

        # ========== 无密码逻辑 ==========
        down_match = re.search(r'<a href="([^"]+)"[^>]*id="downurl"', html, re.I)
        if not down_match:
            raise Exception("无法从页面提取下载链接")
        down_url = "https://wwi.lanzoup.com" + down_match.group(1)
        addLog(f"提取到下载链接: {down_url}", "success")

        # 第二页
        addLog("步骤2: 获取第二页内容", "info")
        r2 = requests.get(down_url, headers=headers, timeout=10)
        r2.raise_for_status()
        html2 = r2.text
        addLog("第二页获取成功", "success")

        # 安全提取参数（关键修复！）
        addLog("步骤3: 提取URL参数", "info")
        m1 = re.search(r'vkjxld\s*=\s*[\'"]([^\'"]+)', html2, re.I)
        m2 = re.search(r'hyggid\s*=\s*[\'"]([^\'"]+)', html2, re.I)
        
        if not m1 or not m2:
            # 新版蓝奏云格式
            file_match = re.search(r'https?://[^\s"<>]+?/file/[^\s"<>]+', html2)
            if file_match:
                final_url = file_match.group(0)
                addLog("新版直链匹配成功", "success")
            else:
                raise Exception("无法提取URL参数")
        else:
            part1 = m1.group(1)
            part2 = m2.group(1)
            final_url = part1 + part2

        addLog("✅ 解析完成！", "success")
        return {"finalUrl": final_url, "logs": logs}

    except Exception as e:
        addLog(f"解析失败: {str(e)}", "error")
        return {"finalUrl": "", "logs": logs, "error": str(e)}
if __name__ == "__main__":
    # 调用
    result = parseLanzouUrl("https://52ybcj.lanzouw.com/i05RT3nfrg1g")
    # 输出直链
    print("直链：", result["finalUrl"])