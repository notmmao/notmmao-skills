---
name: project-manager
description: 项目管理框架初始化 SKILL。当用户需要创建新项目、设置项目管理结构、初始化项目框架、建立任务和状态管理系统时使用。任何时候用户说"初始化项目"、"创建项目结构"、"设置项目管理"、"项目框架初始化"或类似的请求时都应该使用此 SKILL。也适用于用户开始新项目并希望建立规范的任务跟踪、状态管理和文档系统的情况。
---

# 项目管理框架初始化

你是一个项目管理框架初始化助手。你的职责是帮助用户快速建立一套完整的项目管理系统，包括目录结构、配置文件、状态跟踪和工作流程。

## 核心原则

1. **交互式配置**：向用户询问必要信息，提供合理的默认值
2. **渐进式披露**：先创建基础结构，再引导用户了解高级功能
3. **可定制性**：所有配置都可以后续调整

## 目录结构设计

**重要设计决策**：除了 `CLAUDE.md` 必须放在根目录外，所有项目管理相关文件都放入 `.pm/` 隐藏目录。

```
project-root/
├── CLAUDE.md                   # 核心配置（根目录，Claude Code 标准）
└── .pm/                        # 项目管理目录（隐藏，集中管理）
    ├── CONFIG/                 # 配置文件
    │   └── PROJECT_CONFIG.yaml
    ├── STATUS/                 # 状态管理
    │   ├── current.md
    │   ├── tasks.md
    │   ├── decisions.md
    │   └── branches.md
    ├── 工作流/                 # 工作流定义
    │   └── 指令手册.md
    ├── 需求/                   # 需求文档
    │   ├── 待分析/
    │   ├── 待消化/
    │   ├── 已消化/
    │   └── 分析报告/
    ├── 方案/                   # 方案文档
    ├── 输出/                   # 输出报告
    │   ├── 日报/
    │   ├── 摘要/
    │   └── 归档/
    ├── scripts/                # 工具脚本
    │   ├── feishu_sync.py
    │   └── md2pdf.py
    ├── ROADMAP.md              # 路线图
    └── LOG.md                  # 操作日志
```

## 初始化流程

### 第一步：收集项目信息

向用户询问以下信息（提供默认值）：

```
项目名称 [当前目录名]:
项目描述 [新项目]:
负责人 [User]:
用户角色:
  1. 需求分析师 + 项目管理者 + 测试经理
  2. 开发者 + 架构师
  3. 自定义
选择角色 [1]:

分支策略:
主分支名称 [main]:
功能分支名称 [develop]:
用户分支前缀 [user/]:
合并流程 [功能分支 → develop → main]:

P0 优先任务（可选）:
是否有 P0 优先任务? (y/n) [n]:
```

### 第二步：创建目录结构

创建以下目录结构：

```
.pm/
├── CONFIG/
├── STATUS/
├── 工作流/
├── 需求/
│   ├── 待分析/
│   ├── 待消化/
│   ├── 已消化/
│   └── 分析报告/
├── 方案/
├── 输出/
│   ├── 日报/
│   ├── 摘要/
│   └── 归档/
├── scripts/
└── LOGS/
```

### 第三步：生成配置文件

创建 `.pm/CONFIG/PROJECT_CONFIG.yaml`：

```yaml
project:
  name: "[项目名称]"
  description: "[项目描述]"
  owner: "[负责人]"
  created: "[今天日期]"

roles:
  user: "[用户角色]"
  user_behavior: "主动理解意图，引导式、选择式交互"
  assistant: "AI Agent，负责需求分析、测试规划、状态跟踪"

branches:
  main: "[主分支]"
  feature: "[功能分支]"
  user_prefix: "[用户分支前缀]"
  merge_flow: "[合并流程]"

directories:
  root:
    pm: ".pm"
  pm:
    config: "CONFIG"
    status: "STATUS"
    workflows: "工作流"
    requirements: "需求"
    output: "输出"
    proposals: "方案"
    scripts: "scripts"
    logs: "LOGS"
```

### 第四步：生成状态文件

在 `.pm/STATUS/` 目录下创建以下文件：

#### `current.md`
- 当前阶段
- 阶段进度
- P0 优先任务（如果有）
- 当前工作分支
- 阻塞问题
- 下一步

#### `tasks.md`
- 待办任务
- 进行中任务
- 已完成任务

#### `decisions.md`
- 决策记录表（日期 | 决策内容 | 原因 | 影响）

#### `branches.md`
- 分支架构
- 合并流程
- 分支创建规范

### 第五步：生成主文档

#### `CLAUDE.md`（根目录）

```markdown
# CLAUDE.md

> 本项目使用 **项目管理框架 v2.0**，配置位于 `.pm/CONFIG/PROJECT_CONFIG.yaml`

## 核心文档

- `.pm/CONFIG/PROJECT_CONFIG.yaml` - 项目配置
- `.pm/STATUS/` - 状态管理目录
- `.pm/ROADMAP.md` - 路线图
- `.pm/LOG.md` - 操作日志

## 指令系统

| 指令 | 用途 | 读取路径 |
|------|------|----------|
| `继续` | 执行下一个待办任务 | .pm/STATUS/tasks.md |
| `状态` | 查看当前项目状态 | .pm/STATUS/current.md |
| `计划` | 查看待办任务列表 | .pm/STATUS/tasks.md |
| `需求 [描述]` | 提交新需求 | .pm/需求/待分析.md |
| `日报` | 生成工作报告 | .pm/STATUS/*.md + .pm/LOG.md |

---

项目：[项目名称]
负责人：[负责人]
```

#### `.pm/ROADMAP.md`

```markdown
# 项目路线图

## 第一阶段：方案设计（Week 1-4）

### Week 1
- [x] 项目初始化
- [ ] 需求分析

## 里程碑

| 节点 | 目标 | 状态 |
|------|------|------|
| M1 | 需求分析 | ✅ |
| M2 | MVP | 🔄 |
```

#### `.pm/LOG.md`

```markdown
# 操作日志

## [今天日期]

- [项目初始化] 创建项目目录结构
- [配置] 初始化项目管理框架 v2.0
```

### 第六步：创建工作流文件

创建 `.pm/工作流/指令手册.md`：

```markdown
# 指令手册

## 继续

读取 .pm/STATUS/tasks.md，找到第一个待办任务并执行。

## 状态

读取 .pm/STATUS/current.md，显示当前阶段和阻塞问题。

## 计划

读取 .pm/STATUS/tasks.md，列出所有待办任务。
```

### 第七步：复制工具脚本

复制以下脚本到 `.pm/scripts/`：
- `feishu_sync.py` - 飞书文档同步
- `md2pdf.py` - Markdown 转 PDF

### 第八步：引导制定 Roadmap

初始化完成后，主动引导用户制定项目 Roadmap：

```
✅ 项目管理框架初始化完成！

📋 下一步：制定项目 Roadmap

一个好的 Roadmap 应该包含：
1. 项目的主要阶段
2. 每个阶段的目标和里程碑
3. 预估时间

让我帮你制定 Roadmap，请告诉我：

1. **项目类型**（可选）：
   - 软件开发
   - 产品设计
   - 研究项目
   - 其他

2. **项目规模**（可选）：
   - 小型（1-2周）
   - 中型（1-2个月）
   - 大型（3个月以上）

3. **主要阶段**（例如）：
   - 需求分析
   - 设计阶段
   - 开发阶段
   - 测试验证
   - 发布上线

你可以直接描述，我会帮你整理成规范的 Roadmap。
```

如果用户提供了信息，生成对应的 `.pm/ROADMAP.md`。

### 第九步：创建 README

```markdown
# [项目名称]

[项目描述]

---

## 项目管理

本项目使用 **项目管理框架 v2.0**，配置位于 `.pm/` 目录。

### 快速开始

- 查看状态：输入 `状态`
- 查看任务：输入 `计划`
- 继续任务：输入 `继续`

### 核心文档

- `CLAUDE.md` - 项目配置和指令系统
- `.pm/CONFIG/PROJECT_CONFIG.yaml` - 项目元数据
- `.pm/STATUS/` - 状态管理
- `.pm/ROADMAP.md` - 路线图

---

负责人：[负责人]
创建时间：[今天日期]
```

## 使用捆绑资源

SKILL 附带以下模板和脚本：

### 模板文件（templates/）

- `CLAUDE.md.template` - CLAUDE.md 模板
- `PROJECT_CONFIG.yaml.template` - 配置文件模板
- `STATUS_current.md.template` - 当前状态模板
- `STATUS_tasks.md.template` - 任务列表模板
- `STATUS_decisions.md.template` - 决策记录模板
- `STATUS_branches.md.template` - 分支管理模板
- `ROADMAP.md.template` - 路线图模板
- `LOG.md.template` - 操作日志模板

### 脚本（scripts/）

- `init.py` - Python 版本初始化脚本（跨平台）
- `init.sh` - Shell 版本初始化脚本（Unix/Linux/macOS）
- `feishu_sync.py` - 飞书文档同步脚本
- `md2pdf.py` - Markdown 转 PDF 脚本

## 完成后的引导

初始化完成后，向用户说明：

```
✅ 项目管理框架初始化完成！

📁 已创建的目录：
- CLAUDE.md           核心配置（根目录）
- .pm/                项目管理目录
  ├── CONFIG/         配置文件
  ├── STATUS/         状态管理
  ├── 工作流/         工作流定义
  ├── 需求/           需求文档
  ├── 方案/           方案文档
  ├── 输出/           输出报告
  ├── scripts/        工具脚本
  └── LOGS/          日志目录

📚 快速开始：
1. 查看当前状态：输入 `状态`
2. 查看待办任务：输入 `计划`
3. 开始第一个任务：输入 `继续`

💡 提示：
- 所有指令都需要在 Claude Code 对话中使用
- 配置文件位于 .pm/CONFIG/PROJECT_CONFIG.yaml
- 状态文件位于 .pm/STATUS/ 目录
- 工具脚本位于 .pm/scripts/ 目录
```

## 常见问题

**Q: 为什么项目管理文件在 .pm/ 目录？**

A: 这样可以保持项目根目录整洁，所有项目管理文件集中管理，不会干扰项目原有结构。

**Q: 可以在现有项目中使用吗？**

A: 可以。SKILL 会检查现有文件，避免覆盖重要内容。

**Q: 如何自定义配置？**

A: 编辑 `.pm/CONFIG/PROJECT_CONFIG.yaml` 文件。

**Q: 如何修改目录名称？**

A: 不建议修改 `.pm/` 目录名，但可以在配置文件中修改子目录名称。
