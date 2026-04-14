#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智谱AI Web Search API 搜索工具
"""

import os
import sys
import json
import argparse
import uuid
from datetime import datetime

import requests


def search(
    query: str,
    api_token: str,
    engine: str = "search_std",
    intent: bool = False,
    count: int = 10,
    domain_filter: str = None,
    recency: str = "noLimit",
    content_size: str = "medium",
    request_id: str = None,
    user_id: str = None,
) -> dict:
    """
    调用智谱AI Web Search API进行搜索

    Args:
        query: 搜索查询词
        api_token: API Token
        engine: 搜索引擎类型 (search_std, search_pro)
        intent: 是否启用搜索意图分析
        count: 返回结果数量 (1-10)
        domain_filter: 域名过滤
        recency: 时间过滤 (noLimit, oneDay, oneWeek, oneMonth)
        content_size: 内容长度 (medium, long)
        request_id: 请求追踪ID
        user_id: 用户ID

    Returns:
        API响应的JSON数据
    """
    url = "https://open.bigmodel.cn/api/paas/v4/web_search"

    # 构建请求payload
    payload = {
        "search_query": query,
        "search_engine": engine,
        "search_intent": intent,
        "count": count,
        "search_recency_filter": recency,
        "content_size": content_size,
    }

    # 添加可选参数
    if domain_filter:
        payload["search_domain_filter"] = domain_filter
    if request_id:
        payload["request_id"] = request_id
    if user_id:
        payload["user_id"] = user_id

    # 设置请求头
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    # 发送请求
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    return response.json()


def format_results(results: dict) -> str:
    """
    格式化搜索结果为可读文本

    Args:
        results: API返回的搜索结果

    Returns:
        格式化的文本字符串
    """
    output = []

    # 基本信息
    output.append(f"搜索请求ID: {results.get('id', 'N/A')}")
    output.append(f"创建时间: {results.get('created', 'N/A')}")
    output.append(f"请求追踪ID: {results.get('request_id', 'N/A')}")
    output.append("")

    # 搜索意图（如果有）
    if "search_intent" in results and results["search_intent"]:
        output.append("## 搜索意图分析")
        for intent in results["search_intent"]:
            output.append(f"- 查询: {intent.get('query', 'N/A')}")
            output.append(f"- 意图: {intent.get('intent', 'N/A')}")
            output.append(f"- 关键词: {intent.get('keywords', 'N/A')}")
        output.append("")

    # 搜索结果
    search_results = results.get("search_result", [])
    if search_results:
        output.append(f"## 搜索结果 (共 {len(search_results)} 条)")
        output.append("")

        for i, result in enumerate(search_results, 1):
            output.append(f"### {i}. {result.get('title', '无标题')}")
            output.append(f"**链接**: {result.get('link', 'N/A')}")
            if result.get("media"):
                output.append(f"**来源**: {result.get('media')}")
            if result.get("publish_date"):
                output.append(f"**发布日期**: {result.get('publish_date')}")
            output.append("")
            output.append(result.get("content", "无内容"))
            output.append("")
            output.append("-" * 80)
            output.append("")
    else:
        output.append("未找到搜索结果")

    return "\n".join(output)


def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(
        description="智谱AI Web Search API 搜索工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python search.py "人工智能发展趋势"
  python search.py "Python编程教程" --count 5
  python search.py "机器学习" --domain-filter zhihu.com
  python search.py "科技新闻" --recency oneWeek
  python search.py "量子计算" --engine search_pro
        """,
    )

    parser.add_argument("query", help="搜索查询词")
    parser.add_argument(
        "--engine",
        choices=["search_std", "search_pro"],
        default="search_std",
        help="搜索引擎类型 (默认: search_std)",
    )
    parser.add_argument(
        "--intent",
        action="store_true",
        help="启用搜索意图分析",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="返回结果数量 (1-10, 默认: 10)",
    )
    parser.add_argument(
        "--domain-filter",
        help="域名过滤 (如: zhihu.com)",
    )
    parser.add_argument(
        "--recency",
        choices=["noLimit", "oneDay", "oneWeek", "oneMonth"],
        default="noLimit",
        help="时间过滤 (默认: noLimit)",
    )
    parser.add_argument(
        "--content-size",
        choices=["medium", "long"],
        default="medium",
        help="内容长度 (默认: medium)",
    )
    parser.add_argument(
        "--request-id",
        help="请求追踪ID (默认: 自动生成)",
    )
    parser.add_argument(
        "--user-id",
        help="用户ID",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="以JSON格式输出结果",
    )

    args = parser.parse_args()

    # 获取API Token
    api_token = os.environ.get("ZHIPU_API_TOKEN")
    if not api_token:
        print(
            "错误: 未设置 ZHIPU_API_TOKEN 环境变量",
            file=sys.stderr,
        )
        print(
            "请设置: export ZHIPU_API_TOKEN='your-token-here'",
            file=sys.stderr,
        )
        sys.exit(1)

    # 生成request_id（如果未提供）
    request_id = args.request_id or str(uuid.uuid4())

    try:
        # 调用搜索API
        results = search(
            query=args.query,
            api_token=api_token,
            engine=args.engine,
            intent=args.intent,
            count=args.count,
            domain_filter=args.domain_filter,
            recency=args.recency,
            content_size=args.content_size,
            request_id=request_id,
            user_id=args.user_id,
        )

        # 输出结果
        if args.json_output:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(format_results(results))

    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"未知错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
