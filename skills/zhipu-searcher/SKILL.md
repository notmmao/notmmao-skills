---
name: zhipu-searcher
description: 使用智谱AI的Web搜索API进行网络搜索。支持自定义搜索条件、时间过滤、域名过滤等功能
allowed-tools: Bash(python *)
---

# Zhipu Searcher

使用智谱AI Web Search API进行网络搜索的工具。

## 前置要求

1. 需要有智谱AI的API Token
2. 设置环境变量 `ZHIPU_API_TOKEN` 或在调用时提供

## 基本用法

```bash
python ./scripts/search.py "搜索关键词"
```

## 请求参数

### 必填参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `search_query` | string | 搜索查询词 |

### 可选参数
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--engine` | string | `search_std` | 搜索引擎类型：`search_std`(标准搜索), `search_pro`(专业搜索) |
| `--intent` | boolean | `false` | 是否启用搜索意图分析 |
| `--count` | int | `10` | 返回结果数量 (1-10) |
| `--domain-filter` | string | 无 | 域名过滤，如 `zhihu.com` 只搜索该域名 |
| `--recency` | string | `noLimit` | 时间过滤：`noLimit`, `oneDay`, `oneWeek`, `oneMonth` |
| `--content-size` | string | `medium` | 内容长度：`medium`(中等), `long`(长) |
| `--request-id` | string | 自动生成 | 请求追踪ID |
| `--user-id` | string | 无 | 用户ID |

## 响应格式

```json
{
  "id": "搜索请求ID",
  "created": 123,
  "request_id": "请求追踪ID",
  "search_intent": [
    {
      "query": "分析的查询词",
      "intent": "SEARCH_ALL",
      "keywords": "提取的关键词"
    }
  ],
  "search_result": [
    {
      "title": "搜索结果标题",
      "content": "搜索结果内容摘要",
      "link": "原始链接",
      "media": "来源媒体",
      "icon": "网站图标",
      "refer": "来源引用",
      "publish_date": "发布日期"
    }
  ]
}
```

## 使用示例

### 1. 基本搜索
```bash
python ./scripts/search.py "2024年人工智能发展趋势"
```

### 2. 指定搜索数量
```bash
python ./scripts/search.py "Python编程教程" --count 5
```

### 3. 限制域名
```bash
python ./scripts/search.py "机器学习入门" --domain-filter zhihu.com
```

### 4. 时间过滤
```bash
python ./scripts/search.py "最新科技新闻" --recency oneWeek
```

### 5. 使用专业搜索引擎
```bash
python ./scripts/search.py "量子计算研究进展" --engine search_pro
```

### 6. 完整参数示例
```bash
python ./scripts/search.py "AI医疗应用" \
  --engine search_pro \
  --count 8 \
  --domain-filter github.com \
  --recency oneMonth \
  --content-size long
```

## 注意事项

1. **API Token**: 必须设置 `ZHIPU_API_TOKEN` 环境变量
   ```bash
   # Windows PowerShell
   $env:ZHIPU_API_TOKEN="your-token-here"
   
   # Linux/Mac
   export ZHIPU_API_TOKEN="your-token-here"
   ```

2. **速率限制**: 注意API调用频率限制

3. **域名过滤**: `search_domain_filter` 支持多个域名（某些引擎）

4. **时间过滤**: `search_recency_filter` 选项：
   - `noLimit`: 无限制
   - `oneDay`: 一天内
   - `oneWeek`: 一周内
   - `oneMonth`: 一月内
