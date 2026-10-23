# AI生成
"""
HERMES AI引爆BOT - V3 独立智能体
有自己的大脑(GLM)、自己的记忆(knowledge.json)、能进化
每天3次：搜索 → GLM创新分析 → 写入Supabase → 生成报告 → 自我进化
部署: C:\hermes-deploy\hermes_monitor.py
配置: C:\hermes-deploy\hermes_config.json
"""
import json
import time
import logging
import sys
import os
import random
from datetime import datetime, timezone, timedelta

try:
    import requests
except ImportError:
    print("缺少 requests 库")
    sys.exit(1)

# ============ 配置 ============
CONFIG_PATH = "C:/hermes-deploy/hermes_config.json"
DEFAULT_CONFIG = {
    "supabase_url": "https://wvneqcxbahkctaqjjdwv.supabase.co",
    "supabase_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind2bmVxY3hiYWhrY3RhcWpqZHd2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTA4NTE3MzYsImV4cCI6MjEwNjQyNzczNn0.X9nihTvWGIle1M4sdE9VLL4ji-b9gGKVSf7ZD-6-xMI",
    "glm_key": "0e116433766145c398ee8e3d6af09ca9",
    "glm_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    "glm_model": "glm-4-flash",
    "feishu_webhook": "",
    "serverchan_key": "",
    "search_times": ["08:00", "12:00", "18:00"],
    "report_dir": "C:/hermes-deploy/reports",
    "knowledge_file": "C:/hermes-deploy/knowledge.json",
}

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
            return cfg
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

CFG = load_config()

# ============ 日志 ============
os.makedirs("C:/hermes-deploy/reports", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('C:/hermes-deploy/hermes.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("HERMES-BOT")

# ============ Supabase ============
def supabase_insert(table, data):
    url = f"{CFG['supabase_url']}/rest/v1/{table}"
    headers = {"apikey": CFG['supabase_key'], "Authorization": f"Bearer {CFG['supabase_key']}", "Content-Type": "application/json", "Prefer": "return=minimal"}
    try:
        resp = requests.post(url, json=data, headers=headers, timeout=30)
        return resp.status_code in (200, 201)
    except:
        return False

def supabase_query(table, select="*", limit=100):
    url = f"{CFG['supabase_url']}/rest/v1/{table}?select={select}&limit={limit}"
    headers = {"apikey": CFG['supabase_key'], "Authorization": f"Bearer {CFG['supabase_key']}"}
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        return resp.json() if resp.status_code == 200 else []
    except:
        return []

def get_existing_names():
    tools = supabase_query("ai_tools", select="name", limit=500)
    return {t.get("name", "").lower() for t in tools if t.get("name")}

# ============ 搜索源 ============
def search_github():
    results = []
    try:
        resp = requests.get("https://api.github.com/search/repositories",
            params={"q": "AI agent OR LLM OR AI tool", "sort": "stars", "order": "desc", "per_page": 10},
            timeout=30, headers={"User-Agent": "HERMES-BOT-V3"})
        if resp.status_code == 200:
            for item in resp.json().get("items", [])[:5]:
                results.append({"name": item.get("full_name",""), "description": item.get("description","") or "",
                    "url": item.get("html_url",""), "category": "Agent框架", "source": "GitHub",
                    "stars": item.get("stargazers_count",0)})
            logger.info(f"  GitHub: {len(results)}个")
    except Exception as e:
        logger.error(f"  GitHub失败: {e}")
    return results

def search_hn():
    results = []
    try:
        resp = requests.get("https://hn.algolia.com/api/v1/search",
            params={"query": "AI tool OR LLM OR AI agent", "tags": "story", "hitsPerPage": 10}, timeout=20)
        if resp.status_code == 200:
            for hit in resp.json().get("hits", [])[:5]:
                title = hit.get("title","")
                results.append({"name": title[:100], "description": f"HN热门: {title}",
                    "url": hit.get("url","") or f"https://news.ycombinator.com/item?id={hit.get('objectID','')}",
                    "category": "AI模型", "source": "HackerNews", "stars": hit.get("points",0)})
            logger.info(f"  HN: {len(results)}条")
    except:
        pass
    return results

def search_producthunt():
    results = []
    try:
        resp = requests.get("https://hn.algolia.com/api/v1/search",
            params={"query": "AI product launch OR AI tool launch", "tags": "story", "hitsPerPage": 5}, timeout=20)
        if resp.status_code == 200:
            for hit in resp.json().get("hits", [])[:3]:
                title = hit.get("title","")
                results.append({"name": title[:100], "description": f"产品发布: {title}",
                    "url": hit.get("url","") or "", "category": "内容创作", "source": "ProductNews",
                    "stars": hit.get("points",0)})
            logger.info(f"  产品新闻: {len(results)}条")
    except:
        pass
    return results

def search_ai_news():
    results = []
    try:
        for query in ["AI use case", "AI workflow tips", "AI hack"]:
            resp = requests.get("https://hn.algolia.com/api/v1/search",
                params={"query": query, "tags": "story", "hitsPerPage": 3}, timeout=15)
            if resp.status_code == 200:
                for hit in resp.json().get("hits", [])[:2]:
                    title = hit.get("title","")
                    if title and title not in [r["name"] for r in results]:
                        results.append({"name": title[:100], "description": f"AI玩法: {title}",
                            "url": hit.get("url","") or "", "category": "新手/副业",
                            "source": "AI玩法", "stars": hit.get("points",0)})
        logger.info(f"  AI玩法资讯: {len(results)}条")
    except:
        pass
    return results

def categorize(name, desc):
    text = (name + " " + desc).lower()
    cats = {"agent":"Agent框架","llm":"AI模型","coding":"AI编程","image":"内容创作",
            "video":"内容创作","platform":"平台/云","副业":"新手/副业","入门":"新手/副业",
            "automation":"新手/副业","workflow":"新手/副业","voice":"内容创作","tts":"内容创作"}
    for k, v in cats.items():
        if k in text:
            return v
    return "其他"

# ============ BOT大脑：GLM创新分析 ============
def load_knowledge():
    if os.path.exists(CFG['knowledge_file']):
        with open(CFG['knowledge_file'], "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "ideas": [],           # 积累的创新想法
        "tools_learned": 0,    # 学习过的工具数
        "categories_seen": {}, # 分类统计
        "trends": [],          # 趋势观察
        "evolution_log": [],   # 进化日志
        "personality": "好奇、务实、喜欢跨界组合",  # BOT性格（会进化）
        "last_update": "",
    }

def save_knowledge(kb):
    with open(CFG['knowledge_file'], "w", encoding="utf-8") as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)

def glm_chat(prompt, system_prompt=None):
    """调用GLM API"""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    try:
        resp = requests.post(CFG['glm_url'], json={
            "model": CFG['glm_model'],
            "messages": messages,
            "max_tokens": 800,
            "temperature": 0.85
        }, headers={
            "Authorization": f"Bearer {CFG['glm_key']}",
            "Content-Type": "application/json"
        }, timeout=45)
        
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        else:
            logger.warning(f"  GLM返回: {resp.status_code} {resp.text[:100]}")
            return None
    except Exception as e:
        logger.error(f"  GLM调用失败: {e}")
        return None

def creative_analysis(new_tools, kb):
    """BOT用GLM大脑做创新分析"""
    if not new_tools:
        return [], ""
    
    # 构造工具列表
    tools_desc = "\n".join([f"- {t['name']} ({t['category']}): {t['description'][:100]}" for t in new_tools])
    
    # 构造历史知识摘要
    recent_ideas = kb["ideas"][-5:] if kb["ideas"] else []
    history = "\n".join([f"- {idea.get('idea','')[:80]}" for idea in recent_ideas]) if recent_ideas else "暂无"
    
    # 构造分类统计
    cat_stats = kb.get("categories_seen", {})
    cat_summary = ", ".join([f"{k}:{v}" for k,v in sorted(cat_stats.items(), key=lambda x:-x[1])[:5]])
    
    system_prompt = f"""你是AI引爆BOT，一个有创新思维的AI顾问助手。
你的性格：{kb.get('personality','好奇、务实')}
你的使命：为中国小企业和个人创业者发现AI新工具，生成具体可执行的创新玩法。

你已学习{kb.get('tools_learned',0)}个工具，积累{len(kb.get('ideas',[]))}条创意。
你关注的趋势：{', '.join(kb.get('trends',[])[:3]) if kb.get('trends') else '刚开始学习'}

要求：
1. 每个工具给2-3个创新碰撞想法，要具体、可执行、有成本估算
2. 想法要跨界，不要老套
3. 面向中国用户，考虑国内环境
4. 附带一个趋势观察"""

    prompt = f"""新发现的AI工具：
{tools_desc}

你最近的创意（避免重复）：
{history}

分类分布：{cat_summary}

请分析这些工具，返回JSON格式：
{{
  "ideas": [
    {{"tool": "工具名", "category": "分类", "idea": "创新玩法描述", "cost": "成本估算", "difficulty": "入门/进阶/高级"}}
  ],
  "trend": "本轮趋势观察（一句话）",
  "self_reflection": "对自己分析的反思（一句话）"
}}"""

    result = glm_chat(prompt, system_prompt)
    
    if result:
        # 尝试解析JSON
        try:
            start = result.find("{")
            end = result.rfind("}") + 1
            if start >= 0 and end > start:
                parsed = json.loads(result[start:end])
                ideas = parsed.get("ideas", [])
                trend = parsed.get("trend", "")
                reflection = parsed.get("self_reflection", "")
                
                # 标记来源
                for idea in ideas:
                    idea["mode"] = "GLM"
                    idea["timestamp"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
                
                logger.info(f"  🧠 GLM生成{len(ideas)}条创意")
                return ideas, trend + " | " + reflection
        except json.JSONDecodeError:
            logger.warning("  GLM返回非JSON，使用原始文本")
            # 降级：把整个返回当作一条创意
            return [{"tool": new_tools[0]["name"], "category": "综合", "idea": result[:300], "mode": "GLM-raw"}], ""
    
    # GLM失败，降级到模板
    logger.warning("  GLM分析失败，降级模板模式")
    return template_analysis(new_tools), ""

def template_analysis(new_tools):
    """模板降级模式"""
    templates = {
        "Agent框架": ["用{t}搭建自动客服，7x24响应", "用{t}做竞品情报自动化监控"],
        "AI模型": ["用{t}批量生成文案，一天100条", "用{t}做数据分析，丢Excel出报告"],
        "AI编程": ["用{t}让运营也能写脚本", "用{t}快速搭MVP，1天上线"],
        "内容创作": ["用{t}做商品主图，省设计费", "用{t}生成短视频素材"],
        "新手/副业": ["用{t}开启AI副业", "用{t}自动化重复工作，每天省2小时"],
        "其他": ["关注{t}，可能是下一个风口"],
    }
    ideas = []
    for tool in new_tools:
        cat = tool.get("category", "其他")
        for tmpl in templates.get(cat, templates["其他"]):
            ideas.append({"tool": tool["name"], "category": cat, "idea": tmpl.format(t=tool["name"][:30]), "mode": "模板"})
    return ideas

# ============ BOT进化机制 ============
def evolve(kb, new_tools, ideas, trend):
    """BOT自我进化"""
    # 1. 积累创意
    kb["ideas"].extend(ideas)
    kb["ideas"] = kb["ideas"][-200:]  # 保留最近200条
    
    # 2. 更新工具计数
    kb["tools_learned"] += len(new_tools)
    
    # 3. 更新分类统计
    for t in new_tools:
        cat = t.get("category", "其他")
        kb["categories_seen"][cat] = kb["categories_seen"].get(cat, 0) + 1
    
    # 4. 更新趋势
    if trend:
        kb["trends"].append(trend[:100])
        kb["trends"] = kb["trends"][-20:]  # 保留最近20条趋势
    
    # 5. 进化日志
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    kb["evolution_log"].append({
        "time": now,
        "new_tools": len(new_tools),
        "ideas_generated": len(ideas),
        "total_tools": kb["tools_learned"],
    })
    kb["evolution_log"] = kb["evolution_log"][-50:]  # 保留最近50次
    
    # 6. 性格进化（每50个工具调整一次）
    if kb["tools_learned"] > 0 and kb["tools_learned"] % 50 == 0:
        top_cats = sorted(kb["categories_seen"].items(), key=lambda x: -x[1])[:3]
        kb["personality"] = f"好奇、务实、擅长{'/'.join([c[0] for c in top_cats])}领域"
    
    kb["last_update"] = now
    save_knowledge(kb)
    return kb

# ============ 报告生成 ============
def generate_report(stats, ideas, trend, kb):
    now = datetime.now(timezone(timedelta(hours=8)))
    lines = [
        f"# 🔥 AI引爆日报 {now.strftime('%Y-%m-%d %H:%M')}",
        f"",
        f"## 📊 本轮搜索",
        f"- 搜索源: GitHub + HackerNews + AI玩法",
        f"- 发现: {stats['total_found']}条 | 新增: {stats['new_added']}条 | 数据库总计: {stats['db_total']}条",
        f"- BOT已学习: {kb.get('tools_learned',0)}个工具 | 积累: {len(kb.get('ideas',[]))}条创意",
        f"",
    ]
    
    if stats['new_tools']:
        lines.append("## 🆕 新发现工具")
        for i, t in enumerate(stats['new_tools'], 1):
            lines.append(f"{i}. **{t['name']}** ({t['category']}) - {t['source']}")
        lines.append("")
    
    if ideas:
        lines.append("## 💡 创新碰撞（BOT想法）")
        for i, idea in enumerate(ideas, 1):
            cost = idea.get("cost", "")
            diff = idea.get("difficulty", "")
            extra = f" [成本:{cost}]" if cost else ""
            extra += f" [{diff}]" if diff else ""
            lines.append(f"{i}. {idea['idea']}{extra}")
        lines.append("")
    
    if trend:
        lines.append("## 📈 BOT趋势观察")
        lines.append(f"> {trend}")
        lines.append("")
    
    if stats['category_stats']:
        lines.append("## 📊 数据库分布")
        for cat, count in sorted(stats['category_stats'].items(), key=lambda x: -x[1]):
            lines.append(f"- {cat}: {count}")
        lines.append("")
    
    mode = "GLM AI" if CFG.get('glm_key') else "模板模式"
    lines.append(f"---")
    lines.append(f"BOT大脑: {mode} | 性格: {kb.get('personality','')} | 进化次数: {len(kb.get('evolution_log',[]))}")
    
    return "\n".join(lines)

def save_report(text):
    try:
        os.makedirs(CFG['report_dir'], exist_ok=True)
        now = datetime.now(timezone(timedelta(hours=8)))
        filepath = os.path.join(CFG['report_dir'], f"report_{now.strftime('%Y-%m-%d_%H-%M')}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        with open(os.path.join(CFG['report_dir'], "latest.md"), "w", encoding="utf-8") as f:
            f.write(text)
        logger.info(f"  报告已保存")
    except Exception as e:
        logger.error(f"  保存报告失败: {e}")

# ============ Server酱微信推送 ============
def push_serverchan(title, content):
    """通过Server酱推送到微信"""
    key = CFG.get("serverchan_key", "")
    if not key:
        logger.info("  Server酱未配置，跳过微信推送")
        return False
    try:
        url = f"https://sctapi.ftqq.com/{key}.send"
        resp = requests.post(url, data={"title": title[:100], "desp": content[:3000]}, timeout=10)
        if resp.status_code == 200 and "SUCCESS" in resp.text:
            logger.info("  微信推送成功")
            return True
        else:
            logger.warning(f"  微信推送失败: {resp.status_code}")
            return False
    except Exception as e:
        logger.error(f"  微信推送错误: {e}")
        return False

# ============ 主搜索周期 ============
def run_cycle():
    logger.info("=" * 50)
    logger.info(f"🔥 BOT开始工作 - {datetime.now(timezone(timedelta(hours=8))).strftime('%H:%M')}")
    
    # 搜索
    all_results = []
    all_results.extend(search_github())
    all_results.extend(search_hn())
    all_results.extend(search_producthunt())
    all_results.extend(search_ai_news())
    logger.info(f"共找到 {len(all_results)} 条")
    
    if not all_results:
        logger.info("本轮无搜索结果")
        return
    
    # 去重+分类
    existing = get_existing_names()
    new_tools = []
    for tool in all_results:
        if tool["name"].lower() not in existing:
            tool["category"] = categorize(tool["name"], tool["description"])
            new_tools.append(tool)
            existing.add(tool["name"].lower())
    
    logger.info(f"新增 {len(new_tools)} 个工具")
    
    # 写入Supabase
    inserted = 0
    for tool in new_tools:
        now_iso = datetime.now(timezone(timedelta(hours=8))).isoformat()
        tool_id = tool["name"].lower().replace(" ","-").replace("/","-")[:50]
        data = {
            "id": tool_id, "name": tool["name"][:200], "full_name": tool["name"][:200],
            "category": tool["category"], "summary": tool["description"][:500],
            "detail": f"来源: {tool['source']} | URL: {tool['url']}",
            "tags": [tool["source"], tool["category"]], "stars": str(tool.get("stars",0)),
            "status": "新发现", "created_at": now_iso, "updated_at": now_iso,
        }
        if supabase_insert("ai_tools", data):
            inserted += 1
        time.sleep(0.5)
    
    # GLM创新分析
    kb = load_knowledge()
    ideas, trend = creative_analysis(new_tools, kb)
    
    # BOT进化
    kb = evolve(kb, new_tools, ideas, trend)
    
    # 生成报告
    cat_stats = {}
    for t in supabase_query("ai_tools", select="category", limit=500):
        c = t.get("category","其他")
        cat_stats[c] = cat_stats.get(c, 0) + 1
    
    stats = {
        "total_found": len(all_results), "new_added": inserted,
        "db_total": sum(cat_stats.values()),
        "new_tools": [{"name":t["name"][:50],"category":t["category"],"source":t["source"]} for t in new_tools],
        "category_stats": cat_stats,
    }
    
    report = generate_report(stats, ideas, trend, kb)
    save_report(report)

    # 推送到微信
    push_title = f"AI引爆日报 - 新增{inserted}个工具"
    push_serverchan(push_title, report)

    logger.info(f"BOT完成: 搜索{len(all_results)}条, 新增{inserted}条, 创意{len(ideas)}条, 累计学习{kb['tools_learned']}个工具")

# ============ 定时调度 ============
def get_next_run_time():
    now = datetime.now(timezone(timedelta(hours=8)))
    today_times = []
    for t in CFG['search_times']:
        h, m = map(int, t.split(":"))
        target = now.replace(hour=h, minute=m, second=0, microsecond=0)
        today_times.append(target)
    for t in today_times:
        if t > now:
            return t
    return today_times[0] + timedelta(days=1)

def main():
    logger.info("=" * 50)
    logger.info("🔥 HERMES BOT V3 启动 - 独立AI引爆智能体")
    logger.info(f"大脑: GLM ({CFG['glm_model']})")
    logger.info(f"搜索时间: {CFG['search_times']}")
    logger.info(f"知识库: {CFG['knowledge_file']}")
    logger.info("=" * 50)
    
    # 启动先跑一轮
    run_cycle()
    
    while True:
        next_run = get_next_run_time()
        now = datetime.now(timezone(timedelta(hours=8)))
        wait_seconds = (next_run - now).total_seconds()
        logger.info(f"下次运行: {next_run.strftime('%Y-%m-%d %H:%M')} (等待{wait_seconds/3600:.1f}小时)")
        time.sleep(wait_seconds + 1)
        try:
            run_cycle()
        except Exception as e:
            logger.error(f"BOT异常: {e}")

if __name__ == "__main__":
    main()
