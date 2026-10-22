// AI生成
// AI引爆 — 交互逻辑（Supabase版）
let DATA = null;
let activeCategory = 'all';

// 从 Supabase 加载数据
async function loadData() {
  const headers = {
    'apikey': SUPABASE_CONFIG.anonKey,
    'Authorization': 'Bearer ' + SUPABASE_CONFIG.anonKey
  };
  try {
    const [toolsRes, termsRes, scenariosRes] = await Promise.all([
      fetch(SUPABASE_CONFIG.restUrl + '/ai_tools?select=*', { headers }),
      fetch(SUPABASE_CONFIG.restUrl + '/ai_terms?select=*', { headers }),
      fetch(SUPABASE_CONFIG.restUrl + '/ai_scenarios?select=*', { headers })
    ]);
    const tools = await toolsRes.json();
    const terms = await termsRes.json();
    const scenarios = await scenariosRes.json();
    DATA = {
      tools: tools.map(t => ({
        id: t.id, name: t.name, fullName: t.full_name, category: t.category,
        lang: t.lang, maker: t.maker, status: t.status, stars: t.stars,
        license: t.license, summary: t.summary, detail: t.detail,
        pros: t.pros || [], cons: t.cons || [], tags: t.tags || [],
        compareWith: t.compare_with || []
      })),
      terms: terms.map(t => ({ term: t.term, full: t.full_name, desc: t.description })),
      scenarios: scenarios.map(s => ({ title: s.title, tools: s.tools || [], desc: s.description })),
      categories: CATEGORIES,
      lastUpdate: new Date().toLocaleDateString('zh-CN')
    };
    init();
  } catch(e) {
    console.error('Supabase加载失败，尝试本地JSON', e);
    try {
      const res = await fetch('data.json');
      DATA = await res.json();
      if (!DATA.categories) DATA.categories = CATEGORIES;
      init();
    } catch(e2) {
      document.getElementById('toolCount').textContent = '⚠️';
      console.error('本地JSON也失败', e2);
    }
  }
}

function init() {
  renderStats();
  renderUpdateTime();
  renderCategories();
  renderTools();
  renderTerms();
  renderScenarios();
  renderLatest();
  renderCompareSelects();
  bindEvents();
}

function renderStats() {
  document.getElementById('toolCount').textContent = DATA.tools.length;
  document.getElementById('termCount').textContent = DATA.terms.length;
  document.getElementById('scenarioCount').textContent = DATA.scenarios.length;
  document.getElementById('catCount').textContent = DATA.categories.length;
}

function renderUpdateTime() {
  const t = '最后更新：' + DATA.lastUpdate;
  document.getElementById('updateTime').textContent = t;
  document.getElementById('footerUpdate').textContent = t;
}

function renderCategories() {
  const wrap = document.getElementById('categoryPills');
  let html = '<div class="pill active" data-cat="all">全部</div>';
  DATA.categories.forEach(c => {
    html += `<div class="pill" data-cat="${c.id}">${c.icon} ${c.name}</div>`;
  });
  wrap.innerHTML = html;
  wrap.querySelectorAll('.pill').forEach(p => {
    p.onclick = () => {
      wrap.querySelectorAll('.pill').forEach(x => x.classList.remove('active'));
      p.classList.add('active');
      activeCategory = p.dataset.cat;
      renderTools();
    };
  });
}

function getStatusClass(status) {
  if (!status) return 'blue';
  if (status.includes('生产') || status.includes('可用') || status.includes('开源') || status.includes('免费')) return 'green';
  if (status.includes('预览') || status.includes('商业')) return 'yellow';
  return 'blue';
}

function renderTools(filter = '') {
  const grid = document.getElementById('toolsGrid');
  let tools = activeCategory === 'all' ? DATA.tools : DATA.tools.filter(t => t.category === activeCategory);
  if (filter) {
    const f = filter.toLowerCase();
    tools = tools.filter(t => t.name.toLowerCase().includes(f) || t.summary.toLowerCase().includes(f) || (t.tags||[]).some(tag=>tag.toLowerCase().includes(f)));
  }
  if (tools.length === 0) {
    grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:48px;color:var(--text2)">没有找到匹配的工具</div>';
    return;
  }
  grid.innerHTML = tools.map(t => {
    const cat = DATA.categories.find(c => c.id === t.category);
    return `<div class="tool-card" data-id="${t.id}">
      <div class="tc-header">
        <span class="tc-name">${t.name}</span>
        <span class="tc-status ${getStatusClass(t.status)}">${t.status||'—'}</span>
      </div>
      <div class="tc-summary">${t.summary}</div>
      <div class="tc-meta">
        ${t.maker ? `<span>🏢 ${t.maker}</span>`:''}
        ${t.lang && t.lang!=='—' ? `<span>⚙️ ${t.lang}</span>`:''}
        ${t.stars && t.stars!=='—' ? `<span>⭐ ${t.stars}</span>`:''}
        ${t.license ? `<span>📄 ${t.license}</span>`:''}
      </div>
      <div class="tc-tags">${(t.tags||[]).map(tag=>`<span class="tc-tag">${tag}</span>`).join('')}</div>
    </div>`;
  }).join('');
  grid.querySelectorAll('.tool-card').forEach(card => {
    card.onclick = () => showDetail(card.dataset.id);
  });
}

function showDetail(id) {
  const t = DATA.tools.find(x => x.id === id);
  if (!t) return;
  const cat = DATA.categories.find(c => c.id === t.category);
  const modal = document.getElementById('modalContent');
  modal.innerHTML = `
    <span class="modal-close" onclick="closeModal()">✕</span>
    <h2>${t.name}${t.fullName?' <span style="font-size:16px;color:var(--text2)">('+t.fullName+')</span>':''}</h2>
    <div class="modal-summary">${t.summary}</div>
    <div class="modal-detail">${t.detail||''}</div>
    <div class="modal-section-title">✅ 优势</div>
    <ul class="modal-pros">${(t.pros||[]).map(p=>`<li>${p}</li>`).join('')}</ul>
    <div class="modal-section-title">❌ 劣势</div>
    <ul class="modal-cons">${(t.cons||[]).map(c=>`<li>${c}</li>`).join('')}</ul>
    <div class="modal-section-title">📊 基本信息</div>
    <div style="font-size:13px;color:var(--text2);line-height:1.8">
      分类：${cat?cat.icon+' '+cat.name:''}<br>
      开发方：${t.maker||'—'}<br>
      语言：${t.lang||'—'}<br>
      状态：${t.status||'—'}<br>
      Stars：${t.stars||'—'}<br>
      许可证：${t.license||'—'}
    </div>
  `;
  document.getElementById('modalOverlay').classList.add('active');
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('active');
}

function renderTerms(filter = '') {
  const grid = document.getElementById('termsGrid');
  let terms = DATA.terms;
  if (filter) {
    const f = filter.toLowerCase();
    terms = terms.filter(t => t.term.toLowerCase().includes(f) || t.desc.toLowerCase().includes(f));
  }
  grid.innerHTML = terms.map(t => `
    <div class="term-card">
      <div class="t-term">${t.term}</div>
      <div class="t-full">${t.full||''}</div>
      <div class="t-desc">${t.desc}</div>
    </div>`).join('');
}

function renderScenarios() {
  const grid = document.getElementById('scenariosGrid');
  grid.innerHTML = DATA.scenarios.map(s => `
    <div class="scenario-card">
      <h4>${s.title}</h4>
      <p>${s.desc}</p>
      <div class="sc-tools">${(s.tools||[]).map(t=>`<span class="sc-tool">${t}</span>`).join('')}</div>
    </div>`).join('');
}

function renderLatest() {
  const feed = document.getElementById('latestFeed');
  const latest = DATA.tools.slice(0, 8);
  feed.innerHTML = latest.map(t => {
    const cat = DATA.categories.find(c => c.id === t.category);
    return `<div class="latest-card" data-id="${t.id}">
      <span class="tag">${cat?cat.icon+' '+cat.name:''}</span>
      <h4>${t.name}</h4>
      <p>${t.summary}</p>
    </div>`;
  }).join('');
  feed.querySelectorAll('.latest-card').forEach(card => {
    card.onclick = () => showDetail(card.dataset.id);
  });
}

function renderCompareSelects() {
  const opts = DATA.tools.map(t => `<option value="${t.id}">${t.name}</option>`).join('');
  document.getElementById('compareA').innerHTML = '<option value="">选择工具A</option>' + opts;
  document.getElementById('compareB').innerHTML = '<option value="">选择工具B</option>' + opts;
}

function doCompare() {
  const aId = document.getElementById('compareA').value;
  const bId = document.getElementById('compareB').value;
  if (!aId || !bId) return;
  const a = DATA.tools.find(x => x.id === aId);
  const b = DATA.tools.find(x => x.id === bId);
  const result = document.getElementById('compareResult');
  result.classList.add('active');
  result.innerHTML = `
    <table class="compare-table">
      <tr><th>维度</th><th>${a.name}</th><th>${b.name}</th></tr>
      <tr><td class="ct-label">一句话</td><td>${a.summary}</td><td>${b.summary}</td></tr>
      <tr><td class="ct-label">开发方</td><td>${a.maker||'—'}</td><td>${b.maker||'—'}</td></tr>
      <tr><td class="ct-label">语言</td><td>${a.lang||'—'}</td><td>${b.lang||'—'}</td></tr>
      <tr><td class="ct-label">状态</td><td>${a.status||'—'}</td><td>${b.status||'—'}</td></tr>
      <tr><td class="ct-label">Stars</td><td>${a.stars||'—'}</td><td>${b.stars||'—'}</td></tr>
      <tr><td class="ct-label">许可证</td><td>${a.license||'—'}</td><td>${b.license||'—'}</td></tr>
      <tr><td class="ct-label">✅ 优势</td><td class="compare-pros"><ul>${(a.pros||[]).map(p=>`<li>${p}</li>`).join('')}</ul></td><td class="compare-pros"><ul>${(b.pros||[]).map(p=>`<li>${p}</li>`).join('')}</ul></td></tr>
      <tr><td class="ct-label">❌ 劣势</td><td class="compare-cons"><ul>${(a.cons||[]).map(p=>`<li>${p}</li>`).join('')}</ul></td><td class="compare-cons"><ul>${(b.cons||[]).map(p=>`<li>${p}</li>`).join('')}</ul></td></tr>
      <tr><td class="ct-label">标签</td><td>${(a.tags||[]).join(', ')}</td><td>${(b.tags||[]).join(', ')}</td></tr>
    </table>`;
}

function bindEvents() {
  const search = document.getElementById('searchInput');
  search.addEventListener('input', e => {
    const f = e.target.value.trim();
    renderTools(f);
    renderTerms(f);
    if (f) {
      document.getElementById('tools').scrollIntoView({behavior:'smooth'});
    }
  });
  document.getElementById('compareBtn').onclick = doCompare;
  document.getElementById('modalOverlay').onclick = e => {
    if (e.target.id === 'modalOverlay') closeModal();
  };
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
  });
}

// 启动
loadData();