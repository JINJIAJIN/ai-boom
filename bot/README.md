# AI引爆项目 - BOT架构

## 系统架构

```
搜索BOT (hermes_monitor.py)
  ├─ 每天 8:00/12:00/18:00 自动搜索
  ├─ 来源: GitHub + HackerNews + AI玩法
  ├─ GLM-4-flash 大脑分析新工具
  ├─ 写入 Supabase → 网站自动更新
  ├─ 知识库 knowledge.json 积累进化
  └─ Server酱 → 推送到微信

监督BOT (hermes_supervisor.py)
  ├─ 每天 7:00 检查系统健康
  ├─ 12项检查: 数据库/Token/内存/进程/API/网站等
  └─ Server酱 → 推送健康报告到微信
```

## 部署位置
- 服务器: 115.175.143.253 (Windows Server 2019, 2核2G)
- 脚本目录: C:\hermes-deploy\
- 配置文件: hermes_config.json (含密钥，不入库)
- 知识库: knowledge.json (BOT的积累)

## 恢复步骤
1. 把 bot/hermes_monitor.py 和 bot/hermes_supervisor.py 复制到服务器 C:\hermes-deploy\
2. 参考 bot/hermes_config.template.json 创建 hermes_config.json，填入真实密钥
3. 创建Windows计划任务: HERMES-Monitor (搜索BOT) 和 HERMES-Supervisor (监督BOT)
4. 运行 schtasks /run /tn HERMES-Monitor 启动
