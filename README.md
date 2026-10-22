# 💥 AI引爆

> 搜集 · 思考 · 碰撞 · 引爆每一个AI新玩法

## 部署到 GitHub Pages（3步上线）

### 1. 在 GitHub 创建仓库
- 登录 GitHub → New Repository
- 仓库名：`ai-boom`（或你喜欢的名字）
- 设为 Public
- 勾选 "Add a README file"
- 创建

### 2. 上传文件
把以下4个文件上传到仓库根目录：
- `index.html`
- `style.css`
- `app.js`
- `data.json`

### 3. 开启 GitHub Pages
- 仓库 → Settings → Pages
- Source: Deploy from a branch
- Branch: `main` / Folder: `/ (root)`
- Save
- 等待1-2分钟，访问 `https://你的用户名.github.io/ai-boom/`

## 本地预览
```bash
cd ai-boom
python -m http.server 8080
# 浏览器打开 http://localhost:8080
```

## 文件说明
| 文件 | 作用 |
|------|------|
| index.html | 页面结构 |
| style.css | 爆炸风格样式 |
| app.js | 搜索/分类/对比/弹窗交互 |
| data.json | 所有AI工具数据（自动更新此文件即可更新网站）|

## 自动运营
data.json 是网站的数据源。Agent 定时搜索新AI工具后，更新此文件并 git push，网站自动刷新。
