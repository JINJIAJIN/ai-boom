// AI生成
// AI引爆 — Supabase 配置
const SUPABASE_CONFIG = {
  url: 'https://wvneqcxbahkctaqjjdwv.supabase.co',
  anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind2bmVxY3hiYWhrY3RhcWpqZHd2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTA4NTE3MzYsImV4cCI6MjEwNjQyNzczNn0.X9nihTvWGIle1M4sdE9VLL4ji-b9gGKVSf7ZD-6-xMI',
  restUrl: 'https://wvneqcxbahkctaqjjdwv.supabase.co/rest/v1'
};

// 分类定义（前端硬编码，不需要存数据库）
const CATEGORIES = [
  { id: 'agent', name: 'Agent框架', icon: '🤖', desc: '给AI装上手脚的骨架' },
  { id: 'model', name: 'AI模型', icon: '🧠', desc: '大脑本身' },
  { id: 'coding', name: 'AI编程工具', icon: '💻', desc: '帮你写代码的' },
  { id: 'content', name: 'AI内容创作', icon: '🎨', desc: '绘图/视频/语音' },
  { id: 'platform', name: 'AI平台/云服务', icon: '☁️', desc: '模型托管和部署' },
  { id: 'term', name: '关键术语', icon: '📚', desc: '必须懂的AI名词' }
];
