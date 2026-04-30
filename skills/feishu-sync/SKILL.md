---
name: feishu-sync
version: 1.0.0
description: "飞书文档同步：从飞书 Wiki/Docx 下载文档到本地 Markdown，自动转换内嵌表格。支持单个和批量同步。当用户需要同步飞书文档、下载 Wiki 内容、批量拉取飞书文档、同步文档到本地时使用。触发词：同步飞书、sync feishu、feishu-sync、下载飞书文档。"
metadata:
  requires:
    bins: ["lark-cli", "python3"]
---

# feishu-sync

从飞书 Wiki/Docx 同步文档到本地 Markdown 文件，自动将内嵌表格展开为 Markdown 表格。

## 前置条件

1. **lark-cli** 已安装且已认证（`lark-cli auth login`）
2. **python3** 可用

## 快速使用

```
# 单文档同步
/feishu-sync <URL> <输出目录> [文档名]

# 批量同步（多个 URL 用空格分隔）
/feishu-sync <URL1> <URL2> ... --output <输出目录>
```

## 同步脚本

脚本位置：`<skill_dir>/scripts/feishu_sync.py`

### 单文档同步

```bash
python <skill_dir>/scripts/feishu_sync.py <URL> <输出目录> [文档名]
```

参数说明：
| 参数 | 必填 | 说明 |
|------|------|------|
| URL | 是 | 飞书文档 URL（支持 /wiki/、/docs/、/docx/ 格式） |
| 输出目录 | 是 | 本地保存路径 |
| 文档名 | 否 | 自定义文件名，不传则自动提取文档标题 |

示例：
```bash
# 自动提取标题
python <skill_dir>/scripts/feishu_sync.py https://xxx.feishu.cn/wiki/RU3jwhFHpibp1ik7P2NcHUIonKh "接口文档/2026-04-30"

# 指定文档名
python <skill_dir>/scripts/feishu_sync.py https://xxx.feishu.cn/wiki/RU3jwhFHpibp1ik7P2NcHUIonKh "接口文档/2026-04-30" "协议规范"
```

### 输出文件

每次同步生成两个文件：
- `文档名_骨架.md` — 原始版本（保留 `<sheet token="..."/>` 标记）
- `文档名.md` — 完整可读版本（内嵌表格已展开为 Markdown 表格）

### 批量同步

当用户提供多个 URL 时，**逐个调用脚本**，最后汇总结果：

```
步骤：
1. 遍历每个 URL
2. 对每个 URL 执行 python <skill_dir>/scripts/feishu_sync.py <URL> <输出目录>
3. 收集所有结果
4. 输出汇总报告：

   同步完成汇总：
   ✅ 文档A → 接口文档/2026-04-30/文档A.md
   ✅ 文档B → 接口文档/2026-04-30/文档B.md
   ❌ 文档C → 失败：权限不足
   共 3 个文档，成功 2，失败 1
```

### URL 格式支持

| URL 格式 | Token 提取方式 |
|----------|---------------|
| `/wiki/TOKEN` | 路径最后一段 |
| `/docs/TOKEN` | 路径最后一段 |
| `/docx/TOKEN` | 路径最后一段 |

## 工作流程

```
用户提供 URL
    ↓
提取文档 Token
    ↓
调用 lark-cli docs +fetch 获取内容
    ↓
检测内嵌表格 (<sheet token="..."/>)
    ↓ (有表格)
获取 spreadsheet 尺寸 → 读取表格数据 → 转为 Markdown
    ↓
保存两个文件（骨架 + 完整版）
    ↓
（可选）记录到 LOG.md
```

## 与项目集成

如果项目中存在 `LOG.md`，脚本会自动追加同步记录：

```
2026-04-30 - [同步] 飞书文档: 文档名 → 输出目录
```

## 已知限制

1. **嵌入表格**：需要 lark-cli 有 sheets 读取权限
2. **大文档**：超过 60 秒获取超时
3. **权限**：文档必须对当前 lark-cli 认证用户可见

## 错误处理

| 错误 | 原因 | 处理 |
|------|------|------|
| `无法从 URL 中提取文档 token` | URL 格式不正确 | 检查 URL 是否包含 /wiki/、/docs/、/docx/ |
| `获取文档失败` | lark-cli 未认证或无权限 | 运行 `lark-cli auth login` |
| `获取文档超时` | 文档过大 | 手动在飞书中导出 |
| `表格加载失败` | sheets 权限不足 | 表格处标记失败，其余内容正常保存 |
