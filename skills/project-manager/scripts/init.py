#!/usr/bin/env python3
"""
项目管理框架 v2.0 初始化脚本

用法：
    python init.py              # 交互式初始化
    python init.py --config     # 从配置文件初始化
    python init.py --help       # 显示帮助
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

# 模板占位符
PLACEHOLDERS = {
    "PROJECT_NAME": "",
    "PROJECT_DESCRIPTION": "",
    "OWNER_NAME": "",
    "TODAY": datetime.now().strftime("%Y-%m-%d"),
    "USER_ROLE": "需求分析师 + 项目管理者",
    "MAIN_BRANCH": "main",
    "FEATURE_BRANCH": "develop",
    "USER_PREFIX": "user/",
    "MERGE_FLOW": "功能分支 → develop → main",
    "P0_TASK_NAME": "",
    "P0_TASK_GOAL": "",
}


def print_header(text: str):
    """打印标题"""
    print("\n" + "=" * 50)
    print(f"  {text}")
    print("=" * 50)


def print_step(step: int, text: str):
    """打印步骤"""
    print(f"\n[{step}] {text}")


def ask_question(prompt: str, default: str = "") -> str:
    """询问用户输入"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()


def fill_template(content: str, placeholders: dict) -> str:
    """填充模板内容"""
    result = content
    for key, value in placeholders.items():
        placeholder = "{{" + key + "}}"
        result = result.replace(placeholder, value)
    return result


def create_directory_structure(project_root: Path):
    """创建目录结构"""
    print_step(1, "创建目录结构...")

    directories = [
        ".pm/CONFIG",
        ".pm/STATUS",
        ".pm/工作流",
        ".pm/需求/待分析",
        ".pm/需求/待消化",
        ".pm/需求/已消化",
        ".pm/需求/分析报告",
        ".pm/方案",
        ".pm/输出/日报",
        ".pm/输出/摘要",
        ".pm/输出/归档",
        ".pm/scripts",
        ".pm/LOGS",
    ]

    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ 创建: {directory}/")


def collect_user_info() -> dict:
    """收集用户信息"""
    print_step(2, "收集项目信息...")

    placeholders = PLACEHOLDERS.copy()

    placeholders["PROJECT_NAME"] = ask_question("项目名称", os.path.basename(os.getcwd()))
    placeholders["PROJECT_DESCRIPTION"] = ask_question("项目描述", "新项目")
    placeholders["OWNER_NAME"] = ask_question("负责人", "User")

    print("\n角色定义:")
    print("  1. 需求分析师 + 项目管理者 + 测试经理")
    print("  2. 开发者 + 架构师")
    print("  3. 自定义")

    role_choice = ask_question("选择角色", "1")
    if role_choice == "1":
        placeholders["USER_ROLE"] = "需求分析师 + 项目管理者 + 测试经理"
    elif role_choice == "2":
        placeholders["USER_ROLE"] = "开发者 + 架构师"
    else:
        placeholders["USER_ROLE"] = ask_question("输入自定义角色")

    print("\n分支策略:")
    placeholders["MAIN_BRANCH"] = ask_question("主分支名称", "main")
    placeholders["FEATURE_BRANCH"] = ask_question("功能分支名称", "develop")
    placeholders["USER_PREFIX"] = ask_question("用户分支前缀", "user/")
    placeholders["MERGE_FLOW"] = ask_question("合并流程", "功能分支 → develop → main")

    print("\nP0 任务（可选）:")
    has_p0 = ask_question("是否有 P0 优先任务", "n").lower() == "y"
    if has_p0:
        placeholders["P0_TASK_NAME"] = ask_question("P0 任务名称")
        placeholders["P0_TASK_GOAL"] = ask_question("P0 任务目标")

    return placeholders


def create_config_file(project_root: Path, placeholders: dict):
    """创建配置文件"""
    print_step(3, "创建配置文件...")

    template_path = Path(__file__).parent.parent / "templates" / "PROJECT_CONFIG.yaml.template"
    output_path = project_root / ".pm" / "CONFIG" / "PROJECT_CONFIG.yaml"

    if template_path.exists():
        content = template_path.read_text(encoding="utf-8")
        filled_content = fill_template(content, placeholders)
        output_path.write_text(filled_content, encoding="utf-8")
        print(f"  ✓ 创建: .pm/CONFIG/PROJECT_CONFIG.yaml")
    else:
        print(f"  ⚠ 模板文件不存在: {template_path}")


def create_status_files(project_root: Path, placeholders: dict):
    """创建状态文件"""
    print_step(4, "创建状态文件...")

    status_files = [
        ("STATUS_current.md.template", ".pm/STATUS/current.md"),
        ("STATUS_tasks.md.template", ".pm/STATUS/tasks.md"),
        ("STATUS_decisions.md.template", ".pm/STATUS/decisions.md"),
        ("STATUS_branches.md.template", ".pm/STATUS/branches.md"),
    ]

    template_dir = Path(__file__).parent.parent / "templates"

    for template_name, output_name in status_files:
        template_path = template_dir / template_name
        output_path = project_root / output_name

        if template_path.exists():
            content = template_path.read_text(encoding="utf-8")
            filled_content = fill_template(content, placeholders)
            output_path.write_text(filled_content, encoding="utf-8")
            print(f"  ✓ 创建: {output_name}")


def create_main_files(project_root: Path, placeholders: dict):
    """创建主要文件"""
    print_step(5, "创建主要文件...")

    template_dir = Path(__file__).parent.parent / "templates"

    # CLAUDE.md（根目录）
    claude_template = template_dir / "CLAUDE.md.template"
    if claude_template.exists():
        content = claude_template.read_text(encoding="utf-8")
        filled_content = fill_template(content, placeholders)
        (project_root / "CLAUDE.md").write_text(filled_content, encoding="utf-8")
        print("  ✓ 创建: CLAUDE.md")

    # ROADMAP.md
    roadmap_template = template_dir / "ROADMAP.md.template"
    if roadmap_template.exists():
        content = roadmap_template.read_text(encoding="utf-8")
        filled_content = fill_template(content, placeholders)
        (project_root / ".pm" / "ROADMAP.md").write_text(filled_content, encoding="utf-8")
        print("  ✓ 创建: .pm/ROADMAP.md")

    # LOG.md
    log_template = template_dir / "LOG.md.template"
    if log_template.exists():
        content = log_template.read_text(encoding="utf-8")
        filled_content = fill_template(content, placeholders)
        (project_root / ".pm" / "LOG.md").write_text(filled_content, encoding="utf-8")
        print("  ✓ 创建: .pm/LOG.md")


def copy_workflow_files(project_root: Path):
    """复制工作流文件"""
    print_step(6, "创建工作流文件...")

    # 创建基础指令手册
    workflow_content = """# 指令手册

## 继续

读取 .pm/STATUS/tasks.md，找到第一个待办任务并执行。

## 状态

读取 .pm/STATUS/current.md，显示当前阶段和阻塞问题。

## 计划

读取 .pm/STATUS/tasks.md，列出所有待办任务。

## 同步

使用 .pm/scripts/feishu_sync.py 同步飞书文档。

## 发布

使用 .pm/scripts/md2pdf.py 将 Markdown 转换为 PDF。
"""

    (project_root / ".pm" / "工作流" / "指令手册.md").write_text(workflow_content, encoding="utf-8")
    print("  ✓ 创建: .pm/工作流/指令手册.md")


def copy_scripts(project_root: Path):
    """复制脚本文件"""
    print_step(7, "复制脚本文件...")

    # 复制 feishu_sync.py
    feishu_src = Path(__file__).parent / "feishu_sync.py"
    if feishu_src.exists():
        shutil.copy2(feishu_src, project_root / ".pm" / "scripts" / "feishu_sync.py")
        print("  ✓ 复制: feishu_sync.py")

    # 复制 md2pdf.py
    md2pdf_src = Path(__file__).parent / "md2pdf.py"
    if md2pdf_src.exists():
        shutil.copy2(md2pdf_src, project_root / ".pm" / "scripts" / "md2pdf.py")
        print("  ✓ 复制: md2pdf.py")


def guide_roadmap(project_root: Path, placeholders: dict):
    """引导用户制定 Roadmap"""
    print_step(8, "引导制定 Roadmap...")

    print("\n" + "=" * 50)
    print(" 📋 让我们帮你制定项目 Roadmap")
    print("=" * 50)
    print("\n一个好的 Roadmap 应该包含：")
    print("  1. 项目的主要阶段")
    print("  2. 每个阶段的目标和里程碑")
    print("  3. 预估时间")
    print("\n你可以直接描述，我会帮你整理成规范的格式。")
    print("输入 'skip' 跳过，稍后手动创建。")

    # 询问是否要制定 Roadmap
    choice = input("\n是否现在制定 Roadmap? (y/n) [y]: ").strip().lower()
    if choice == 'n' or choice == 'skip':
        # 创建默认空模板
        create_default_roadmap(project_root, placeholders)
        return

    print("\n请告诉我关于项目的信息（按 Enter 跳过）：")

    # 收集项目信息
    project_type = ask_question("项目类型", "软件开发").strip()
    project_scale = ask_question("项目规模", "小型").strip()

    # 根据规模推荐阶段
    if project_scale == "小型":
        default_stages = "需求分析, 开发, 测试, 发布"
    elif project_scale == "中型":
        default_stages = "需求分析, 设计, 开发, 测试, 发布"
    else:
        default_stages = "需求分析, 设计, 开发, 测试, 部署, 维护"

    stages_input = ask_question("主要阶段（用逗号分隔）", default_stages).strip()
    stages = [s.strip() for s in stages_input.split(',') if s.strip()]

    # 目标日期
    deadline = ask_question("预期完成日期", "").strip()

    # 生成 Roadmap
    roadmap_content = generate_roadmap_content(placeholders, project_type, project_scale, stages, deadline)

    roadmap_path = project_root / ".pm" / "ROADMAP.md"
    roadmap_path.write_text(roadmap_content, encoding="utf-8")
    print(f"\n  ✓ 创建: .pm/ROADMAP.md")

    print("\n💡 提示：你可以在 .pm/ROADMAP.md 中随时修改 Roadmap。")


def create_default_roadmap(project_root: Path, placeholders: dict):
    """创建默认空 Roadmap"""
    roadmap_content = f"""# 项目路线图

> 最后更新：{placeholders['TODAY']}

## 项目概述

**项目名称**：{placeholders['PROJECT_NAME']}
**项目描述**：{placeholders['PROJECT_DESCRIPTION']}
**负责人**：{placeholders['OWNER_NAME']}

---

## 阶段规划

### 第一阶段：需求分析（Week 1）

**目标**：
- [ ] 收集和整理需求
- [ ] 明确项目范围
- [ ] 输出需求文档

**里程碑**：M1 - 需求分析完成

### 第二阶段：设计阶段（Week 2-3）

**目标**：
- [ ] 完成技术方案设计
- [ ] 完成 UI/UX 设计
- [ ] 输出设计文档

**里程碑**：M2 - 设计完成

### 第三阶段：开发阶段（Week 4-8）

**目标**：
- [ ] 核心功能开发
- [ ] 代码审查
- [ ] 单元测试

**里程碑**：M3 - 开发完成

### 第四阶段：测试验证（Week 9-10）

**目标**：
- [ ] 集成测试
- [ ] 用户验收测试
- [ ] Bug 修复

**里程碑**：M4 - 测试完成

### 第五阶段：发布上线（Week 11-12）

**目标**：
- [ ] 部署准备
- [ ] 正式发布
- [ ] 项目总结

**里程碑**：M5 - 项目完成

---

## 里程碑总览

| 节点 | 目标 | 状态 | 预期完成 |
|------|------|------|----------|
| M1 | 需求分析 | ⏳ | Week 1 |
| M2 | 设计完成 | ⏳ | Week 3 |
| M3 | 开发完成 | ⏳ | Week 8 |
| M4 | 测试完成 | ⏳ | Week 10 |
| M5 | 项目完成 | ⏳ | Week 12 |

---

## 备注

可以根据项目实际情况调整阶段划分和时间安排。
"""

    roadmap_path = project_root / ".pm" / "ROADMAP.md"
    roadmap_path.write_text(roadmap_content, encoding="utf-8")
    print(f"  ✓ 创建: .pm/ROADMAP.md（默认模板）")


def generate_roadmap_content(placeholders: dict, project_type: str, project_scale: str, stages: list, deadline: str) -> str:
    """生成 Roadmap 内容"""
    today = placeholders['TODAY']

    # 计算每个阶段的周数
    weeks_per_stage = 2 if project_scale == "小型" else (3 if project_scale == "中型" else 4)

    content = f"""# 项目路线图

> 最后更新：{today}
> 项目类型：{project_type}
> 项目规模：{project_scale}

## 项目概述

**项目名称**：{placeholders['PROJECT_NAME']}
**项目描述**：{placeholders['PROJECT_DESCRIPTION']}
**负责人**：{placeholders['OWNER_NAME']}
**预期完成**：{deadline if deadline else "待定"}

---

## 阶段规划
"""

    # 生成各阶段
    for i, stage in enumerate(stages, 1):
        week_start = (i - 1) * weeks_per_stage + 1
        week_end = i * weeks_per_stage
        content += f"""

### 第{i}阶段：{stage}（Week {week_start}-{week_end}）

**目标**：
- [ ] 待添加具体任务

**里程碑**：M{i} - {stage}完成

**交付物**：
- 待添加

**注意事项**：
- 待添加
"""

    # 生成里程碑表
    content += "\n---\n\n## 里程碑总览\n\n"
    content += "| 节点 | 目标 | 状态 | 预期完成 |\n"
    content += "|------|------|------|----------|\n"

    for i, stage in enumerate(stages, 1):
        week_start = (i - 1) * weeks_per_stage + 1
        week_end = i * weeks_per_stage
        content += f"| M{i} | {stage}完成 | ⏳ | Week {week_end} |\n"

    if deadline:
        content += f"| 最终 | 项目完成 | ⏳ | {deadline} |\n"

    content += "\n---\n\n## 备注\n\n"
    content += "💡 提示：这是根据你提供的信息自动生成的 Roadmap。\n"
    content += "可以根据实际情况调整任务、时间线和里程碑。\n"

    return content


def create_readme(project_root: Path, placeholders: dict):
    """创建 README"""
    print_step(9, "创建 README...")

    readme_content = f"""# {placeholders['PROJECT_NAME']}

{placeholders['PROJECT_DESCRIPTION']}

---

## 项目管理

本项目使用 **项目管理框架 v2.0**，配置位于 `.pm/` 目录。

### 快速开始

- 查看状态：输入 `状态`
- 查看任务：输入 `计划`
- 继续任务：输入 `继续`
- 查看帮助：输入 `帮助`

### 核心文档

- `CLAUDE.md` - 项目配置和指令系统
- `.pm/CONFIG/PROJECT_CONFIG.yaml` - 项目元数据
- `.pm/STATUS/` - 状态管理
- `.pm/ROADMAP.md` - 路线图

### 目录结构

```
.
├── CLAUDE.md          # 项目主文档（根目录）
└── .pm/               # 项目管理目录
    ├── CONFIG/        # 配置文件
    ├── STATUS/        # 状态管理
    ├── 工作流/        # 工作流定义
    ├── 需求/          # 需求文档
    ├── 方案/          # 方案文档
    ├── 输出/          # 输出报告
    ├── scripts/       # 工具脚本
    └── LOGS/          # 日志目录
```

---

负责人：{placeholders['OWNER_NAME']}
创建时间：{placeholders['TODAY']}
"""

    (project_root / "README.md").write_text(readme_content, encoding="utf-8")
    print("  ✓ 创建: README.md")


def print_summary(placeholders: dict):
    """打印初始化摘要"""
    print_step(9, "初始化完成！")
    print("\n📋 项目配置摘要:")
    print(f"  项目名称: {placeholders['PROJECT_NAME']}")
    print(f"  负责人: {placeholders['OWNER_NAME']}")
    print(f"  主分支: {placeholders['MAIN_BRANCH']}")
    print(f"  功能分支: {placeholders['FEATURE_BRANCH']}")

    print("\n📁 目录结构:")
    print("  CLAUDE.md           # 核心配置（根目录）")
    print("  .pm/                # 项目管理目录")
    print("  ├── CONFIG/         # 配置文件")
    print("  ├── STATUS/         # 状态管理")
    print("  ├── 工作流/         # 工作流定义")
    print("  ├── 需求/           # 需求文档")
    print("  ├── 方案/           # 方案文档")
    print("  ├── 输出/           # 输出报告")
    print("  ├── scripts/        # 工具脚本")
    print("  └── LOGS/           # 日志目录")

    print("\n📚 快速开始:")
    print("  1. 查看当前状态：输入 `状态`")
    print("  2. 查看待办任务：输入 `计划`")
    print("  3. 开始第一个任务：输入 `继续`")

    print("\n💡 提示:")
    print("  - 所有指令都需要在 Claude Code 对话中使用")
    print("  - 配置文件位于 .pm/CONFIG/PROJECT_CONFIG.yaml")
    print("  - 状态文件位于 .pm/STATUS/ 目录")
    print("  - 工具脚本位于 .pm/scripts/ 目录")

    print("\n" + "=" * 50)


def main():
    """主函数"""
    print_header("项目管理框架 v2.0 初始化")

    # 获取项目根目录
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])
    else:
        project_root = Path.cwd()

    print(f"\n📁 项目根目录: {project_root}")

    # 确认初始化
    confirm = ask_question("\n是否在此目录初始化项目", "y")
    if confirm.lower() != "y":
        print("已取消")
        return

    # 收集用户信息
    placeholders = collect_user_info()

    # 创建目录结构
    create_directory_structure(project_root)

    # 创建文件
    create_config_file(project_root, placeholders)
    create_status_files(project_root, placeholders)
    create_main_files(project_root, placeholders)

    # 复制文件（如果存在）
    copy_workflow_files(project_root)
    copy_scripts(project_root)

    # 引导制定 Roadmap
    guide_roadmap(project_root, placeholders)

    # 创建 README
    create_readme(project_root, placeholders)

    # 打印摘要
    print_summary(placeholders)


if __name__ == "__main__":
    main()
