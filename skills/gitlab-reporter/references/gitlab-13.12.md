# GitLab 13.12.x API 参考

GitLab 13.12.x 是常见的自托管实例版本，与最新版本存在 API 差异。

## 如何判断 GitLab 版本

```bash
curl --header "PRIVATE-TOKEN: YOUR_TOKEN" "https://your-gitlab/api/v4/version"
```

返回示例：
```json
{
  "version": "13.12.12"
}
```

## Events API (推荐用于周报生成)

**端点:** `GET /users/:id/events`

### ✅ 支持的参数

| 参数 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `after` | date | 否 | 返回此日期之后（不含）创建的事件，格式 `YYYY-MM-DD` |
| `before` | date | 否 | 返回此日期之前（不含）创建的事件，格式 `YYYY-MM-DD` |
| `per_page` | integer | 否 | 每页结果数 (默认 20，最大 100) |
| `action` | string | 否 | 事件类型 (如 `pushed_to`, `merged`, `closed`) |
| `target_type` | string | 否 | 目标类型 (如 `Issue`, `MergeRequest`) |
| `sort` | string | 否 | 排序方式 (`asc` 或 `desc`) |
| `scope` | string | 否 | 事件范围 (如 `all`) |

### 返回字段

```json
[
  "id", "author", "author_id", "author_username",
  "created_at", "project_id", "action_name",
  "target_id", "target_iid", "target_title", "target_type",
  "push_data"
]
```

### push_data 字段结构

当 `action_name` 为 `pushed to` 时，`push_data` 包含：

```json
{
  "commit_count": 3,
  "commit_from": "abc123",
  "commit_to": "def456",
  "commit_title": "单个提交时的标题",
  "ref": "master",
  "ref_type": "branch"
}
```

### 常见事件类型

- `pushed to` - 代码推送
- `merged` - MR 已合并
- `created` - MR/Issue 已创建
- `closed` - Issue 已关闭
- `commented on` - 发表评论

### 使用示例

```bash
# 获取本周用户事件
GET /users/7/events?after=2026-05-18&before=2026-05-25

# 只获取 push 事件
GET /users/7/events?action=pushed_to&per_page=100

# 只获取 Issue 相关事件
GET /users/7/events?target_type=Issue
```

**注意:** `before` 和 `after` 都是**不包含**边界日期的，如果需要包含 5月18日，`after` 应设为 `2026-05-17`。

## Compare API (获取提交详情)

**端点:** `GET /projects/:id/repository/commits`

使用 `ref_name` 参数比较两个 commit 之间的提交：

```bash
# 获取 commit_from 到 commit_to 之间的所有提交
GET /projects/123/repository/commits?ref_name=def456...abc123
```

**注意:** 格式为 `to...from`（三个点）

### 返回示例

```json
[
  {
    "id": "xyz789",
    "title": "提交标题",
    "message": "完整提交信息",
    "author_name": "作者名",
    "author_email": "作者邮箱",
    "created_at": "2026-05-20T10:30:00Z"
  }
]
```

## Commits API 差异

**端点:** `GET /projects/:id/repository/commits`

### ✅ 支持的参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `since` | string | 起始日期 (ISO 8601: `2026-05-18T00:00:00Z`) |
| `until` | string | 结束日期 (ISO 8601: `2026-05-24T23:59:59Z`) |
| `per_page` | integer | 每页结果数 (默认 20，最大 100) |
| `ref_name` | string | 分支或标签名（或比较范围 `to...from`）|
| `with_stats` | boolean | 包含统计信息 (additions/deletions) |
| `first_parent` | boolean | 仅跟随第一个父提交 |
| `all` | boolean | 获取所有提交 |

### ❌ 不支持的参数

| 参数 | 状态 | 说明 |
|------|------|------|
| `author` | 被忽略 | 设置任何值都返回所有提交 |
| `path` | 返回空结果 | 文件路径过滤不可用 |
| `order` | 被忽略 | 排序参数无效 |

## 推荐方案对比

### Events API vs Commits API

| 特性 | Events API | Commits API |
|------|-----------|-------------|
| 按用户过滤 | ✅ 原生支持 | ❌ 不支持（13.12）|
| 跨项目查询 | ✅ 一次调用 | ❌ 需逐项目查询 |
| 日期过滤 | ✅ | ✅ |
| 事件类型 | push/MR/issue | 仅提交 |
| 准确性 | 100% 用户数据 | 可能混入其他用户 |

### 周报生成最佳实践

```python
# 步骤1: 获取用户事件
events = GET /users/{user_id}/events?after={date}

# 步骤2: 筛选 push 事件
push_events = [e for e in events if e['action_name'] == 'pushed to']

# 步骤3: 对每次 push 获取提交详情
if push_event['commit_count'] == 1:
    # 单个提交，直接使用 commit_title
    commit_title = push_event['commit_title']
else:
    # 多个提交，使用 compare API
    commits = GET /projects/{id}/repository/commits?ref_name={to}...{from}
```

**推荐:** 周报生成使用 **Events API + Compare API** 组合，确保只统计用户本人的提交。
