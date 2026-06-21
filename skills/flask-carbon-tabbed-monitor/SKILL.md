---
name: flask-carbon-tabbed-monitor
description: |
  当用户想要创建一个 Flask + IBM Carbon 风格的 Tab 式 Web 应用时使用此 Skill，
  作为架构、技术栈与前端风格的指导性参考。
  适用场景：硬件监控面板、控制台、内部工具、实时数据看板等单页多 Tab 应用。
  本 Skill 不生成完整脚手架，仅在 assets/templates/ 下提供 base.html、style.css、
  app.js 三件套作为风格参考，创建新应用时由 Claude 在该风格基础上从零编写业务代码。
  触发关键词：Flask Web 应用、Carbon 风格、Tab 页面、控制面板、监控仪表盘、SSE 实时更新。
version: 2.0.0
author: Claude
---

# Flask Carbon Tabbed Monitor — 指导说明

本 Skill 不是脚手架生成器，而是一份**架构与风格指南**。`assets/templates/` 下保留了
`base.html` / `style.css` / `app.js` 三个文件作为风格参考，创建新应用时由 Claude 阅读
这三个文件后在目标项目中从零编写业务代码（不复制业务逻辑，只复用结构与样式约定）。

## 何时使用

用户需要从零创建一个具有以下特征的 Flask Web 工具：

- 多功能模块通过顶部 Tab 切换的单页应用
- 服务端渲染（Jinja2）+ vanilla JS，无前端框架
- 简洁、专业的企业级视觉风格（IBM Carbon Design System）
- 实时数据更新（SSE 或定时轮询）
- 离线可用（不依赖 CDN 资源加载业务功能）

## 技术栈

| 层 | 选型 |
|----|------|
| 后端 | Python 3.9+、Flask 2+、Jinja2 |
| 前端 | vanilla JavaScript（无框架）、IBM Carbon Design System（CSS 变量） |
| 图表 | ECharts（按需引入本地 `echarts.min.js`） |
| 实时通信 | SSE（`text/event-stream`）为主，fetch 轮询为辅 |
| 日志 | loguru（控制台彩色 + 按日轮转文件） |
| 后台任务 | `threading.Thread(daemon=True)` + `threading.Lock` 保护共享状态 |

## 推荐目录结构

```
{{ project_name }}/
├── pyproject.toml
├── logs/                            # loguru 日志输出
├── src/{{ package_name }}/
│   ├── __init__.py
│   ├── cli.py                       # 入口（argparse / click）
│   ├── config.py                    # 配置 dataclass
│   ├── logging_config.py            # loguru 配置
│   ├── core/                        # 业务核心（硬件通信、状态管理等）
│   │   └── ...
│   └── web/
│       ├── __init__.py
│       ├── app.py                   # Flask factory + Blueprint 注册
│       ├── blueprints/              # 按 Tab/功能拆分 Blueprint
│       ├── templates/
│       │   ├── base.html            # 单页面 Tab 骨架
│       │   └── includes/            # 各 Tab 子模板（可选）
│       └── static/
│           ├── css/
│           │   ├── fonts.css      # 本地 @font-face 声明
│           │   └── style.css      # Carbon design tokens + 组件
│           ├── fonts/             # IBM Plex 字体文件 (woff2)
│           └── js/app.js          # Tab 切换 + 通用工具 + SSE
└── tests/
```

## 前端风格约定（IBM Carbon）

参考 `assets/templates/static/css/style.css`。核心约定：

- **字体**：IBM Plex Sans（正文/标题）、IBM Plex Mono（数据/代码）
- **颜色系统**：`:root` CSS 变量
  - 主色 `--color-primary: #0f62fe`
  - 语义色 `--color-semantic-success/warning/error/info`
  - 表面层 `--color-canvas / surface-1 / surface-2`
  - 文字 `--color-ink / ink-muted / ink-subtle`
- **间距**：4px 基准网格（`--spacing-xxs` ~ `--spacing-xxl`）
- **形状**：默认直角（`border-radius: 0`），仅状态点使用 pill
- **组件类**（已实现，直接复用）：
  - 容器：`.container`、`.header`、`.panel`、`.panel-header`、`.panel-title`
  - 导航：`.header-nav`、`.nav-tab`、`.tab-pane`
  - 状态：`.status-bar`、`.status-item`、`.status-dot`（`.active` 时呼吸动画）
  - 按钮：`.btn` + `.btn-primary / secondary / tertiary / ghost / danger`
  - 表单：`.form-group`、`.form-label`、`.form-input`、`.form-select`、`.button-row`
  - 反馈：`.toast`（`.show` 显示，`.error` 红色）
  - 代码：`.result-pre`

## 交互范式

参考 `assets/templates/static/js/app.js`。核心约定：

1. **Tab 切换**
   - HTML：`.nav-tab[data-tab=NAME]` + `.tab-pane#tab-NAME`
   - JS：调用 `switchTab(name)`，自动同步 `history.pushState` 和 `localStorage.activeTab`
   - 扩展新 Tab：在 `TAB_TITLES` 和 `TAB_URLS` 中追加映射即可
   - 浏览器前进/后退由 `popstate` 监听处理
2. **统一请求封装**
   - 使用 `postJSON(url, payload)`，后端响应信封必须为 `{ success: bool, error?: string, ... }`
   - 失败时自动 `showToast`，业务侧只需判断 `data.success`
3. **操作反馈**
   - 成功/失败统一用 `showToast(message, isError)`
4. **SSE 实时流**（按需启用）
   - 后端实现 `GET /api/stream` 返回 `text/event-stream`，每条消息为 JSON
   - 前端调用 `startSSE(onMessage)` 注册回调
   - 标签页隐藏时自动断开（`visibilitychange`），`beforeunload` 也会清理

## API 设计模式

| 类型 | 示例 | 响应 |
|------|------|------|
| 页面 | `GET /`、`/example` | 渲染 `base.html` |
| 状态 | `GET /api/status` | 直接 JSON |
| 业务数据 | `GET /api/...` | 直接 JSON |
| 实时流 | `GET /api/stream` | `text/event-stream` |
| 操作 | `POST /api/action` | `{ success, error?, ... }` |

错误码使用 400/404/500/503，输入校验在系统边界处手动完成。

## 后台任务模式

- 业务核心（如硬件通信）在 `create_app()` 时实例化，独立 Daemon 线程运行
- 共享状态用 `threading.Lock` 保护
- 通过 `stop_event` 实现优雅关闭
- **CAN-bus 隔离原则**：监控信号的 bus 与 TP 通信的 bus 必须独立，即使同通道

## 使用步骤

当用户请求创建此类应用时：

1. 与用户确认：项目名称、Python 包名、应用标题、需要的 Tab 列表
2. 阅读 `assets/templates/` 下的三件套，理解结构与风格约定
3. 在目标项目中按"推荐目录结构"创建文件，复用风格约定但**从零编写业务代码**
4. Flask 应用使用 factory 模式（`create_app(config)` 返回 `app`）
5. 路由按 Tab 拆分到独立 Blueprint，避免单文件膨胀
6. 输出启动命令（如 `python -m {{ package_name }} --port 8080`）

## 不要做的事

- ❌ 不要把整个 `assets/templates/` 复制过去当业务代码
- ❌ 不要引入前端框架（React/Vue）——风格约定就是 vanilla JS
- ❌ 不要从 CDN 加载业务必需资源（ECharts 等大文件放本地 `static/`）
- ❌ 不要从 CDN 加载字体（IBM Plex 字体放本地 `static/fonts/`）
- ❌ 不要在 `app.js` 中堆业务函数，保持通用骨架，业务函数另开文件
- ❌ 不要在 base.html 内联大段样式或脚本，保持模板清爽

## 示例唤起

用户："帮我做一个 Flask 的设备调试工具，要有连接、控制、日志三个 Tab，风格专业一点。"

Claude：
1. 使用此 Skill 作为风格与架构参考
2. 询问项目名称、Python 包名、设备接口类型（串口/CAN/TCP）
3. 阅读 `assets/templates/` 三件套，理解 Carbon 风格
4. 在目标目录创建项目骨架（目录结构 + factory + Blueprint）
5. 实现 `core/` 中的设备通信逻辑
6. 输出启动命令
