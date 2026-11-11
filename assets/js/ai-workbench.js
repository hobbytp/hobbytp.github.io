/**
 * AI 开源项目研究台 (AI Project Workbench) 前端交互脚本
 * 特性：
 * - 渐进增强：首屏已由 Hugo 服务端渲染，本脚本负责多维即时筛选、分页、表格/卡片切换
 * - URL Query 状态同步：支持分享筛选条件 (?cat=agent&lang=Python) 与对比链接 (?compare=a,b,c)，不引入 SPA 路由
 * - 最多 3 项横向对比（含差异高亮）+ 内联 SVG 12 周活跃迷你图
 * - 访客本地个人层（关注、采用状态、私人笔记、JSON 导出/导入）
 * - 访客 GitHub Stars 在线读取与本站项目库重合度对照
 */
(() => {
  'use strict';

  const payloadEl = document.getElementById('aiwb-data-payload');
  const appEl = document.getElementById('ai-workbench-app');
  if (!payloadEl || !appEl) return;

  let rawData = {};
  try {
    rawData = JSON.parse(payloadEl.textContent || '{}');
    if (typeof rawData === 'string') {
      rawData = JSON.parse(rawData);
    }
  } catch (err) {
    console.error('Failed to parse workbench payload:', err);
    return;
  }

  const projects = Array.isArray(rawData.projects) ? rawData.projects : [];
  const events = Array.isArray(rawData.events) ? rawData.events : [];
  const scenarios = Array.isArray(rawData.scenarios) ? rawData.scenarios : [];
  const generatedAt = rawData.generated_at || appEl.dataset.generatedAt || '';

  const byId = new Map(projects.map((p) => [p.id, p]));
  const byRepo = new Map(projects.map((p) => [String(p.repo || '').toLowerCase(), p]));

  const STORAGE_KEY = 'aiwb_personal_state_v2';
  const PAGE_SIZE = 36;

  const personal = loadPersonalState();

  const state = {
    view: 'directory',
    cat: 'all',
    verdict: 'all',
    lang: 'all',
    status: 'all',
    sort: 'featured',
    query: '',
    layout: 'cards',
    page: 1,
    eventType: 'all',
    compare: [],
  };

  function loadPersonalState() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      return {
        watched: new Set(Array.isArray(saved.watched) ? saved.watched : []),
        adoption: saved.adoption && typeof saved.adoption === 'object' ? saved.adoption : {},
        notes: saved.notes && typeof saved.notes === 'object' ? saved.notes : {},
      };
    } catch {
      return { watched: new Set(), adoption: {}, notes: {} };
    }
  }

  function savePersonalState() {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          version: 2,
          updated_at: new Date().toISOString(),
          watched: Array.from(personal.watched),
          adoption: personal.adoption,
          notes: personal.notes,
        })
      );
    } catch {
      /* ignore quota errors */
    }
  }

  function esc(val) {
    return String(val ?? '').replace(/[&<>"']/g, (c) => (
      { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
    ));
  }

  function fmtNum(n) {
    const num = Number(n || 0);
    return Number.isFinite(num) ? num.toLocaleString('en-US') : '0';
  }

  function el(id) {
    return document.getElementById(id);
  }

  let toastTimer = null;
  function showToast(msg) {
    const node = el('aiwb-toast');
    if (!node) return;
    node.textContent = msg;
    node.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      node.hidden = true;
    }, 2600);
  }

  // 1. 数据新鲜度检测 (> 48 小时显示陈旧提示)
  function checkFreshness() {
    if (!generatedAt) return;
    const ts = Date.parse(generatedAt);
    if (!Number.isFinite(ts)) return;
    const hours = (Date.now() - ts) / 3600000;
    const label = el('aiwb-updated-label');
    if (label && hours >= 0) {
      if (hours < 1) {
        label.textContent = '🕒 刚刚更新';
      } else if (hours < 24) {
        label.textContent = `🕒 ${Math.round(hours)} 小时前更新`;
      } else {
        label.textContent = `🕒 ${Math.floor(hours / 24)} 天前更新 (${generatedAt.slice(0, 10)})`;
      }
    }
    if (hours > 48) {
      const banner = el('aiwb-stale-banner');
      const hrsEl = el('aiwb-stale-hours');
      if (hrsEl) hrsEl.textContent = String(Math.round(hours));
      if (banner) banner.hidden = false;
    }
  }

  // 2. 内联 SVG 12 周趋势迷你图
  function renderSparklineSVG(arr) {
    const seq = Array.isArray(arr) && arr.length ? arr : [4, 5, 6, 5, 7, 8, 6, 9, 10, 8, 11, 12];
    const max = Math.max(1, ...seq);
    const bars = seq
      .slice(-12)
      .map((v, i) => {
        const h = Math.max(2, Math.round((Number(v || 0) / max) * 18));
        const x = i * 5;
        const y = 20 - h;
        return `<rect x="${x}" y="${y}" width="3.5" height="${h}" rx="1" fill="currentColor" opacity="${i >= 9 ? '0.95' : '0.45'}"></rect>`;
      })
      .join('');
    return `<svg width="60" height="20" viewBox="0 0 60 20" aria-label="近12周活跃趋势" style="color:var(--aiwb-accent);vertical-align:middle;margin-left:4px;">${bars}</svg>`;
  }

  // 3. URL Query 参数解析与同步
  function readUrlParams() {
    const params = new URLSearchParams(window.location.search);
    if (params.get('view') && ['directory', 'feed', 'scenarios', 'watched'].includes(params.get('view'))) {
      state.view = params.get('view');
    }
    if (params.get('cat')) state.cat = params.get('cat');
    if (params.get('verdict')) state.verdict = params.get('verdict');
    if (params.get('lang')) state.lang = params.get('lang');
    if (params.get('status')) state.status = params.get('status');
    if (params.get('sort')) state.sort = params.get('sort');
    if (params.get('q')) state.query = params.get('q');
    if (params.get('layout') && ['cards', 'table'].includes(params.get('layout'))) {
      state.layout = params.get('layout');
    }
    if (params.get('page')) {
      const p = parseInt(params.get('page'), 10);
      if (p > 0) state.page = p;
    }
    if (params.get('compare')) {
      const ids = params
        .get('compare')
        .split(',')
        .map((s) => s.trim())
        .filter((id) => byId.has(id))
        .slice(0, 3);
      state.compare = ids;
    }
  }

  function syncUrlParams() {
    const params = new URLSearchParams();
    if (state.view !== 'directory') params.set('view', state.view);
    if (state.cat !== 'all') params.set('cat', state.cat);
    if (state.verdict !== 'all') params.set('verdict', state.verdict);
    if (state.lang !== 'all') params.set('lang', state.lang);
    if (state.status !== 'all') params.set('status', state.status);
    if (state.sort !== 'featured') params.set('sort', state.sort);
    if (state.query.trim()) params.set('q', state.query.trim());
    if (state.layout !== 'cards') params.set('layout', state.layout);
    if (state.page > 1) params.set('page', String(state.page));
    if (state.compare.length > 0) params.set('compare', state.compare.join(','));

    const qs = params.toString();
    const newUrl = window.location.pathname + (qs ? `?${qs}` : '');
    window.history.replaceState(null, '', newUrl);
  }

  // 4. 过滤与排序项目列表
  function getFilteredProjects() {
    const q = state.query.trim().toLowerCase();
    return projects
      .filter((p) => {
        if (state.cat !== 'all' && p.category !== state.cat) return false;
        if (state.verdict !== 'all') {
          if (state.verdict === 'curated' && p.verdict === 'unrated') return false;
          if (state.verdict === 'has_posts' && (!p.posts || !p.posts.length)) return false;
          if (!['curated', 'has_posts'].includes(state.verdict) && p.verdict !== state.verdict) return false;
        }
        if (state.lang !== 'all') {
          const pLang = String(p.language || '').toLowerCase();
          if (state.lang === 'C++') {
            if (!['c++', 'c', 'cuda'].includes(pLang)) return false;
          } else if (pLang !== state.lang.toLowerCase()) {
            return false;
          }
        }
        if (state.status !== 'all') {
          if (state.status === 'active' && p.status !== 'active') return false;
          if (state.status === 'has_release' && (!p.release || !p.release.tag)) return false;
          if (state.status === 'risk' && (!p.risks || !p.risks.length)) return false;
        }
        if (q) {
          const hay = [
            p.name,
            p.repo,
            p.summary_zh,
            p.description,
            p.category_name,
            ...(p.tags || []),
            ...(p.topics || []),
          ]
            .join(' ')
            .toLowerCase();
          if (!hay.includes(q)) return false;
        }
        return true;
      })
      .sort((a, b) => {
        if (state.sort === 'starred_at') {
          return String(b.starred_at || '').localeCompare(String(a.starred_at || '')) || b.stars - a.stars;
        }
        if (state.sort === 'health') {
          return (b.health?.score || 0) - (a.health?.score || 0) || b.stars - a.stars;
        }
        if (state.sort === 'velocity') {
          return (b.stars_7d || 0) - (a.stars_7d || 0) || (b.stars_per_day || 0) - (a.stars_per_day || 0);
        }
        if (state.sort === 'stars') {
          return (b.stars || 0) - (a.stars || 0);
        }
        if (state.sort === 'pushed_at') {
          return String(b.pushed_at || '').localeCompare(String(a.pushed_at || ''));
        }
        // featured 默认：推荐/试用 -> 有本站解读 -> Star 时间 -> Stars
        const vRank = { recommend: 3, trial: 2, watch: 1 };
        const va = vRank[a.verdict] || 0;
        const vb = vRank[b.verdict] || 0;
        if (vb !== va) return vb - va;
        const pa = a.posts?.length ? 1 : 0;
        const pb = b.posts?.length ? 1 : 0;
        if (pb !== pa) return pb - pa;
        return String(b.starred_at || '').localeCompare(String(a.starred_at || '')) || (b.stars || 0) - (a.stars || 0);
      });
  }

  // 5. 渲染卡片与紧凑表格
  function renderCardHTML(p) {
    const isWatched = personal.watched.has(p.id);
    const isCompared = state.compare.includes(p.id);
    const adoptVal = personal.adoption[p.id] || '';
    const risksHTML = (p.risks || [])
      .map((r) => `<span class="aiwb-badge aiwb-risk-${esc(r.level)}" title="${esc(r.label)}">⚠️ ${esc(r.label)}</span>`)
      .join('');
    const tagsHTML = (p.tags || [])
      .slice(0, 3)
      .map((t) => `<span class="aiwb-tag">#${esc(t)}</span>`)
      .join('');
    const relTag = p.release?.tag ? esc(p.release.tag) : '主干交付';
    const relSub = p.release?.published_at
      ? esc(p.release.published_at.slice(0, 10))
      : `推送 ${esc((p.pushed_at || '').slice(0, 10))}`;
    const postLinkHTML =
      p.posts && p.posts.length
        ? `<a class="aiwb-card-link aiwb-card-link-post" href="${esc(p.posts[0].url)}" title="${esc(p.posts[0].title)}">📝 本站解读 (${p.posts.length})</a>`
        : '';
    const dossierAttr = p.has_static_page ? '' : `data-quick-project="${esc(p.id)}"`;

    return `
      <article class="aiwb-card" data-project-id="${esc(p.id)}">
        <div class="aiwb-card-header">
          <div class="aiwb-card-title-group">
            <a class="aiwb-card-title" href="${esc(p.page_url)}" ${dossierAttr}>${esc(p.name)}</a>
            <span class="aiwb-card-repo">${esc(p.repo)}${p.starred_at ? ` · ⭐ ${esc(p.starred_at.slice(0, 10))}` : ''}</span>
          </div>
          <div class="aiwb-card-badges">
            <span class="aiwb-badge aiwb-verdict-${esc(p.verdict || 'unrated')}">${esc(p.verdict_label || '已收藏待评')}</span>
            ${risksHTML}
          </div>
        </div>
        <p class="aiwb-card-summary">${esc(p.summary_zh || p.description || '暂无描述')}</p>
        <div class="aiwb-card-tags">
          <span class="aiwb-tag aiwb-tag-cat">${esc(p.category_name)}</span>
          ${tagsHTML}
        </div>
        <div class="aiwb-card-metrics">
          <div class="aiwb-metric-cell">
            <span class="aiwb-metric-k">⭐ Stars</span>
            <strong class="aiwb-metric-v">${fmtNum(p.stars)}</strong>
            <small class="aiwb-metric-sub">+${fmtNum(p.stars_7d)} / 7d</small>
          </div>
          <div class="aiwb-metric-cell">
            <span class="aiwb-metric-k">📦 最新版本</span>
            <strong class="aiwb-metric-v">${relTag}</strong>
            <small class="aiwb-metric-sub">${relSub}</small>
          </div>
          <div class="aiwb-metric-cell">
            <span class="aiwb-metric-k">🩺 健康度</span>
            <strong class="aiwb-metric-v">${p.health?.score || 75}${renderSparklineSVG(p.weekly_commits)}</strong>
            <small class="aiwb-metric-sub">${esc(p.language || 'Multi')} · ${esc(p.license || '未声明')}</small>
          </div>
        </div>
        <div class="aiwb-card-footer">
          <div class="aiwb-card-links">
            <button type="button" class="aiwb-link-btn" data-quick-project="${esc(p.id)}">快速档案</button>
            ${p.has_static_page ? `<a class="aiwb-card-link" href="${esc(p.page_url)}">独立页 →</a>` : ''}
            ${postLinkHTML}
            <a class="aiwb-card-link" href="https://github.com/${esc(p.repo)}" target="_blank" rel="noopener noreferrer">GitHub ↗</a>
          </div>
          <div class="aiwb-card-controls">
            <select class="aiwb-select" style="padding:2px 6px;font-size:0.72rem;" data-adopt-id="${esc(p.id)}" aria-label="${esc(p.name)} 个人状态">
              <option value=""${adoptVal === '' ? ' selected' : ''}>个人状态</option>
              <option value="try"${adoptVal === 'try' ? ' selected' : ''}>🎯 想试</option>
              <option value="using"${adoptVal === 'using' ? ' selected' : ''}>✅ 在用</option>
              <option value="hold"${adoptVal === 'hold' ? ' selected' : ''}>⏸️ 放弃</option>
            </select>
            <label class="aiwb-compare-check">
              <input type="checkbox" data-compare-id="${esc(p.id)}"${isCompared ? ' checked' : ''}> 对比
            </label>
            <button type="button" class="aiwb-watch-btn ${isWatched ? 'on' : ''}" data-watch-id="${esc(p.id)}" aria-label="关注 ${esc(p.name)}">${isWatched ? '★' : '☆'}</button>
          </div>
        </div>
      </article>
    `;
  }

  function renderTableHTML(slice) {
    const rows = slice
      .map((p) => {
        const isWatched = personal.watched.has(p.id);
        const isCompared = state.compare.includes(p.id);
        const rel = p.release?.tag ? `${esc(p.release.tag)} (${esc((p.release.published_at || '').slice(0, 10))})` : '主干交付';
        return `
          <tr>
            <td><input type="checkbox" data-compare-id="${esc(p.id)}"${isCompared ? ' checked' : ''} aria-label="对比 ${esc(p.name)}"></td>
            <td>
              <button type="button" class="aiwb-link-btn" style="font-weight:700;font-size:0.9rem;text-align:left;" data-quick-project="${esc(p.id)}">${esc(p.name)}</button>
              <div style="font-size:0.72rem;color:var(--aiwb-muted);">${esc(p.repo)} · ${esc(p.category_name)}</div>
            </td>
            <td style="max-width:300px;font-size:0.8rem;">${esc(p.summary_zh || p.description || '')}</td>
            <td><strong>${fmtNum(p.stars)}</strong><div style="font-size:0.72rem;color:var(--aiwb-muted);">+${fmtNum(p.stars_7d)}/7d</div></td>
            <td><strong>${p.health?.score || 75}</strong>/100 ${renderSparklineSVG(p.weekly_commits)}</td>
            <td style="font-size:0.78rem;">${rel}</td>
            <td style="font-size:0.78rem;">${esc(p.language || 'Multi')} · ${esc(p.license || '未声明')}</td>
            <td><span class="aiwb-badge aiwb-verdict-${esc(p.verdict || 'unrated')}">${esc(p.verdict_label || '已收藏待评')}</span></td>
            <td><button type="button" class="aiwb-watch-btn ${isWatched ? 'on' : ''}" data-watch-id="${esc(p.id)}">${isWatched ? '★' : '☆'}</button></td>
          </tr>
        `;
      })
      .join('');

    return `
      <table class="aiwb-table">
        <thead>
          <tr>
            <th>对比</th>
            <th>项目 / 仓库</th>
            <th>一句话中文定位</th>
            <th>Stars / 增速</th>
            <th>CHAOSS 健康度</th>
            <th>最新版本</th>
            <th>语言 / 协议</th>
            <th>选型判断</th>
            <th>关注</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    `;
  }

  function renderPagination(totalItems, totalPages) {
    const pager = el('aiwb-pagination');
    if (!pager) return;
    if (totalPages <= 1) {
      pager.innerHTML = '';
      return;
    }
    let html = `<button type="button" class="aiwb-btn" data-page="${state.page - 1}" ${state.page <= 1 ? 'disabled' : ''}>« 上一页</button>`;
    html += `<span style="font-size:0.84rem;color:var(--aiwb-muted);margin:0 0.6rem;">第 <strong>${state.page}</strong> / ${totalPages} 页（共 ${totalItems} 项）</span>`;
    html += `<button type="button" class="aiwb-btn" data-page="${state.page + 1}" ${state.page >= totalPages ? 'disabled' : ''}>下一页 »</button>`;
    pager.innerHTML = html;
  }

  function renderDirectory() {
    const list = getFilteredProjects();
    const totalPages = Math.max(1, Math.ceil(list.length / PAGE_SIZE));
    if (state.page > totalPages) state.page = totalPages;
    const start = (state.page - 1) * PAGE_SIZE;
    const slice = list.slice(start, start + PAGE_SIZE);

    const cardsWrap = el('aiwb-projects-container');
    const tableWrap = el('aiwb-table-container');
    const summaryEl = el('aiwb-result-summary');
    const resetBtn = el('aiwb-reset-filters');

    const hasActiveFilter =
      state.cat !== 'all' ||
      state.verdict !== 'all' ||
      state.lang !== 'all' ||
      state.status !== 'all' ||
      Boolean(state.query.trim());

    if (resetBtn) resetBtn.hidden = !hasActiveFilter;
    if (summaryEl) {
      summaryEl.innerHTML = `筛选出 <strong>${list.length}</strong> 个开源项目 · 第 ${state.page}/${totalPages} 页（勾选最多 3 个项目可横向对比）`;
    }

    if (state.layout === 'cards') {
      if (cardsWrap) {
        cardsWrap.hidden = false;
        cardsWrap.innerHTML = slice.length
          ? slice.map(renderCardHTML).join('')
          : `<div class="aiwb-panel" style="grid-column:1/-1;text-align:center;">没有匹配当前筛选条件的开源项目。</div>`;
      }
      if (tableWrap) tableWrap.hidden = true;
    } else {
      if (cardsWrap) cardsWrap.hidden = true;
      if (tableWrap) {
        tableWrap.hidden = false;
        tableWrap.innerHTML = slice.length
          ? renderTableHTML(slice)
          : `<div class="aiwb-panel" style="text-align:center;">没有匹配当前筛选条件的开源项目。</div>`;
      }
    }

    renderPagination(list.length, totalPages);
  }

  // 6. 渲染变化信号流 (Feed)
  function renderFeed() {
    const listEl = el('aiwb-feed-list');
    if (!listEl) return;
    const filtered = events.filter((e) => {
      if (state.eventType === 'all') return true;
      if (state.eventType === 'release') return e.type === 'release' || e.type === 'release_major';
      return e.type === state.eventType;
    });
    listEl.innerHTML = filtered.length
      ? filtered
          .slice(0, 60)
          .map(
            (e) => `
          <article class="aiwb-event-card aiwb-event-${esc(e.importance)}">
            <div class="aiwb-event-meta">
              <span class="aiwb-event-badge">${esc(e.type_label)}</span>
              <time class="aiwb-event-date">${esc(e.date)}</time>
              <span class="aiwb-event-repo">${esc(e.repo)}</span>
            </div>
            <h3 class="aiwb-event-title">
              <a href="${esc(e.url)}" data-quick-project="${esc(e.project_id)}">${esc(e.title)}</a>
            </h3>
            <p class="aiwb-event-summary">${esc(e.summary)}</p>
            <div class="aiwb-event-actions">
              <button type="button" class="aiwb-link-btn" data-quick-project="${esc(e.project_id)}">查看项目档案 →</button>
              ${e.external_url ? `<a href="${esc(e.external_url)}" target="_blank" rel="noopener noreferrer">来源链接 ↗</a>` : ''}
            </div>
          </article>
        `
          )
          .join('')
      : `<div class="aiwb-panel" style="grid-column:1/-1;text-align:center;">该分类下暂无近期事件信号。</div>`;
  }

  // 7. 渲染我的关注 (Watched)
  function renderWatched() {
    const count = personal.watched.size + Object.keys(personal.adoption).filter((k) => personal.adoption[k]).length;
    const uniqueTrackedIds = new Set([
      ...personal.watched,
      ...Object.keys(personal.adoption).filter((k) => personal.adoption[k]),
    ]);
    const statNode = el('aiwb-watched-stat');
    const tabBadge = el('aiwb-watched-tab-count');
    if (statNode) statNode.textContent = String(uniqueTrackedIds.size);
    if (tabBadge) tabBadge.textContent = String(uniqueTrackedIds.size);

    const wrap = el('aiwb-watched-list');
    if (!wrap) return;

    if (uniqueTrackedIds.size === 0) {
      wrap.innerHTML = `
        <div style="padding:1.5rem 0;color:var(--aiwb-muted);font-size:0.88rem;">
          你还没有关注或标记任何项目。在「项目库」中点击卡片右下角的 ☆ 或选择「个人状态（想试/在用）」，即可在此处集中追踪它们的版本发布与异动。
        </div>
      `;
      return;
    }

    const adoptLabels = { try: '🎯 想试', using: '✅ 在用', hold: '⏸️ 放弃' };
    const trackedProjects = Array.from(uniqueTrackedIds)
      .map((id) => byId.get(id))
      .filter(Boolean);

    wrap.innerHTML = trackedProjects
      .map((p) => {
        const adopt = adoptLabels[personal.adoption[p.id]] || '⭐ 已关注';
        const rel = p.release?.tag ? `最新 Release: ${esc(p.release.tag)} (${esc((p.release.published_at || '').slice(0, 10))})` : `最近推送: ${esc((p.pushed_at || '').slice(0, 10))}`;
        return `
          <div style="padding:0.85rem 0;border-bottom:1px solid var(--aiwb-border);display:flex;justify-content:space-between;align-items:center;gap:0.75rem;flex-wrap:wrap;">
            <div>
              <button type="button" class="aiwb-link-btn" style="font-weight:700;font-size:0.95rem;" data-quick-project="${esc(p.id)}">${esc(p.name)}</button>
              <span class="aiwb-badge" style="margin-left:6px;">${adopt}</span>
              <div style="font-size:0.78rem;color:var(--aiwb-muted);margin-top:3px;">${esc(p.repo)} · ${rel} · 健康度 ${p.health?.score || 75}</div>
            </div>
            <div style="display:flex;gap:0.5rem;">
              <button type="button" class="aiwb-btn" data-quick-project="${esc(p.id)}">档案</button>
              <button type="button" class="aiwb-btn" data-watch-id="${esc(p.id)}">移除</button>
            </div>
          </div>
        `;
      })
      .join('');
  }

  // 8. 对比栏与最多 3 项横向对比弹窗
  function updateCompareBar() {
    const bar = el('aiwb-compare-bar');
    const countEl = el('aiwb-compare-count');
    const namesEl = el('aiwb-compare-names');
    const openBtn = el('aiwb-compare-open');
    if (!bar) return;

    if (state.compare.length === 0) {
      bar.hidden = true;
      return;
    }
    bar.hidden = false;
    if (countEl) countEl.textContent = String(state.compare.length);
    const selectedProjects = state.compare.map((id) => byId.get(id)).filter(Boolean);
    if (namesEl) namesEl.textContent = selectedProjects.map((p) => p.name).join(' vs ');
    if (openBtn) {
      openBtn.disabled = selectedProjects.length < 2;
      openBtn.textContent =
        selectedProjects.length >= 2
          ? `立即对比这 ${selectedProjects.length} 个项目 →`
          : '再选 1 个项目开始对比';
    }
  }

  function openDialog(title, bodyHTML) {
    const dlg = el('aiwb-dialog');
    const titleEl = el('aiwb-dialog-title');
    const bodyEl = el('aiwb-dialog-body');
    if (!dlg || !titleEl || !bodyEl) return;
    titleEl.textContent = title;
    bodyEl.innerHTML = bodyHTML;
    if (!dlg.open) dlg.showModal();
  }

  function openCompareModal() {
    const items = state.compare.map((id) => byId.get(id)).filter(Boolean);
    if (items.length < 2) return;

    const maxScore = Math.max(...items.map((p) => p.health?.score || 0));
    const maxStars = Math.max(...items.map((p) => p.stars || 0));
    const maxVel = Math.max(...items.map((p) => p.stars_7d || 0));

    const headers = items
      .map(
        (p) => `
        <th>
          <a href="${esc(p.page_url)}" style="font-size:1rem;font-weight:800;color:var(--aiwb-accent);">${esc(p.name)}</a>
          <div style="font-size:0.74rem;color:var(--aiwb-muted);">${esc(p.repo)}</div>
        </th>
      `
      )
      .join('');

    const row = (label, fn) => `
      <tr>
        <td style="font-weight:700;width:150px;background:var(--aiwb-surface);">${label}</td>
        ${items.map((p) => `<td>${fn(p)}</td>`).join('')}
      </tr>
    `;

    const html = `
      <p class="aiwb-muted" style="margin-top:0;">先对比适用边界与维护健康度，再决定选型顺序。绿色高亮代表该数值维度当前领先。</p>
      <div class="aiwb-table-wrap">
        <table class="aiwb-table">
          <thead>
            <tr><th>对比维度</th>${headers}</tr>
          </thead>
          <tbody>
            ${row('领域与选型判断', (p) => `<span class="aiwb-badge aiwb-verdict-${esc(p.verdict)}">${esc(p.verdict_label)}</span> · ${esc(p.category_name)}`)}
            ${row('一句话中文定位', (p) => esc(p.summary_zh || p.description || ''))}
            ${row('适合场景 (Good For)', (p) => `<ul style="margin:0;padding-left:1.1rem;font-size:0.8rem;">${(p.good_for || []).map((x) => `<li>${esc(x)}</li>`).join('')}</ul>`)}
            ${row('不适用边界 (Not For)', (p) => `<ul style="margin:0;padding-left:1.1rem;font-size:0.8rem;color:var(--aiwb-muted);">${(p.not_for || []).map((x) => `<li>${esc(x)}</li>`).join('')}</ul>`)}
            ${row('CHAOSS 综合健康度', (p) => {
              const s = p.health?.score || 0;
              return `<strong style="${s === maxScore ? 'color:var(--aiwb-green);font-size:1.05rem;' : ''}">${s} / 100</strong> (活跃 ${p.health?.activity} · 社区 ${p.health?.community} · 发布 ${p.health?.release} · 合规 ${p.health?.sustainability})`;
            })}
            ${row('GitHub Stars 与增速', (p) => `<strong style="${p.stars === maxStars ? 'color:var(--aiwb-green);' : ''}">${fmtNum(p.stars)}</strong> <span style="${p.stars_7d === maxVel ? 'color:var(--aiwb-green);font-weight:700;' : 'color:var(--aiwb-muted);'}">(+${fmtNum(p.stars_7d)} / 7d)</span>`)}
            ${row('最新版本与推送', (p) => (p.release?.tag ? `<code>${esc(p.release.tag)}</code> (${esc((p.release.published_at || '').slice(0, 10))})` : `主干交付 (最近推送 ${esc((p.pushed_at || '').slice(0, 10))})`))}
            ${row('语言与开源许可证', (p) => `${esc(p.language || 'Multi')} · <code>${esc(p.license || '未声明')}</code>`)}
            ${row('风险信号', (p) => (p.risks && p.risks.length ? p.risks.map((r) => `⚠️ ${esc(r.label)}`).join('<br>') : '🟢 无异常风险标志'))}
            ${row('本站深度解读文章', (p) => (p.posts && p.posts.length ? p.posts.map((post) => `<a href="${esc(post.url)}">📝 《${esc(post.title)}》</a>`).join('<br>') : '<span class="aiwb-muted">暂无专题文章</span>'))}
            ${row('链接入口', (p) => `<a href="${esc(p.page_url)}">站内档案 →</a> · <a href="https://github.com/${esc(p.repo)}" target="_blank" rel="noopener">GitHub ↗</a>`)}
          </tbody>
        </table>
      </div>
    `;
    openDialog(`⚖️ 开源项目横向对比 (${items.map((p) => p.name).join(' vs ')})`, html);
  }

  // 9. 项目快速档案弹窗 (支持所有 595+ 项目即时查看与写个人笔记)
  function openProjectQuickDossier(projectId) {
    const p = byId.get(projectId);
    if (!p) return;
    const noteVal = personal.notes[p.id] || '';
    const relHTML = p.release?.tag
      ? `<div class="aiwb-panel" style="margin-top:1rem;">
          <h3 style="margin:0 0 0.4rem;font-size:0.98rem;">🚀 最新版本 ${esc(p.release.tag)} (${esc((p.release.published_at || '').slice(0, 10))})</h3>
          <ul style="margin:0;padding-left:1.2rem;font-size:0.84rem;">
            ${(p.release.highlights || []).map((h) => `<li>${esc(h)}</li>`).join('')}
          </ul>
        </div>`
      : '';
    const postsHTML =
      p.posts && p.posts.length
        ? `<div class="aiwb-panel" style="margin-top:1rem;">
            <h3 style="margin:0 0 0.5rem;font-size:0.98rem;">📝 本站深度解读文章</h3>
            ${p.posts.map((post) => `<div style="margin-bottom:0.35rem;"><a href="${esc(post.url)}">《${esc(post.title)}》 (${esc(post.date)}) →</a></div>`).join('')}
          </div>`
        : '';

    const html = `
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;margin-bottom:0.75rem;">
        <div>
          <span class="aiwb-badge aiwb-verdict-${esc(p.verdict)}">${esc(p.verdict_label)}</span>
          <span class="aiwb-tag aiwb-tag-cat" style="margin-left:6px;">${esc(p.category_name)}</span>
          <span class="aiwb-muted" style="margin-left:8px;font-size:0.8rem;">${esc(p.repo)} · ⭐ 收藏于 ${esc((p.starred_at || '').slice(0, 10) || '早期')}</span>
        </div>
        <div style="display:flex;gap:0.5rem;">
          ${p.has_static_page ? `<a class="aiwb-btn aiwb-btn-primary" href="${esc(p.page_url)}">打开独立 SEO 档案页 →</a>` : ''}
          <a class="aiwb-btn" href="https://github.com/${esc(p.repo)}" target="_blank" rel="noopener noreferrer">GitHub 仓库 ↗</a>
        </div>
      </div>

      <p style="font-size:0.96rem;line-height:1.6;margin:0 0 1rem;">${esc(p.summary_zh || p.description || '')}</p>

      <div class="aiwb-facts-grid">
        <div class="aiwb-fact-box">
          <span class="aiwb-fact-label">⭐ Stars / 7日增量</span>
          <strong class="aiwb-fact-val">${fmtNum(p.stars)}</strong>
          <small>+${fmtNum(p.stars_7d)} / 7d · 日均 +${p.stars_per_day}</small>
        </div>
        <div class="aiwb-fact-box">
          <span class="aiwb-fact-label">🩺 CHAOSS 健康度</span>
          <strong class="aiwb-fact-val">${p.health?.score || 75} / 100</strong>
          <small>活跃 ${p.health?.activity} · 社区 ${p.health?.community} · 发布 ${p.health?.release}</small>
        </div>
        <div class="aiwb-fact-box">
          <span class="aiwb-fact-label">📜 许可证 / 语言</span>
          <strong class="aiwb-fact-val">${esc(p.license || '未声明')}</strong>
          <small>${esc(p.language || 'Multi')} · 最近推送 ${esc((p.pushed_at || '').slice(0, 10))}</small>
        </div>
      </div>

      <div class="aiwb-dossier-grid">
        <div class="aiwb-panel" style="margin-bottom:0;">
          <h3 style="margin:0 0 0.4rem;font-size:0.95rem;">✅ 适用场景 (Good For)</h3>
          <ul style="margin:0;padding-left:1.1rem;font-size:0.84rem;">
            ${(p.good_for || []).map((x) => `<li>${esc(x)}</li>`).join('')}
          </ul>
        </div>
        <div class="aiwb-panel" style="margin-bottom:0;">
          <h3 style="margin:0 0 0.4rem;font-size:0.95rem;">🚫 局限与不适用边界 (Not For)</h3>
          <ul style="margin:0;padding-left:1.1rem;font-size:0.84rem;">
            ${(p.not_for || []).map((x) => `<li>${esc(x)}</li>`).join('')}
          </ul>
        </div>
      </div>

      ${relHTML}
      ${postsHTML}

      <div class="aiwb-panel" style="margin-top:1rem;margin-bottom:0;">
        <h3 style="margin:0 0 0.4rem;font-size:0.95rem;">📓 我的私人选型笔记（仅保存在当前浏览器）</h3>
        <textarea id="aiwb-modal-note" class="aiwb-input" style="width:100%;min-height:68px;" placeholder="记录你的试用体验、踩坑点或替换条件…">${esc(noteVal)}</textarea>
        <div style="margin-top:0.5rem;display:flex;justify-content:flex-end;">
          <button type="button" class="aiwb-btn aiwb-btn-primary" id="aiwb-save-note-btn" data-note-id="${esc(p.id)}">保存私人笔记</button>
        </div>
      </div>
    `;
    openDialog(`${p.name} · 项目研究档案`, html);
  }

  // 10. 导出与恢复本地关注记录
  function openExportModal() {
    const exportObj = {
      version: 2,
      exported_at: new Date().toISOString(),
      watched: Array.from(personal.watched),
      adoption: personal.adoption,
      notes: personal.notes,
    };
    const jsonStr = JSON.stringify(exportObj, null, 2);
    const html = `
      <p class="aiwb-muted">你可以将本地关注的项目、采用状态与私人笔记导出为 JSON 备份，或在其它设备粘贴恢复。</p>
      <textarea id="aiwb-export-textarea" class="aiwb-input" style="width:100%;min-height:180px;font-family:monospace;font-size:0.78rem;">${esc(jsonStr)}</textarea>
      <div style="display:flex;gap:0.6rem;margin-top:0.85rem;flex-wrap:wrap;">
        <button type="button" class="aiwb-btn aiwb-btn-primary" id="aiwb-download-json">⬇️ 下载 JSON 文件</button>
        <button type="button" class="aiwb-btn" id="aiwb-restore-json">🔄 从上方文本框恢复记录</button>
        <button type="button" class="aiwb-btn" id="aiwb-clear-local" style="color:var(--aiwb-red);">🗑️ 清空本地记录</button>
      </div>
    `;
    openDialog('💾 导出 / 恢复本地个人研究记录', html);
  }

  // 11. 访客 GitHub Stars 导入与本站重合度对照
  async function handleVisitorStarsCompare(username) {
    const statusEl = el('aiwb-visitor-status');
    const resultEl = el('aiwb-visitor-result');
    const btn = el('aiwb-visitor-fetch-btn');
    if (!statusEl || !resultEl) return;

    const cleanUser = String(username || '').trim();
    if (!/^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$/.test(cleanUser)) {
      statusEl.textContent = '❌ 请输入有效的 GitHub 用户名。';
      return;
    }

    if (btn) btn.disabled = true;
    statusEl.textContent = `⏳ 正在读取 @${cleanUser} 的公开 GitHub Stars (前 200 条)...`;
    resultEl.innerHTML = '';

    try {
      const visitorRepos = [];
      for (let page = 1; page <= 2; page++) {
        const resp = await fetch(
          `https://api.github.com/users/${encodeURIComponent(cleanUser)}/starred?per_page=100&page=${page}`,
          { headers: { Accept: 'application/vnd.github+json' } }
        );
        if (!resp.ok) {
          throw new Error(`GitHub API 返回 HTTP ${resp.status}`);
        }
        const arr = await resp.json();
        if (!Array.isArray(arr) || !arr.length) break;
        visitorRepos.push(...arr);
        if (arr.length < 100) break;
      }

      const overlap = [];
      const uniqueToVisitor = [];

      for (const r of visitorRepos) {
        const full = String(r.full_name || '').toLowerCase();
        if (!full) continue;
        if (byRepo.has(full)) {
          overlap.push(byRepo.get(full));
        } else {
          uniqueToVisitor.push({
            repo: r.full_name,
            name: r.name,
            stars: r.stargazers_count || 0,
            description: r.description || '',
          });
        }
      }

      statusEl.textContent = `✅ 读取完成：最近 ${visitorRepos.length} 个 Star 中，与本站共同关注 ${overlap.length} 个，你独有收藏 ${uniqueToVisitor.length} 个。`;

      const overlapHTML = overlap.length
        ? `<div style="margin-bottom:1rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
              <strong>🤝 与本站共同关注的开源项目 (${overlap.length})</strong>
              <button type="button" class="aiwb-btn" id="aiwb-watch-all-overlap">一键全部加入我的关注</button>
            </div>
            <div class="aiwb-card-tags">
              ${overlap
                .slice(0, 30)
                .map((p) => `<button type="button" class="aiwb-pill aiwb-pill-link" data-quick-project="${esc(p.id)}">${esc(p.name)} (${esc(p.verdict_label)})</button>`)
                .join('')}
            </div>
          </div>`
        : '';

      const uniqueHTML = uniqueToVisitor.length
        ? `<div>
            <strong>💡 你收藏但本站尚未收录的项目 (前 12 个)</strong>
            <div style="display:grid;gap:0.5rem;margin-top:0.5rem;">
              ${uniqueToVisitor
                .slice(0, 12)
                .map((u) => {
                  const issueTitle = encodeURIComponent(`[项目推荐] 建议研究台收录 ${u.repo}`);
                  const issueBody = encodeURIComponent(`仓库地址: https://github.com/${u.repo}\n当前 Stars: ${u.stars}\n简介: ${u.description}`);
                  return `
                    <div style="display:flex;justify-content:space-between;align-items:center;background:var(--aiwb-surface);padding:0.5rem 0.75rem;border-radius:8px;font-size:0.8rem;gap:0.5rem;flex-wrap:wrap;">
                      <div>
                        <a href="https://github.com/${esc(u.repo)}" target="_blank" rel="noopener"><strong>${esc(u.repo)}</strong></a>
                        <span class="aiwb-muted"> (⭐ ${fmtNum(u.stars)}) · ${esc(u.description.slice(0, 60))}</span>
                      </div>
                      <a class="aiwb-link-btn" href="https://github.com/hobbytp/hobbytp.github.io/issues/new?title=${issueTitle}&body=${issueBody}" target="_blank" rel="noopener">推荐收录 ↗</a>
                    </div>
                  `;
                })
                .join('')}
            </div>
          </div>`
        : '';

      resultEl.innerHTML = overlapHTML + uniqueHTML;
      const watchAllBtn = el('aiwb-watch-all-overlap');
      if (watchAllBtn) {
        watchAllBtn.addEventListener('click', () => {
          overlap.forEach((p) => personal.watched.add(p.id));
          savePersonalState();
          renderWatched();
          renderDirectory();
          showToast(`已将 ${overlap.length} 个共同关注项目加入本地关注列表`);
        });
      }
    } catch (err) {
      statusEl.textContent = `⚠️ 读取失败：${err.message || '请稍后重试'}`;
    } finally {
      if (btn) btn.disabled = false;
    }
  }

  // 12. 视图切换与事件绑定
  function switchView(viewName) {
    state.view = viewName;
    document.querySelectorAll('.aiwb-tab').forEach((btn) => {
      const active = btn.dataset.view === viewName;
      btn.classList.toggle('active', active);
      btn.setAttribute('aria-selected', String(active));
    });
    ['directory', 'feed', 'scenarios', 'watched'].forEach((v) => {
      const panel = el(`aiwb-view-${v}`);
      if (panel) panel.hidden = v !== viewName;
    });
    syncUrlParams();
  }

  function applyStateToControls() {
    const searchInput = el('aiwb-search');
    const verdictSel = el('aiwb-filter-verdict');
    const langSel = el('aiwb-filter-lang');
    const statusSel = el('aiwb-filter-status');
    const sortSel = el('aiwb-sort');

    if (searchInput) searchInput.value = state.query;
    if (verdictSel) verdictSel.value = state.verdict;
    if (langSel) langSel.value = state.lang;
    if (statusSel) statusSel.value = state.status;
    if (sortSel) sortSel.value = state.sort;

    document.querySelectorAll('#aiwb-cat-bar .aiwb-cat-btn').forEach((b) => {
      b.classList.toggle('active', b.dataset.cat === state.cat);
    });
    document.querySelectorAll('.aiwb-layout-btn').forEach((b) => {
      b.classList.toggle('active', b.dataset.layout === state.layout);
    });
  }

  function bindEvents() {
    document.addEventListener('click', (e) => {
      const tabBtn = e.target.closest('.aiwb-tab');
      if (tabBtn && tabBtn.dataset.view) {
        switchView(tabBtn.dataset.view);
        return;
      }

      const switchBtn = e.target.closest('[data-switch-view]');
      if (switchBtn) {
        switchView(switchBtn.dataset.switchView);
        return;
      }

      const catBtn = e.target.closest('#aiwb-cat-bar .aiwb-cat-btn');
      if (catBtn && catBtn.dataset.cat) {
        state.cat = catBtn.dataset.cat;
        state.page = 1;
        applyStateToControls();
        renderDirectory();
        syncUrlParams();
        return;
      }

      const evtBtn = e.target.closest('#aiwb-feed-filters .aiwb-cat-btn');
      if (evtBtn && evtBtn.dataset.eventType) {
        state.eventType = evtBtn.dataset.eventType;
        document.querySelectorAll('#aiwb-feed-filters .aiwb-cat-btn').forEach((b) => {
          b.classList.toggle('active', b.dataset.eventType === state.eventType);
        });
        renderFeed();
        return;
      }

      const layoutBtn = e.target.closest('.aiwb-layout-btn');
      if (layoutBtn && layoutBtn.dataset.layout) {
        state.layout = layoutBtn.dataset.layout;
        applyStateToControls();
        renderDirectory();
        syncUrlParams();
        return;
      }

      const pageBtn = e.target.closest('[data-page]');
      if (pageBtn && !pageBtn.disabled) {
        state.page = parseInt(pageBtn.dataset.page, 10) || 1;
        renderDirectory();
        syncUrlParams();
        appEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
        return;
      }

      const watchBtn = e.target.closest('[data-watch-id]');
      if (watchBtn) {
        const pid = watchBtn.dataset.watchId;
        if (personal.watched.has(pid)) {
          personal.watched.delete(pid);
          showToast('已从本地关注移除');
        } else {
          personal.watched.add(pid);
          showToast('⭐ 已加入本地关注');
        }
        savePersonalState();
        renderDirectory();
        renderWatched();
        return;
      }

      const quickBtn = e.target.closest('[data-quick-project]');
      if (quickBtn) {
        e.preventDefault();
        openProjectQuickDossier(quickBtn.dataset.quickProject);
        return;
      }

      const openRepoBtn = e.target.closest('[data-open-repo]');
      if (openRepoBtn) {
        const repoLow = String(openRepoBtn.dataset.openRepo || '').toLowerCase();
        const found = byRepo.get(repoLow);
        if (found) {
          openProjectQuickDossier(found.id);
        } else {
          window.open(`https://github.com/${openRepoBtn.dataset.openRepo}`, '_blank', 'noopener');
        }
        return;
      }

      const scCompareBtn = e.target.closest('[data-compare-scenario]');
      if (scCompareBtn) {
        const sc = scenarios.find((s) => s.id === scCompareBtn.dataset.compareScenario);
        if (sc && Array.isArray(sc.stack)) {
          const ids = sc.stack
            .map((st) => byRepo.get(String(st.project || '').toLowerCase())?.id)
            .filter(Boolean)
            .slice(0, 3);
          if (ids.length >= 2) {
            state.compare = ids;
            updateCompareBar();
            renderDirectory();
            syncUrlParams();
            openCompareModal();
          }
        }
        return;
      }

      const saveNoteBtn = e.target.closest('#aiwb-save-note-btn');
      if (saveNoteBtn) {
        const pid = saveNoteBtn.dataset.noteId;
        const noteNode = el('aiwb-modal-note');
        if (pid && noteNode) {
          personal.notes[pid] = noteNode.value.trim();
          personal.watched.add(pid);
          savePersonalState();
          renderWatched();
          showToast('📓 私人选型笔记已保存');
        }
        return;
      }

      if (e.target.closest('#aiwb-download-json')) {
        const ta = el('aiwb-export-textarea');
        const blob = new Blob([ta ? ta.value : '{}'], { type: 'application/json;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ai-workbench-personal-${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
        return;
      }

      if (e.target.closest('#aiwb-restore-json')) {
        const ta = el('aiwb-export-textarea');
        try {
          const parsed = JSON.parse(ta ? ta.value : '{}');
          if (Array.isArray(parsed.watched)) personal.watched = new Set(parsed.watched);
          if (parsed.adoption && typeof parsed.adoption === 'object') personal.adoption = parsed.adoption;
          if (parsed.notes && typeof parsed.notes === 'object') personal.notes = parsed.notes;
          savePersonalState();
          renderDirectory();
          renderWatched();
          showToast('✅ 本地记录已成功恢复');
        } catch {
          showToast('❌ JSON 格式有误，无法恢复');
        }
        return;
      }

      if (e.target.closest('#aiwb-clear-local')) {
        personal.watched.clear();
        personal.adoption = {};
        personal.notes = {};
        savePersonalState();
        renderDirectory();
        renderWatched();
        el('aiwb-dialog')?.close();
        showToast('已清空本地关注与笔记');
      }
    });

    document.addEventListener('change', (e) => {
      const cmpCheck = e.target.closest('[data-compare-id]');
      if (cmpCheck) {
        const pid = cmpCheck.dataset.compareId;
        if (cmpCheck.checked) {
          if (state.compare.length >= 3 && !state.compare.includes(pid)) {
            cmpCheck.checked = false;
            showToast('最多支持同时对比 3 个项目');
            return;
          }
          if (!state.compare.includes(pid)) state.compare.push(pid);
        } else {
          state.compare = state.compare.filter((id) => id !== pid);
        }
        updateCompareBar();
        syncUrlParams();
        return;
      }

      const adoptSel = e.target.closest('[data-adopt-id]');
      if (adoptSel) {
        const pid = adoptSel.dataset.adoptId;
        personal.adoption[pid] = adoptSel.value;
        if (adoptSel.value) personal.watched.add(pid);
        savePersonalState();
        renderWatched();
        showToast('个人采用状态已更新');
      }
    });

    el('aiwb-search')?.addEventListener('input', (e) => {
      state.query = e.target.value;
      state.page = 1;
      renderDirectory();
      syncUrlParams();
    });

    ['verdict', 'lang', 'status'].forEach((key) => {
      el(`aiwb-filter-${key}`)?.addEventListener('change', (e) => {
        state[key] = e.target.value;
        state.page = 1;
        renderDirectory();
        syncUrlParams();
      });
    });

    el('aiwb-sort')?.addEventListener('change', (e) => {
      state.sort = e.target.value;
      state.page = 1;
      renderDirectory();
      syncUrlParams();
    });

    el('aiwb-reset-filters')?.addEventListener('click', () => {
      state.cat = 'all';
      state.verdict = 'all';
      state.lang = 'all';
      state.status = 'all';
      state.query = '';
      state.page = 1;
      applyStateToControls();
      renderDirectory();
      syncUrlParams();
    });

    el('aiwb-compare-clear')?.addEventListener('click', () => {
      state.compare = [];
      updateCompareBar();
      renderDirectory();
      syncUrlParams();
    });

    el('aiwb-compare-open')?.addEventListener('click', openCompareModal);
    el('aiwb-open-export')?.addEventListener('click', openExportModal);
    el('aiwb-open-stars-compare')?.addEventListener('click', () => {
      switchView('watched');
      el('aiwb-visitor-username')?.focus();
    });

    el('aiwb-dialog-close')?.addEventListener('click', () => el('aiwb-dialog')?.close());
    el('aiwb-dialog')?.addEventListener('click', (e) => {
      const dlg = el('aiwb-dialog');
      if (e.target === dlg) dlg.close();
    });

    el('aiwb-visitor-stars-form')?.addEventListener('submit', (e) => {
      e.preventDefault();
      const u = el('aiwb-visitor-username')?.value;
      handleVisitorStarsCompare(u);
    });
  }

  // 初始化
  checkFreshness();
  readUrlParams();
  applyStateToControls();
  switchView(state.view);
  renderDirectory();
  renderFeed();
  renderWatched();
  updateCompareBar();
  bindEvents();

  // 若 URL 带有 ?project=<id> 或 ?compare=a,b 则自动打开对应弹窗
  const initParams = new URLSearchParams(window.location.search);
  const initProj = initParams.get('project');
  if (initProj && byId.has(initProj)) {
    openProjectQuickDossier(initProj);
  } else if (state.compare.length >= 2 && initParams.get('compare')) {
    openCompareModal();
  }
})();

