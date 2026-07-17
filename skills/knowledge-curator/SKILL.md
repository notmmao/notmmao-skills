---
name: knowledge-curator
description: 当用户要求发布或策展工程知识、把项目文档/调试经验/根因分析提炼为可复用知识卡片并纳入共享知识库时使用。识别架构说明、协议描述、部署/CI 实践、框架用法、故障排查、性能优化等可复用内容，重写为脱敏的知识卡片（剥离项目名/人名/敏感信息），按技术分类写入知识库并 git 提交推送。
---

# 用途

把项目里的可复用工程知识，策展成跨项目共享的知识卡片，写入组织知识库并提交。

- 不是同步项目文档，而是提炼可复用知识。
- 知识库完全由 AI 维护（假设无人类维护者）。
- 宁可漏掉一篇有价值的文档，也不要引入低质量知识。
- 存疑时，跳过，什么都不做。

# 配置

- 本地仓库路径：`~/engineering-knowledge`
- 远程仓库地址：`https://gitlab.carota.ai/hil/engineering-knowledge.git`
- 默认分支：`master`

# 初始化

使用本技能前，确保本地仓库就绪：

1. 若本地仓库路径不存在，先 clone：
   `git clone https://gitlab.carota.ai/hil/engineering-knowledge.git ~/engineering-knowledge`
2. 进入仓库并同步最新：`cd ~/engineering-knowledge && git pull --ff-only`
3. 后续所有知识卡片的写入、commit、push 都在该目录下进行
4. 若为首次运行（空仓库），正常提交首个内容即可建立 master 分支

# 何时使用

在以下情况使用：

- 用户明确要求发布或策展知识时
- 任务完成、多个文档文件发生变更后，用户希望沉淀知识时
- 用户指定某文档或目录需要提炼时

绝不打断正常开发流程；仅在明显有价值或被要求时执行。

# 扫描范围

必要时读取整个仓库。

特别关注：

- *.md
- *.mdx

默认忽略：

- TODO
- 日常日志
- 会议记录
- 变更日志
- 临时笔记
- 草稿文档

优先选择包含以下标签的文档：

- share
- publish
- knowledge

# 目标

提取可复用的工程知识。

不是项目历史。

不是业务背景。

不是客户信息。

不是进度跟踪。

知识应在六个月后仍具有价值。

# 评估标准

若一篇文档包含以下一项或多项内容，则可发布：

- 架构说明
- 协议描述
- 调试经验
- 根因分析
- 部署指南
- CI/CD 实践
- 构建系统知识
- API 用法
- 框架用法
- 工程最佳实践
- 故障排查
- 迁移指南
- 逆向工程笔记
- 性能优化
- 可复用脚本
- 工具配置
- 带有理由的设计决策

拒绝以下文档：

- 项目专属内容
- 里程碑报告
- 规划
- 日程安排
- TODO 列表
- 客户沟通
- 会议纪要

# 重写

绝不直接复制文档。

始终将其重写为可复用的知识卡片。

移除：

- 项目名称
- 任务历史
- 个人评论
- 重复解释
- 不必要的截图
- 无关章节

保留：

- 问题
- 环境
- 根因
- 解决方案
- 局限性
- 参考资料

偏好简洁的文档。

# 安全

绝不发布：

- 密码
- 密钥
- 令牌
- 私钥

自动对明显的敏感值进行脱敏。

除非明确标注为机密，否则公司名称可以保留。

# 知识卡片格式

每篇生成的文档应包含：

# 标题

## 问题

描述工程问题。

## 背景

这种情况何时发生？

## 根因

技术层面的解释。

## 解决方案

分步解决方案。

## 注意事项

边界情况。

## 参考资料

原始项目路径。

生成时间。

相关技术。

# 分类

仓库结构由 AI 管理。

你可以：

- 创建目录
- 重命名目录
- 移动文档
- 重新组织分类

优先采用面向技术的分类，而非面向项目的分类。

示例：

automotive/
docker/
python/
embedded/
linux/
testing/
network/
robotframework/
ci/
troubleshooting/

# 现有知识

始终先检查现有仓库。

若已存在相关的知识卡片：

你可以：

- 更新它
- 改进它
- 合并新信息

除非两篇文档提供了有意义的、不同的方法，否则不要创建重复内容。

# 质量规则

仅在以下情况下发布：

- 可复用
- 技术正确
- 自包含
- 无需原项目即可理解

否则跳过。

# README 目录

README.md 是知识库的目录索引，必须与卡片同步维护。

格式：按分类（一级目录）分组，每张卡片一行 `[标题](相对路径) - 入库时间 - 作者 - 源仓库`。

- 入库时间：卡片首次入库的日期（`date +%F`）。
- 作者：取当前 git 提交作者（`git config user.name`）。
- 源git仓库：来源项目的 git 远程地址（`git -C <源项目路径> remote get-url origin`）；无则填 `-`。

```markdown
# Engineering Knowledge Base

由 knowledge-curator 自动维护。跨项目共享的工程知识卡片。

## 目录

### docker
- [Docker 容器 DNS 解析失败排查](docker/container-dns-resolution-failure.md) - 2026-07-17 - 张三 - https://gitlab.carota.ai/foo/bar.git

### network
- [Nginx upstream keepalive 502](network/nginx-upstream-keepalive-502.md) - 2026-07-17 - 李四 - -
```

- 新增卡片：在对应分类下追加一行，填入入库时间、作者、源仓库；分类不存在则新建 `### 分类名` 标题。
- 更新/删除卡片：同步修改或移除目录对应行；更新时保留原入库时间。

# 发布

卡片写好、README 目录更新后，用发布脚本一次性完成 pull → add → commit → push，不要逐行手动执行 git：

```bash
bash ~/engineering-knowledge/scripts/publish.sh <分类>/<卡片>.md -m "knowledge: add <主题>"
```

脚本封装了：同步远程（`git pull --ff-only`）→ 暂存 README 与卡片 → 提交 → 推送。支持一次发布多张卡片：

```bash
bash ~/engineering-knowledge/scripts/publish.sh docker/a.md network/b.md -m "knowledge: add ..."
```

提交信息规范（中文）：

- 新增：`kb: [docker] 容器 DNS 解析失败排查`
- 改进：`kb: [network] Nginx upstream keepalive 502`
- 更新：`kb: [robotframework] 测试最佳实践`

自动推送，无需人工确认。

# 理念

知识库是活着的工程记忆。

为长期价值而优化。

不为数量而优化。

一篇优秀的知识卡片胜过五十篇平庸的文档。
