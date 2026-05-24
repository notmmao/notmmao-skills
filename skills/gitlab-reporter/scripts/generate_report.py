#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从 GitLab 获取用户活动并生成周报
优化：使用 events API + compare API 减少 API 调用次数
支持 GitLab.com 和自托管实例
"""

import os
import sys
import argparse
import requests
from datetime import datetime, timedelta
from collections import defaultdict

# 可选加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

HEADERS = None


def init_config(args):
    """初始化配置，优先级：命令行参数 > .env 文件 > 默认值"""
    global GITLAB_BASE_URL, GITLAB_TOKEN, USERNAME, HEADERS

    # 从命令行参数或 .env 获取配置
    GITLAB_BASE_URL = args.url if args.url else os.getenv("GITLAB_BASE_URL", "https://gitlab.com/api/v4")
    GITLAB_TOKEN = args.token if args.token else os.getenv("GITLAB_ACCESS_TOKEN")
    USERNAME = args.username if args.username else os.getenv("GITLAB_USERNAME")

    # 验证必需参数
    if not GITLAB_TOKEN:
        print("错误：未找到 GitLab Token，请通过 --token 参数或 .env 文件提供")
        sys.exit(1)

    if not USERNAME:
        print("错误：未指定用户名，请通过 --username 参数或 .env 文件提供")
        sys.exit(1)

    HEADERS = {
        "PRIVATE-TOKEN": GITLAB_TOKEN,
        "Content-Type": "application/json"
    }

    return GITLAB_BASE_URL, GITLAB_TOKEN, USERNAME, HEADERS


def get_week_range():
    """获取本周一到今天的日期范围"""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    return monday, today


def get_week_number(date):
    """获取 ISO 周数 (一年中的第几周)"""
    return date.isocalendar()[1]


def get_user_id(username):
    """通过用户名获取用户 ID"""
    url = f"{GITLAB_BASE_URL}/users?username={username}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    users = response.json()
    if users:
        return users[0]["id"]
    raise ValueError(f"用户 {username} 未找到")


def get_user_events(user_id, since_date):
    """获取用户活动事件，返回项目信息和 push 事件"""
    url = f"{GITLAB_BASE_URL}/users/{user_id}/events"
    # after 参数返回指定日期之后（不含）的事件，所以需要减去一天来包含 since_date 当天
    after_date = since_date - timedelta(days=1)
    params = {
        "after": after_date.strftime("%Y-%m-%d"),
        "per_page": 100
    }

    project_ids = set()
    push_events = []

    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()
        events = response.json()

        for event in events:
            project_id = event.get("project_id")
            if not project_id:
                continue

            project_ids.add(project_id)

            # 收集 push 事件
            if event.get("action_name") == "pushed to" and event.get("push_data"):
                push_events.append({
                    "project_id": project_id,
                    "created_at": event["created_at"],
                    "push_data": event["push_data"]
                })

    except requests.exceptions.RequestException as e:
        print(f"获取事件失败：{e}")

    return list(project_ids), push_events


def get_project_info(project_id):
    """获取单个项目信息，返回 URL 编码的路径"""
    from urllib.parse import quote
    url = f"{GITLAB_BASE_URL}/projects/{project_id}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "id": data["id"],
                "path": data["path"],
                "name": data["name"],
                "path_encoded": quote(data.get("path_with_namespace", data["path"]), safe='')
            }
    except:
        pass
    return {"id": project_id, "path": f"project-{project_id}", "name": f"Project {project_id}", "path_encoded": str(project_id)}


def get_commits_between(project_info, from_sha, to_sha):
    """使用 compare API 获取两个 commit 之间的提交"""
    url = f"{GITLAB_BASE_URL}/projects/{project_info['path_encoded']}/repository/commits"
    params = {"ref_name": f"{to_sha}...{from_sha}"}

    commits = []
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            for commit in data:
                commits.append({
                    "project": project_info["path"],
                    "message": commit["title"],
                    "date": commit["created_at"],
                    "type": "commit"
                })
    except requests.exceptions.RequestException:
        pass

    return commits


def get_merge_requests(author_id):
    """获取用户的合并请求"""
    mrs = []
    url = f"{GITLAB_BASE_URL}/merge_requests"
    params = {
        "author_id": author_id,
        "per_page": 100,
        "state": "all"
    }
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()
        for mr in response.json():
            mrs.append({
                "project_id": mr["source_project_id"],
                "title": mr["title"],
                "iid": mr["iid"],
                "state": mr["state"],
                "created_at": mr["created_at"],
                "updated_at": mr["updated_at"],
                "merged_at": mr.get("merged_at"),
                "type": "mr"
            })
    except requests.exceptions.RequestException as e:
        print(f"获取 MR 失败：{e}")
    return mrs


def get_issues(author_id):
    """获取用户创建的 issues"""
    issues = []
    url = f"{GITLAB_BASE_URL}/issues"
    params = {
        "author_id": author_id,
        "per_page": 100,
        "state": "all"
    }
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()
        for issue in response.json():
            issues.append({
                "project_id": issue["project_id"],
                "title": issue["title"],
                "iid": issue["iid"],
                "state": issue["state"],
                "created_at": issue["created_at"],
                "closed_at": issue.get("closed_at"),
                "type": "issue"
            })
    except requests.exceptions.RequestException as e:
        print(f"获取 Issues 失败：{e}")
    return issues


def parse_date(date_str):
    """解析 ISO 日期字符串为 datetime"""
    date_str = date_str.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S")


def generate_report():
    """生成周报"""
    print("正在生成周报...")

    # 1. 获取日期范围
    monday, today = get_week_range()
    print(f"本周范围：{monday.strftime('%Y-%m-%d')} 到 {today.strftime('%Y-%m-%d')}")

    # 2. 获取用户 ID
    user_id = get_user_id(USERNAME)
    print(f"用户 ID: {user_id}")

    # 3. 获取用户活动事件和项目列表
    print("正在获取用户活动事件...")
    project_ids, push_events = get_user_events(user_id, monday)
    print(f"  找到 {len(project_ids)} 个项目，{len(push_events)} 次 push")

    # 4. 获取项目信息
    print("正在获取项目信息...")
    projects = {}
    for pid in project_ids:
        info = get_project_info(pid)
        projects[pid] = info
        print(f"  - {info['path']}")

    # 5. 收集所有活动
    all_activities = defaultdict(list)

    # 处理 push 事件获取提交记录
    print("正在获取提交记录...")
    for event in push_events:
        project_id = event["project_id"]
        project_info = projects.get(project_id, {})
        if not project_info:
            continue
        project_name = project_info.get("path", f"project-{project_id}")
        push_data = event["push_data"]
        commit_count = push_data.get("commit_count", 0)

        if commit_count == 1:
            # 单个提交，直接使用 commit_title
            all_activities[parse_date(event["created_at"]).date()].append({
                "project": project_name,
                "message": push_data["commit_title"],
                "type": "commit"
            })
        elif commit_count > 1:
            # 多个提交，使用 compare API
            commits = get_commits_between(
                project_info,
                push_data["commit_from"],
                push_data["commit_to"]
            )
            for commit in commits:
                date = parse_date(commit["date"]).date()
                all_activities[date].append(commit)

    print(f"  共获取 {sum(len(v) for v in all_activities.values())} 条提交记录")

    # 获取 MR
    print("正在获取合并请求...")
    mrs = get_merge_requests(user_id)
    for mr in mrs:
        activity_date = mr.get("merged_at") or mr.get("updated_at") or mr["created_at"]
        date = parse_date(activity_date).date()
        if monday.date() <= date <= today.date():
            mr["project_name"] = projects.get(mr["project_id"], {}).get("path", f"project-{mr['project_id']}")
            all_activities[date].append(mr)
            print(f"  找到 MR: {mr['project_name']}#{mr['iid']}")

    # 获取 Issues
    print("正在获取 Issues...")
    issues = get_issues(user_id)
    for issue in issues:
        activity_date = issue.get("closed_at") or issue["created_at"]
        date = parse_date(activity_date).date()
        if monday.date() <= date <= today.date():
            issue["project_name"] = projects.get(issue["project_id"], {}).get("path", f"project-{issue['project_id']}")
            all_activities[date].append(issue)
            print(f"  找到 Issue: {issue['project_name']}#{issue['iid']}")

    # 6. 生成 Markdown
    print("正在生成报告...")
    markdown = generate_markdown(all_activities, monday, today)

    # 7. 保存文件
    week_num = get_week_number(monday)
    output_file = f"weekly_report_{week_num:02d}.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"\n周报已保存到：{output_file}")
    return output_file


def generate_markdown(activities, start_date, end_date):
    """生成 Markdown 格式报告"""
    lines = []
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

    current = start_date
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        weekday_str = weekdays[current.weekday()]
        lines.append(f"### {weekday_str} - {date_str}")
        lines.append("")

        if current.date() in activities and activities[current.date()]:
            by_project = defaultdict(list)
            for activity in activities[current.date()]:
                project = activity.get("project", activity.get("project_name", "unknown"))
                by_project[project].append(activity)

            for project, items in sorted(by_project.items()):
                lines.append(f"- **{project}**")
                for item in items:
                    if item["type"] == "commit":
                        lines.append(f"  - 📝 {item['message']}")
                    elif item["type"] == "mr":
                        state_icon = "✅" if item.get("merged_at") else ("🔄" if item["state"] == "opened" else "📋")
                        lines.append(f"  - {state_icon} MR #{item['iid']}: {item['title']}")
                    elif item["type"] == "issue":
                        state_icon = "✅" if item["state"] == "closed" else "📋"
                        lines.append(f"  - {state_icon} Issue #{item['iid']}: {item['title']}")
                lines.append("")
        else:
            lines.append("没有任何活动")
            lines.append("")

        current += timedelta(days=1)

    return "\n".join(lines)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="从 GitLab 获取用户活动并生成周报（优化版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用 .env 文件中的配置
  python generate_report.py

  # 通过命令行参数传入配置
  python generate_report.py --url https://gitlab.com/api/v4 --token YOUR_TOKEN --username yourname

  # 使用自托管 GitLab 实例
  python generate_report.py --url https://your-gitlab.example.com/api/v4 --token YOUR_TOKEN --username yourname
        """
    )
    parser.add_argument(
        "--url",
        type=str,
        help="GitLab API URL（默认：https://gitlab.com/api/v4）"
    )
    parser.add_argument(
        "--token", "-t",
        type=str,
        help="GitLab Access Token"
    )
    parser.add_argument(
        "--username", "-u",
        type=str,
        help="GitLab 用户名"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    init_config(args)
    generate_report()
