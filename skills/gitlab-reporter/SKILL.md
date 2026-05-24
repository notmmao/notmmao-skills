---
name: gitlab-reporter
description: 从 GitLab 获取用户活动并生成周报。支持 GitLab.com 和自托管实例。当用户需要生成周报、整理 GitLab 提交记录、汇总工作内容时使用。
---

# GitLab Reporter - 周报生成技能

## 功能

- 📊 自动收集 GitLab 活动（提交、MR、Issues）
- 📝 生成原始周报 Markdown
- ✨ AI 润色为专业报告
- 🌐 支持 GitLab.com 和自托管实例
- ⚡ 优化版：使用 events API，只统计本人提交

## 配置

### 方式一：使用 .env 文件（推荐）

在项目目录创建 `.env` 文件：

```bash
# GitLab.com 使用默认 URL，可省略
GITLAB_BASE_URL=https://gitlab.com/api/v4
GITLAB_ACCESS_TOKEN=your_token_here
GITLAB_USERNAME=your_username

# 自托管实例示例
# GITLAB_BASE_URL=https://your-gitlab.example.com/api/v4
# GITLAB_ACCESS_TOKEN=your_token_here
# GITLAB_USERNAME=your_username
```

### 方式二：命令行参数

```bash
# GitLab.com
python scripts/generate_report.py --token YOUR_TOKEN --username yourname

# 自托管实例
python scripts/generate_report.py --url https://your-gitlab.example.com/api/v4 --token YOUR_TOKEN --username yourname
```

### 获取 GitLab Token

1. **GitLab.com**: 访问 https://gitlab.com/-/user_settings/personal_access_tokens
2. **自托管实例**: 访问 `https://your-gitlab.example.com/-/user_settings/personal_access_tokens`
3. 创建 token，勾选 `api` 和 `read_api` 权限

## 使用方法

### 1. 生成原始周报

运行脚本后会生成 `weekly_report_XX.md` 文件（XX 为周数）：

```bash
python scripts/generate_report.py
```

**工作原理：**
- 通过用户的 events API 获取 push 事件
- 使用 compare API 获取提交详情
- **只统计用户本人的提交**，不会混入团队成员的提交

### 2. 润色周报

读取生成的原始报告，按照以下模板润色：

```markdown
# 周报 - 第 XX 周（YYYY.MM.DD - YYYY.MM.DD）

## 本周概述
[按项目分类总结，不要按时间写流水账]

---

## 工作内容

### 项目 A
- 主要进展
- 关键成果

### 项目 B
- ...

---

## 下周计划

---

## 风险与问题
```

润色后的报告保存为 `weekly_report_XX_润色.md`

## 依赖说明

- `python-dotenv` 是可选的，如果没有安装，脚本会跳过 .env 文件加载
- 如果使用 .env 文件，可安装：`pip install python-dotenv`
- 必需依赖：`requests`（安装：`pip install requests`）

## 输出文件

- `weekly_report_XX.md` - 原始报告（按时间排序）
- `weekly_report_XX_润色.md` - 润色后的专业报告

## GitLab 版本差异

**自托管实例注意:** 不同版本的 GitLab API 存在差异。

当遇到以下情况时，读取 `references/gitlab-13.12.md`:
- API 参数不生效（如 `author` 参数被忽略）
- 需要了解特定版本支持的 API 功能
- 自托管实例版本为 13.12.x

**快速判断版本:**
```bash
curl --header "PRIVATE-TOKEN: YOUR_TOKEN" "https://your-gitlab/api/v4/version"
```
