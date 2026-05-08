# Project Manager SKILL

项目管理框架初始化 SKILL - 快速在任何项目中建立完整的项目管理系统。

## 目录结构设计

本 SKILL 采用 **集中式管理** 设计，除了 `CLAUDE.md` 必须在根目录外，所有项目管理文件都放入 `.pm/` 隐藏目录。

```
project-root/
├── CLAUDE.md                   # 核心配置（根目录，Claude Code 标准）
└── .pm/                        # 项目管理目录（隐藏，集中管理）
    ├── CONFIG/                 # 配置文件
    │   └── PROJECT_CONFIG.yaml
    ├── STATUS/                 # 状态管理
    ├── 工作流/                 # 工作流定义
    ├── 需求/                   # 需求文档
    ├── 方案/                   # 方案文档
    ├── 输出/                   # 输出报告
    ├── scripts/                # 工具脚本
    ├── ROADMAP.md              # 路线图
    └── LOG.md                  # 操作日志
```

### 设计优势

- 项目根目录更整洁
- 项目管理文件集中管理
- 不会干扰项目原有结构
- 易于迁移和维护

## 安装

### 方法 1：复制 SKILL 目录

```bash
cp -r project-manager ~/.claude/skills/
```

### 方法 2：创建符号链接

```bash
ln -s /path/to/project-manager ~/.claude/skills/project-manager
```

## 使用

### 在 Claude Code 中使用

```
你: 初始化项目
→ Claude 将使用 project-manager SKILL 创建完整的项目管理结构

你: 帮我设置项目管理系统
→ Claude 将引导你完成配置
```

### 支持的触发词

- "初始化项目"
- "创建项目结构"
- "设置项目管理"
- "项目框架初始化"
- "建立项目管理系统"
- "设置任务跟踪系统"

## 捆绑工具

### 脚本

- `init.py` - Python 版本初始化脚本（跨平台）
- `init.sh` - Shell 版本初始化脚本（Unix/Linux/macOS）
- `feishu_sync.py` - 飞书文档同步脚本
- `md2pdf.py` - Markdown 转 PDF 脚本

## 测试结果

### Iteration 1

| 测试用例 | 结果 |
|----------|------|
| 基础初始化 | ✅ 通过 |
| 自定义配置 | ✅ 通过 |
| 简单输出 | ✅ 通过 |
| 中文目录 | ✅ 通过 |

**通过率：100%**

## 版本历史

### v2.0.0 (2026-05-08)

- 🎉 采用 `.pm/` 集中式目录结构
- ✨ 添加飞书同步和 PDF 生成脚本
- ✨ 清理所有隐私信息
- ✨ 100% 测试通过率

### v1.0.0 (2026-05-08)

- 初始版本发布
- 支持交互式配置
- 支持自定义项目配置

## 故障排查

### SKILL 没有触发

确保 SKILL 已正确安装到 `~/.claude/skills/` 目录。

### 文件创建失败

检查目标目录的写入权限。

### 中文目录名问题

在某些系统上，中文目录名可能需要额外的编码设置。
