// 应用骨架：Tab 切换 + 通用工具 + 可选 SSE
// 业务逻辑请在此基础上扩展，不要在本文件堆业务函数

// ===== Tab 配置（扩展时在此追加） =====
const TAB_TITLES = {
    home: '首页',
    example: '示例'
};

const TAB_URLS = {
    home: '/',
    example: '/example'
};

let currentTab = 'home';

// ===== Tab 切换 =====
function switchTab(tabName) {
    document.querySelectorAll('.nav-tab').forEach(tab => {
        const isActive = tab.dataset.tab === tabName;
        tab.classList.toggle('active', isActive);
        tab.setAttribute('aria-selected', isActive ? 'true' : 'false');
    });

    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.toggle('active', pane.id === `tab-${tabName}`);
    });

    const titleEl = document.getElementById('headerTitle');
    if (titleEl) titleEl.textContent = TAB_TITLES[tabName] || tabName;

    const url = TAB_URLS[tabName] || '/';
    history.pushState({ tab: tabName }, '', url);

    currentTab = tabName;
    localStorage.setItem('activeTab', tabName);
}

function initTabFromUrl() {
    const path = window.location.pathname;
    let tabName = 'home';
    for (const [name, url] of Object.entries(TAB_URLS)) {
        if (url === path) { tabName = name; break; }
    }
    const params = new URLSearchParams(window.location.search);
    if (params.has('tab')) tabName = params.get('tab');
    switchTab(tabName);
}

window.addEventListener('popstate', (e) => {
    if (e.state && e.state.tab) switchTab(e.state.tab);
});

// ===== 通用工具 =====

function showToast(message, isError = false) {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'toast' + (isError ? ' error' : '');
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

// 统一的 POST 请求封装，期望后端返回 { success: bool, error?: string, ... }
async function postJSON(url, payload) {
    try {
        const resp = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await resp.json();
        if (!data.success) showToast(data.error || '操作失败', true);
        return data;
    } catch (e) {
        showToast('请求失败: ' + e.message, true);
        return { success: false, error: e.message };
    }
}

// ===== SSE 实时流（按需启用） =====
// 后端实现 GET /api/stream 返回 text/event-stream，每条消息为 JSON
let eventSource = null;

function startSSE(onMessage) {
    if (eventSource) eventSource.close();
    eventSource = new EventSource('/api/stream');
    eventSource.onmessage = (e) => {
        try { onMessage(JSON.parse(e.data)); }
        catch (err) { console.error('SSE 解析错误:', err); }
    };
    eventSource.onerror = () => {
        console.warn('SSE 连接错误，浏览器将自动重试');
    };
}

function stopSSE() {
    if (eventSource) { eventSource.close(); eventSource = null; }
}

// 后台标签自动暂停 SSE，前台恢复（节省资源）
document.addEventListener('visibilitychange', () => {
    if (document.hidden) stopSSE();
});

// ===== 初始化 =====
document.addEventListener('DOMContentLoaded', () => {
    const saved = localStorage.getItem('activeTab');
    if (saved && TAB_TITLES[saved]) {
        switchTab(saved);
    } else {
        initTabFromUrl();
    }
});

window.addEventListener('beforeunload', stopSSE);
