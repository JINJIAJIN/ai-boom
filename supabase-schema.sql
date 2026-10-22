-- AI引爆 数据库建表脚本
-- 在 Supabase Dashboard → SQL Editor 中运行此脚本
-- 不会影响你已有的小程序表

-- ===== 1. 建表 =====

-- AI工具表
CREATE TABLE IF NOT EXISTS ai_tools (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  full_name TEXT,
  category TEXT NOT NULL,
  lang TEXT,
  maker TEXT,
  status TEXT,
  stars TEXT,
  license TEXT,
  summary TEXT NOT NULL,
  detail TEXT,
  pros JSONB DEFAULT '[]'::jsonb,
  cons JSONB DEFAULT '[]'::jsonb,
  tags JSONB DEFAULT '[]'::jsonb,
  compare_with JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI术语表
CREATE TABLE IF NOT EXISTS ai_terms (
  id SERIAL PRIMARY KEY,
  term TEXT NOT NULL,
  full_name TEXT,
  description TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 场景表
CREATE TABLE IF NOT EXISTS ai_scenarios (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  tools JSONB DEFAULT '[]'::jsonb,
  description TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===== 2. 开启公开读权限（RLS）=====

-- ai_tools
ALTER TABLE ai_tools ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_read_ai_tools" ON ai_tools FOR SELECT USING (true);
CREATE POLICY "auth_write_ai_tools" ON ai_tools FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- ai_terms
ALTER TABLE ai_terms ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_read_ai_terms" ON ai_terms FOR SELECT USING (true);
CREATE POLICY "auth_write_ai_terms" ON ai_terms FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- ai_scenarios
ALTER TABLE ai_scenarios ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_read_ai_scenarios" ON ai_scenarios FOR SELECT USING (true);
CREATE POLICY "auth_write_ai_scenarios" ON ai_scenarios FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- ===== 3. 插入初始数据 =====

-- 工具数据
INSERT INTO ai_tools (id, name, full_name, category, lang, maker, status, stars, license, summary, detail, pros, cons, tags, compare_with) VALUES
('hermes', 'HERMES', NULL, 'agent', 'Python', 'Nous Research', '生产可用', '251K', 'MIT', '越用越聪明的自托管Agent，自动写技能文件复用', '核心卖点是闭环学习：完成复杂任务后自动写可复用技能文件，下次直接调用。三层记忆：技能文件+会话搜索+用户建模。40+内置工具，支持400+模型，$5/月VPS即可跑。', '["自动学习进化","完全自托管","多平台消息","MIT免费"]', '["系统提示较大","无中文渠道","非建站工具"]', '["自托管","闭环学习","个人助手"]', '["dsh","openclaw","officeace"]'),
('dsh', 'DSH', 'DeepSeek Harness', 'agent', 'TypeScript', 'DeepSeek AI', '⚠️ 预览版', '243K', 'MIT', '一切皆插件的运行时，每个组件可替换', '基于Cordis框架，模型/工具/沙箱/存储/循环/UI全部是可替换插件。追加日志记录所有事件，可回放和分叉。Web UI在localhost:3080。', '["极致可组合","系统提示最省","Web UI可视化","会话回放"]', '["Developer Preview","有breaking changes","非生产就绪"]', '["插件化","运行时","预览版"]', '["hermes","openclaw"]'),
('openclaw', 'OpenClaw', NULL, 'agent', 'TypeScript', 'OpenClaw Foundation', '生产可用', '391K', 'MIT', '最广渠道覆盖的Agent网关，22+消息平台', '一个Gateway连接Discord/Slack/Telegram/WhatsApp/iMessage/Teams/WeChat/QQ/Feishu等22+渠道。Live Canvas可视化工作区。', '["渠道最广","原生多端App","Live Canvas"]', '["早期有安全漏洞","无自动技能创建"]', '["多渠道","网关","可视化"]', '["hermes","dsh","officeace"]'),
('officeace', '果办 OfficeAce', NULL, 'agent', NULL, '果办团队', '生产可用', NULL, '商业', '商业化Agent平台，中文生态+技能市场+多渠道', '开箱即用的Agent平台，内置技能市场、MCP连接器、定时任务、知识库。支持飞书/微信/钉钉/小艺四渠道。', '["原生中文","开箱即用","技能市场","国内四渠道"]', '["云端SaaS非自托管","渠道有限"]', '["中文","平台","SaaS"]', '["hermes","openclaw"]'),
('langgraph', 'LangGraph', NULL, 'agent', 'Python', 'LangChain', '生产可用', NULL, 'MIT', '图式编排框架，节点=步骤，边=控制流', 'Agent工作流建模为有向图：节点是计算步骤，边定义流转。支持分支、循环、人机交互检查点。', '["精确控制流","检查点恢复","600+集成"]', '["学习曲线陡","比单Agent重"]', '["图编排","多Agent"]', '["crewai"]'),
('crewai', 'CrewAI', NULL, 'agent', 'Python', '社区', '生产可用', NULL, 'MIT', '角色制多Agent协作，定义团队分工干活', '声明式定义Agent角色、目标和任务，组成Crew协作完成。', '["角色制直观","上手快"]', '["复杂控制流受限"]', '["多Agent","角色制"]', '["langgraph"]'),
('gpt5', 'GPT-5.x', NULL, 'model', NULL, 'OpenAI', '商业', NULL, '闭源', 'OpenAI旗舰模型，通用最强之一', 'OpenAI最新旗舰大模型，多模态支持，工具调用能力强。', '["通用能力强","多模态","生态成熟"]', '["闭源","API付费","国内访问受限"]', '["闭源","多模态"]', '["claude","deepseek"]'),
('claude', 'Claude Opus/Sonnet', NULL, 'model', NULL, 'Anthropic', '商业', NULL, '闭源', 'Anthropic旗舰，长文本和编码强', 'Anthropic旗舰模型，超长上下文窗口，编码和推理能力突出。', '["超长上下文","编码强","推理强"]', '["闭源","API付费"]', '["闭源","长文本"]', '["gpt5","deepseek"]'),
('deepseek', 'DeepSeek V4', NULL, 'model', NULL, 'DeepSeek', '开源', NULL, '开源', '性价比高、中文好的开源旗舰', 'DeepSeek旗舰模型，开源可自部署，中文理解强，API价格低。', '["开源","性价比高","中文好","可自部署"]', '["多模态较弱"]', '["开源","中文"]', '["gpt5","claude","qwen"]'),
('qwen', 'Qwen 通义千问', NULL, 'model', NULL, '阿里', '开源', NULL, '开源', '阿里开源，中文优化', '阿里通义千问系列，开源版本可本地部署，中文理解优秀。', '["开源","中文优秀","可本地部署"]', '["英文略弱"]', '["开源","中文"]', '["deepseek","glm"]'),
('glm', 'GLM', NULL, 'model', NULL, '智谱AI', '开源', NULL, '开源', '智谱AI模型，中文和代码', '智谱AI的GLM系列模型，中文和代码能力突出。', '["中文好","代码能力","开源"]', '["国际知名度较低"]', '["开源","中文"]', '["qwen","deepseek"]'),
('cursor', 'Cursor', NULL, 'coding', NULL, 'Anysphere', '商业', NULL, '商业', 'AI原生IDE，代码补全+对话+重构', 'AI原生IDE，深度集成AI代码补全、对话式编程、智能重构。', '["AI原生体验","补全强"]', '["付费","非开源"]', '["IDE","补全"]', '["copilot","trae"]'),
('copilot', 'GitHub Copilot', NULL, 'coding', NULL, 'GitHub/MS', '商业', NULL, '商业', 'VS Code插件，代码补全', 'GitHub和微软合作的AI编程助手，VS Code集成。', '["VS Code原生","生态大"]', '["功能较基础","付费"]', '["补全","VSCode"]', '["cursor","trae"]'),
('trae', 'TRAE', NULL, 'coding', NULL, '字节跳动', '免费', NULL, '免费', '字节AI原生IDE，中文理解强', '字节跳动出品的AI原生IDE，免费基础版，中文理解强。', '["免费","中文好","AI原生"]', '["较新","生态待发展"]', '["IDE","中文","免费"]', '["cursor","copilot"]'),
('midjourney', 'Midjourney', NULL, 'content', NULL, 'Midjourney', '商业', NULL, '商业', 'AI绘图，文生图质量顶尖', '文生图质量最高的AI绘图工具之一。', '["画质顶尖","风格丰富"]', '["付费","闭源"]', '["文生图"]', '["dalle"]'),
('kling', '可灵 Kling', NULL, 'content', NULL, '快手', '商业', NULL, '商业', '快手AI视频，文生视频，国内可用', '快手出品的AI视频生成工具，文生视频，国内可直接使用。', '["国内可用","视频质量好"]', '["付费","闭源"]', '["文生视频","国内"]', '["sora"]'),
('sora', 'Sora', NULL, 'content', NULL, 'OpenAI', '商业', NULL, '闭源', 'OpenAI视频生成，文生视频', 'OpenAI的文生视频模型，视频质量领先。', '["视频质量领先"]', '["闭源","付费","国内受限"]', '["文生视频"]', '["kling"]'),
('elevenlabs', 'ElevenLabs', NULL, 'content', NULL, 'ElevenLabs', '商业', NULL, '商业', 'AI语音，文生语音逼真', 'AI语音合成，声音逼真度领先，支持多语言和声音克隆。', '["声音逼真","多语言","声音克隆"]', '["付费"]', '["语音合成"]', '[]'),
('openrouter', 'OpenRouter', NULL, 'platform', NULL, '第三方', '可用', NULL, NULL, '统一接入400+模型的API网关', '一个API接入400+模型，统一计费，切换模型只需改一个参数。', '["400+模型","统一API"]', '["中间层依赖"]', '["API网关"]', '[]'),
('huggingface', 'Hugging Face', NULL, 'platform', NULL, '社区', '可用', NULL, NULL, 'AI模型托管平台，GitHub for AI', '最大的AI模型托管平台，可上传/下载/试用模型。', '["模型最多","社区活跃"]', '["国内访问慢"]', '["模型托管"]', '[]')
ON CONFLICT (id) DO NOTHING;

-- 术语数据
INSERT INTO ai_terms (term, full_name, description) VALUES
('Agent', 'AI Agent', '能自主拆任务、调工具、多步执行的AI'),
('Harness', 'Agent Harness', 'Agent的骨架——管理循环、工具、记忆、调度'),
('ReAct', 'Reason+Act', 'Agent经典模式：推理→执行→看结果→再推理'),
('RAG', 'Retrieval-Augmented Generation', '检索增强生成：先搜知识库再让AI回答'),
('MCP', 'Model Context Protocol', 'AI连接外部工具的标准协议（类似USB-C for AI）'),
('A2A', 'Agent-to-Agent', 'Agent之间互相通信的协议'),
('FTS5', 'Full-Text Search 5', 'SQLite全文搜索，用于搜索历史对话'),
('Cordis', '—', 'DSH的底层框架，时空可组合编程范式'),
('Skill', '—', '可复用的过程知识文件，HERMES的核心概念'),
('Sandbox', '—', '隔离执行环境，防止AI执行危险操作伤到主机'),
('Token', '—', 'AI处理文本的最小单位，约1 token ≈ 0.75个英文单词'),
('Context Window', '—', 'AI一次能处理的最大token数'),
('Compaction', '—', '上下文压缩：对话太长时自动摘要，防止超窗口'),
('Fine-tuning', '—', '在基础模型上继续训练，让它擅长某领域'),
('RL', 'Reinforcement Learning', '强化学习：从成功/失败中学习'),
('Multi-agent', '—', '多个Agent协作完成任务'),
('Subagent', '—', '主Agent派出的子Agent，处理子任务'),
('Cron', '—', '定时任务，按时间表自动执行'),
('LLM', 'Large Language Model', '大语言模型'),
('VLM', 'Vision-Language Model', '视觉语言模型'),
('BYO', 'Bring Your Own', '自带（如BYO API Key = 自带密钥）')
ON CONFLICT DO NOTHING;

-- 场景数据
INSERT INTO ai_scenarios (title, tools, description) VALUES
('做AI垂直目录站', '["frontend-dev","officeace"]', '搜集AI工具信息→分类整理→自动更新→多渠道分发'),
('自动化内容再利用', '["officeace"]', '一篇内容→多平台格式自动生成→定时发布'),
('越用越聪明的个人助手', '["hermes"]', '部署HERMES在VPS→自动学习你的工作流→积累技能文件'),
('多Agent协作开发', '["crewai","langgraph"]', '定义角色分工→任务分配→协作完成复杂项目'),
('低成本AI编程', '["trae","deepseek"]', '免费IDE+开源模型→零成本AI辅助编程')
ON CONFLICT DO NOTHING;

-- ===== 4. 更新时间戳触发器 =====
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_ai_tools_updated ON ai_tools;
CREATE TRIGGER trigger_ai_tools_updated BEFORE UPDATE ON ai_tools
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- 完成！
SELECT 'AI引爆 数据库初始化完成！' as result;
