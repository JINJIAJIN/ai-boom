# AI生成
"""
HERMES 监督BOT - 每天7:00检查系统健康
检查项：数据库增长、Token用量、服务器健康、BOT存活、搜索源、网站、GLM、Server酱、知识库、错误率
部署: C:\hermes-deploy\hermes_supervisor.py
"""
import json
import time
import logging
import sys
import os
from datetime import datetime, timezone, timedelta

try:
    import requests
except ImportError:
    print("缺少 requests 库")
    sys.exit(1)

# ============ 配置 ============
CONFIG_PATH = "C:/hermes-deploy/hermes_config.json"
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

CFG = load_config()
CST = timezone(timedelta(hours=8))
NOW = datetime.now(CST)

# ============ 日志 ============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('C:/hermes-deploy/supervisor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SUPERVISOR")

# ============ 检查项 ============
checks = []

def check(name, status, detail=""):
    emoji = "OK" if status == "ok" else "WARN" if status == "warn" else "FAIL"
    checks.append({"name": name, "status": status, "detail": detail, "emoji": emoji})
    logger.info(f"  [{emoji}] {name}: {detail[:80]}")

# 1. 数据库增长
def check_database():
    try:
        url = CFG.get("supabase_url", "")
        key = CFG.get("supabase_key", "")
        headers = {"apikey": key, "Authorization": f"Bearer {key}"}
        
        resp = requests.get(f"{url}/rest/v1/ai_tools?select=id,created_at&limit=1000&order=created_at.desc", headers=headers, timeout=30)
        if resp.status_code == 200:
            tools = resp.json()
            total = len(tools)
            
            # 今天的
            today_str = NOW.strftime("%Y-%m-%d")
            today_new = sum(1 for t in tools if t.get("created_at","").startswith(today_str))
            
            # 昨天的
            yesterday = (NOW - timedelta(days=1)).strftime("%Y-%m-%d")
            yesterday_new = sum(1 for t in tools if t.get("created_at","").startswith(yesterday))
            
            if total < 30:
                check("数据库规模", "warn", f"总计{total}条，偏少")
            elif today_new == 0 and yesterday_new == 0:
                check("数据库增长", "warn", f"总计{total}条，但今天和昨天都无新增")
            else:
                check("数据库增长", "ok", f"总计{total}条，今日新增{today_new}条，昨日{yesterday_new}条")
        else:
            check("数据库连接", "fail", f"Supabase返回{resp.status_code}")
    except Exception as e:
        check("数据库连接", "fail", str(e)[:100])

# 2. Token用量
def check_tokens():
    token_log = "C:/hermes-deploy/token_log.json"
    if not os.path.exists(token_log):
        check("Token用量", "warn", "token_log.json不存在，BOT可能还没用GLM")
        return
    
    try:
        with open(token_log, "r", encoding="utf-8") as f:
            logs = json.load(f)
        
        today_str = NOW.strftime("%Y-%m-%d")
        today_tokens = sum(l.get("total_tokens", 0) for l in logs if l.get("timestamp","").startswith(today_str))
        today_calls = sum(1 for l in logs if l.get("timestamp","").startswith(today_str))
        
        # 本月
        month_str = NOW.strftime("%Y-%m")
        month_tokens = sum(l.get("total_tokens", 0) for l in logs if l.get("timestamp","").startswith(month_str))
        
        check("Token用量", "ok", f"今日{today_calls}次调用/{today_tokens}tokens，本月{month_tokens}tokens")
    except Exception as e:
        check("Token用量", "warn", f"读取失败: {e}")

# 3. 服务器健康
def check_server():
    try:
        import subprocess
        # 内存
        result = subprocess.run(["wmic", "OS", "get", "FreePhysicalMemory,TotalVisibleMemorySize", "/value"], capture_output=True, text=True, timeout=10)
        lines = result.stdout.strip().split("\n")
        free_mem = total_mem = 0
        for line in lines:
            if "FreePhysicalMemory=" in line:
                free_mem = int(line.split("=")[1])
            if "TotalVisibleMemorySize=" in line:
                total_mem = int(line.split("=")[1])
        
        if total_mem > 0:
            used_pct = (1 - free_mem / total_mem) * 100
            if used_pct > 90:
                check("服务器内存", "fail", f"已用{used_pct:.0f}%， dangerously high")
            elif used_pct > 80:
                check("服务器内存", "warn", f"已用{used_pct:.0f}%，偏高")
            else:
                check("服务器内存", "ok", f"已用{used_pct:.0f}%，空闲{free_mem//1024}MB")
        
        # 磁盘
        result2 = subprocess.run(["wmic", "logicaldisk", "where", "DeviceID='C:'", "get", "FreeSpace,Size", "/value"], capture_output=True, text=True, timeout=10)
        for line in result2.stdout.strip().split("\n"):
            if "FreeSpace=" in line:
                free_disk = int(line.split("=")[1]) // (1024**3)
            if "Size=" in line:
                total_disk = int(line.split("=")[1]) // (1024**3)
        if total_disk > 0:
            disk_pct = (1 - free_disk / total_disk) * 100
            if disk_pct > 90:
                check("磁盘空间", "fail", f"C盘已用{disk_pct:.0f}%，仅剩{free_disk}GB")
            else:
                check("磁盘空间", "ok", f"C盘已用{disk_pct:.0f}%，剩余{free_disk}GB")
    except Exception as e:
        check("服务器健康", "warn", f"检查失败: {e}")

# 4. BOT存活
def check_bot_process():
    try:
        import subprocess
        result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"], capture_output=True, text=True, timeout=10)
        lines = result.stdout.strip().split("\n")
        python_count = len([l for l in lines if "python.exe" in l])
        
        if python_count == 0:
            check("BOT进程", "fail", "没有python进程在运行！BOT可能已崩溃")
        elif python_count == 1:
            check("BOT进程", "ok", f"{python_count}个python进程运行中")
        else:
            check("BOT进程", "ok", f"{python_count}个python进程运行中")
    except Exception as e:
        check("BOT进程", "warn", f"检查失败: {e}")

# 5. 搜索源可用性
def check_search_sources():
    # GitHub
    try:
        resp = requests.get("https://api.github.com/rate_limit", timeout=10, headers={"User-Agent": "HERMES-Supervisor"})
        if resp.status_code == 200:
            remaining = resp.json()["resources"]["search"]["remaining"]
            if remaining < 5:
                check("GitHub API", "warn", f"剩余{remaining}次搜索配额")
            else:
                check("GitHub API", "ok", f"剩余{remaining}次搜索配额")
        else:
            check("GitHub API", "fail", f"返回{resp.status_code}")
    except Exception as e:
        check("GitHub API", "fail", str(e)[:50])
    
    # HN
    try:
        resp = requests.get("https://hn.algolia.com/api/v1/search?query=AI&tags=story&hitsPerPage=1", timeout=10)
        check("HackerNews API", "ok" if resp.status_code == 200 else "fail", f"状态{resp.status_code}")
    except Exception as e:
        check("HackerNews API", "fail", str(e)[:50])

# 6. 网站可访问
def check_website():
    try:
        resp = requests.get("https://jinjiajin.github.io/ai-boom/", timeout=15)
        check("网站可访问", "ok" if resp.status_code == 200 else "fail", f"HTTP {resp.status_code}")
    except Exception as e:
        check("网站可访问", "fail", str(e)[:50])

# 7. GLM API状态
def check_glm():
    key = CFG.get("glm_key", "")
    if not key:
        check("GLM API", "warn", "Key未配置")
        return
    try:
        resp = requests.post(CFG.get("glm_url", ""), json={
            "model": CFG.get("glm_model", "glm-4-flash"),
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 5
        }, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, timeout=30)
        
        if resp.status_code == 200:
            usage = resp.json().get("usage", {})
            check("GLM API", "ok", f"正常，本次消耗{usage.get('total_tokens',0)}tokens")
        else:
            check("GLM API", "fail", f"返回{resp.status_code}: {resp.text[:80]}")
    except Exception as e:
        check("GLM API", "fail", str(e)[:50])

# 8. Server酱
def check_serverchan():
    key = CFG.get("serverchan_key", "")
    if not key:
        check("Server酱", "warn", "未配置")
        return
    # 不实际发消息，只检查key格式
    if key.startswith("SCT") and len(key) > 20:
        check("Server酱", "ok", f"Key格式正常({len(key)}字符)")
    else:
        check("Server酱", "warn", "Key格式异常")

# 9. 知识库进化
def check_knowledge():
    kb_file = CFG.get("knowledge_file", "C:/hermes-deploy/knowledge.json")
    if not os.path.exists(kb_file):
        check("知识库", "warn", "knowledge.json不存在")
        return
    try:
        with open(kb_file, "r", encoding="utf-8") as f:
            kb = json.load(f)
        tools = kb.get("tools_learned", 0)
        ideas = len(kb.get("ideas", []))
        trends = len(kb.get("trends", []))
        evo = len(kb.get("evolution_log", []))
        personality = kb.get("personality", "")
        
        if tools < 10:
            check("知识库进化", "warn", f"仅学习{tools}个工具，偏少")
        else:
            check("知识库进化", "ok", f"学习{tools}工具/{ideas}创意/{trends}趋势/{evo}次进化")
    except Exception as e:
        check("知识库", "warn", str(e)[:50])

# 10. 错误率
def check_errors():
    log_file = "C:/hermes-deploy/hermes.log"
    if not os.path.exists(log_file):
        check("错误率", "warn", "hermes.log不存在")
        return
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()[-200:]  # 最近200行
        
        today_str = NOW.strftime("%Y-%m-%d")
        today_lines = [l for l in lines if today_str in l]
        errors = [l for l in today_lines if "[ERROR]" in l]
        warnings = [l for l in today_lines if "[WARNING]" in l]
        
        if len(errors) > 10:
            check("错误率", "fail", f"今日{len(errors)}个错误，{len(warnings)}个警告")
        elif len(errors) > 0:
            check("错误率", "warn", f"今日{len(errors)}个错误，{len(warnings)}个警告")
        else:
            check("错误率", "ok", f"今日0错误，{len(warnings)}个警告")
    except Exception as e:
        check("错误率", "warn", str(e)[:50])

# ============ 报告生成 ============
def generate_report():
    ok_count = sum(1 for c in checks if c["status"] == "ok")
    warn_count = sum(1 for c in checks if c["status"] == "warn")
    fail_count = sum(1 for c in checks if c["status"] == "fail")
    
    lines = [
        f"# 监督BOT日报 {NOW.strftime('%Y-%m-%d %H:%M')}",
        f"",
        f"## 总览: {ok_count}正常 / {warn_count}警告 / {fail_count}故障",
        f"",
        f"## 检查详情",
    ]
    
    for c in checks:
        lines.append(f"- [{c['emoji']}] **{c['name']}**: {c['detail']}")
    
    lines.append("")
    
    if fail_count > 0:
        lines.append("## 需要处理")
        for c in checks:
            if c["status"] == "fail":
                lines.append(f"- {c['name']}: {c['detail']}")
        lines.append("")
    
    lines.append(f"---")
    lines.append(f"监督BOT | 检查{len(checks)}项 | 服务器115.175.143.253")
    
    return "\n".join(lines)

# ============ Server酱推送 ============
def push_wechat(title, content):
    key = CFG.get("serverchan_key", "")
    if not key:
        logger.info("Server酱未配置")
        return
    try:
        resp = requests.post(f"https://sctapi.ftqq.com/{key}.send", data={"title": title[:100], "desp": content[:3000]}, timeout=10)
        if resp.status_code == 200 and "SUCCESS" in resp.text:
            logger.info("微信推送成功")
        else:
            logger.warning(f"微信推送失败: {resp.status_code}")
    except Exception as e:
        logger.error(f"推送错误: {e}")

# ============ 主函数 ============
def main():
    logger.info("=" * 50)
    logger.info(f"监督BOT启动 - {NOW.strftime('%Y-%m-%d %H:%M')}")
    logger.info("=" * 50)
    
    logger.info("检查数据库...")
    check_database()
    
    logger.info("检查Token用量...")
    check_tokens()
    
    logger.info("检查服务器健康...")
    check_server()
    
    logger.info("检查BOT进程...")
    check_bot_process()
    
    logger.info("检查搜索源...")
    check_search_sources()
    
    logger.info("检查网站...")
    check_website()
    
    logger.info("检查GLM API...")
    check_glm()
    
    logger.info("检查Server酱...")
    check_serverchan()
    
    logger.info("检查知识库...")
    check_knowledge()
    
    logger.info("检查错误率...")
    check_errors()
    
    # 生成报告
    report = generate_report()
    logger.info(f"\n{report}")
    
    # 保存报告
    report_dir = CFG.get("report_dir", "C:/hermes-deploy/reports")
    os.makedirs(report_dir, exist_ok=True)
    with open(os.path.join(report_dir, "supervisor_latest.md"), "w", encoding="utf-8") as f:
        f.write(report)
    
    # 推送微信
    fail_count = sum(1 for c in checks if c["status"] == "fail")
    title = f"监督日报: {fail_count}个故障" if fail_count > 0 else "监督日报: 全部正常"
    push_wechat(title, report)
    
    logger.info("监督BOT完成")

if __name__ == "__main__":
    main()
