# HERMES 部署指南（醒来后看这个）

## 当前状态
- AI引爆网站：✅ 已上线 https://jinjiajin.github.io/ai-boom/
- Supabase数据库：✅ 已连通
- 自动搜集定时任务：✅ 每天8点自动执行
- HERMES部署：⏳ 服务器SSH已开启，但华为云安全组22端口未放行

## 你醒来后只需做2件事

### 第1件：华为云控制台开放22端口（2分钟）
1. 打开 https://console.huaweicloud.com
2. 找到ECS服务器 → 安全组 → 配置规则
3. 添加入方向规则：TCP 端口22 源地址0.0.0.0/0
4. 确定

### 第2件：告诉我"端口开了"
我会自动SSH上去完成以下全部操作：
- 安装Docker
- 构建HERMES容器
- 配置连接Supabase
- 启动24/7监控
- 验证运行

## 服务器信息
- IP: 115.175.143.253
- 系统: Windows Server 2019
- 配置: 2核2G 40G
- SSH用户: Administrator
- SSH密码: Jin900616
- SSH端口: 22（已开启，待安全组放行）

## 部署文件位置
所有Docker部署文件已准备好：
- docker/Dockerfile — HERMES容器构建
- docker/hermes-config.yaml — HERMES配置（连Supabase）
- docker/docker-compose.yml — Docker编排

## 注意
- 服务器密码已改，建议事后更换
- HERMES需要DeepSeek API Key（部署时我会问你要）
