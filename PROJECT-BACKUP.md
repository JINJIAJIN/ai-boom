# AI引爆项目 — 聊天重点备份

> 备份时间：2026-10-23 03:33（最终版）
> 参与者：用户(CVO/金佳金) + Agent(小通/glm-5.2)
> 下次继续：从"第七节后续待办"开始，HERMES部署是第一优先级

---

## 一、项目目标

做一个 **AI垂直类的归类整理网站**，是一个能搜集、思考、碰撞新玩法、更新、罗列场景的AGENT，需要自动运营。

完整产线：
- **PA1**（监控学习→知识库）✅ 已完成
- **PA2**（整理归类→自动更新网站→公众号推送→视频剪辑发送）待做

---

## 二、关键决策记录

| 时间 | 决策 | 原因 |
|------|------|------|
| 10/22 14:35 | 产品定名"AI引爆" | 用户要求"爆炸一点" |
| 10/22 14:35 | 部署GitHub Pages | 免费、永久访问 |
| 10/22 21:20 | 架构：果办做大脑+HERMES做手脚 | 用户主动提出，互补 |
| 10/22 21:30 | 数据库用Supabase | 用户已有项目，免费额度够用 |
| 10/23 00:41 | 本机先部署验证 | 快速验证功能 |
| 10/23 01:17 | 定时任务每天8点自动搜集 | 0成本自动运营 |
| 10/23 02:25 | GitHub Pages上线 | 永久公开访问 |

---

## 三、技术架构

```
自动搜集层（每天8点）
  → web_search 搜6路AI新工具
  → fetch_webpage 抓正文
  → 分析归类去重
  → 写入 Supabase
    ↓
数据层（Supabase PostgreSQL）
  → ai_tools 表（20+工具）
  → ai_terms 表（21术语）
  → ai_scenarios 表（5场景）
    ↓
展示层（GitHub Pages静态站）
  → index.html + style.css + app.js + config.js
  → 实时从Supabase REST API读数据
  → 搜索/分类/对比/详情弹窗
```

### Supabase 配置
- Project URL: `https://wvneqcxbahkctaqjjdwv.supabase.co`
- 三张表：`ai_tools`（TEXT主键）、`ai_terms`（SERIAL主键）、`ai_scenarios`（SERIAL主键）
- RLS策略：anon可公开SELECT+INSERT
- 列名注意：`full`和`desc`是PostgreSQL保留字，用`full_name`和`description`代替

### 文件结构
```
ai-boom/
  index.html       — 页面结构
  style.css        — 爆炸风格（暗色+霓虹橙）
  app.js           — 交互逻辑（从Supabase读数据）
  config.js        — Supabase配置+分类定义
  data.json        — 备用数据（Supabase挂了回退）
  supabase-schema.sql — 建表脚本
  README.md        — 部署指南
```

---

## 四、自动搜集关键词

| 分类 | 关键词 |
|------|--------|
| Agent框架 | AI agent framework 2026 new、LLM agent 开源、agent 自托管 |
| AI模型 | new LLM release 2026 open source、多模态模型 |
| AI编程 | AI coding tool IDE 2026、AI编程工具 |
| 内容创作 | AI image video generation tool 2026、文生视频、AI绘图 |
| 平台/云 | AI platform launch、model hosting、AI API gateway |
| 新手/副业 | AI副业实操、AI工具入门教程、AI workflow automation beginner |

搜索来源：GitHub trending、Product Hunt、Hacker News、36kr/机器之心、掘金、Reddit

---

## 五、重要纪律和教训

### 5.1 Agent行为纪律
1. **能自动跑的就不问用户** — 部署类操作直接用API一把梭，只在需要凭证或方向决策时才打断用户
2. **说老实话** — 不夸大能力，数据库✅但真·自我进化❌（笔记本级别非真进化）
3. **安全边界** — 涉及对外发送消息、删除内容、修改文件等操作，必须先征得用户同意
4. **P2原则** — SOP写了下一步→直接做，不问；方向不确定/阻塞→才升级

### 5.2 技术教训
1. **PostgreSQL保留字** — `full`和`desc`都是保留字，建表时不能用，改用`full_name`和`description`
2. **Supabase RLS** — 光开RLS策略不够，还要`GRANT SELECT ON 表名 TO anon`才行
3. **Git安装** — winget装Git需要管理员权限，可能超时；装在C盘不影响使用
4. **GitHub部署** — 应该一开始就要token，用API自动创建仓库+开Pages，不要让用户手动操作5步

### 5.3 用户偏好
- 用户是AI新手，偏好可视化/Web UI操作
- 不想自己写代码
- 要老实话，别瞎说
- 网站名要"爆炸一点"
- 评分标准：5维各2分=10分（自动化/变现/竞争/合规/启动成本）
- 月成本<300元
- 搜索范围：海外+国内都要

---

## 六、能力边界（诚实评估）

### Agent（果办）能做到
- ✅ 建站、改代码、部署
- ✅ 定时搜索+写入数据库（被触发时）
- ✅ 公众号推送、视频剪辑
- ✅ 中文生态、现成技能

### Agent做不到
- ❌ 24/7常驻运行（只能被定时触发）
- ❌ 真·自我进化（不能升级模型、不能自动写技能文件）
- ❌ 爬小红书/公众号（封闭平台反爬）

### HERMES能做到（但还没部署）
- ✅ 24/7常驻运行
- ✅ 自动学习写技能文件
- ❌ 中文渠道、现成建站技能

---

## 七、后续待办

| 优先级 | 事项 | 状态 | 依赖 |
|--------|------|------|------|
| P1 | HERMES部署到服务器 | ⏳阻塞 | 华为云安全组22端口已开，SSH已通，但本机SSH密码传递有问题，明天解决 |
| P1 | 观察自动搜集效果 | 进行中 | 无 |
| P2 | 公众号推送集成 | 待做 | 需AppID+AppSecret |
| P2 | 视频生产管线 | 待做 | 需选路线 |
| P3 | 网站加新手路线图板块 | 待做 | 无 |

### HERMES部署阻塞详情（2026-10-23 03:33）
- 服务器：115.175.143.253，Windows Server 2019，2核2G 40G
- SSH服务：已开启（sshd running）
- SSH密码：已重置为 Jin900616（Administrator用户）
- 华为云安全组：22端口已放行（用户已操作）
- 端口测试：TCP连接成功（Port 22: OPEN）
- 阻塞原因：本机通过plink/ssh连接服务器时，主机密钥确认和密码传递在Windows环境下卡住
- 解决方案：明天可尝试①用code工具的Python环境装paramiko ②服务器上直接跑部署脚本 ③用ssh-keygen生成密钥对免密登录
- 部署文件已准备好：docker/Dockerfile, docker/hermes-config.yaml, docker/docker-compose.yml

---

## 八、关键网址

| 用途 | 网址 |
|------|------|
| 网站公开访问 | https://jinjiajin.github.io/ai-boom/ |
| GitHub仓库 | https://github.com/JINJIAJIN/ai-boom |
| Supabase项目 | https://wvneqcxbahkctaqjjdwv.supabase.co |
| 本机访问 | http://localhost:8080（本机服务器在跑时） |

---

## 九、成本

| 项目 | 费用 |
|------|------|
| GitHub Pages | 免费 |
| Supabase | 免费（500MB额度） |
| 定时任务 | 免费（果办内置） |
| 域名 | 暂无（用GitHub默认域名） |
| **合计** | **0元/月** |

叠加HERMES后：+$5/月（VPS），总计约35元/月
