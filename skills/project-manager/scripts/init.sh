#!/bin/bash
# 项目管理框架 v2.0 初始化脚本（Shell 版本）
# 用于 Unix/Linux/macOS 系统

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印标题
print_header() {
    echo ""
    echo "=================================================="
    echo "  项目管理框架 v2.0 初始化"
    echo "=================================================="
    echo ""
}

# 打印步骤
print_step() {
    echo ""
    echo "[$1] $2"
}

# 获取输入（带默认值）
ask() {
    local prompt="$1"
    local default="$2"
    local result

    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " result
        echo "${result:-$default}"
    else
        read -p "$prompt: " result
        echo "$result"
    fi
}

# 创建目录
create_directories() {
    print_step 1 "创建目录结构..."

    mkdir -p .pm/CONFIG
    mkdir -p .pm/STATUS
    mkdir -p .pm/工作流
    mkdir -p .pm/需求/待分析
    mkdir -p .pm/需求/待消化
    mkdir -p .pm/需求/已消化
    mkdir -p .pm/需求/分析报告
    mkdir -p .pm/方案
    mkdir -p .pm/输出/日报
    mkdir -p .pm/输出/摘要
    mkdir -p .pm/输出/归档
    mkdir -p .pm/scripts
    mkdir -p .pm/LOGS

    echo -e "${GREEN}✓${NC} 目录结构创建完成"
}

# 主函数
main() {
    print_header

    # 检查是否在正确的目录
    if [ -f "CLAUDE.md" ] || [ -f ".pm/CONFIG/PROJECT_CONFIG.yaml" ]; then
        echo -e "${YELLOW}警告: 此目录可能已初始化${NC}"
        read -p "是否继续? (y/n): " confirm
        if [ "$confirm" != "y" ]; then
            echo "已取消"
            exit 0
        fi
    fi

    # 收集信息
    print_step 2 "收集项目信息..."

    PROJECT_NAME=$(ask "项目名称" "$(basename "$(pwd)")")
    PROJECT_DESC=$(ask "项目描述" "新项目")
    OWNER_NAME=$(ask "负责人" "User")

    echo ""
    echo "角色定义:"
    echo "  1. 需求分析师 + 项目管理者 + 测试经理"
    echo "  2. 开发者 + 架构师"
    echo "  3. 自定义"
    ROLE_CHOICE=$(ask "选择角色" "1")

    case "$ROLE_CHOICE" in
        1) USER_ROLE="需求分析师 + 项目管理者 + 测试经理" ;;
        2) USER_ROLE="开发者 + 架构师" ;;
        *) USER_ROLE=$(ask "输入自定义角色") ;;
    esac

    echo ""
    MAIN_BRANCH=$(ask "主分支名称" "main")
    FEATURE_BRANCH=$(ask "功能分支名称" "develop")
    USER_PREFIX=$(ask "用户分支前缀" "user/")
    MERGE_FLOW=$(ask "合并流程" "功能分支 → develop → main")

    # 今天的日期
    TODAY=$(date +%Y-%m-%d)

    # 创建目录
    create_directories

    # 创建配置文件
    print_step 3 "创建配置文件..."

    cat > .pm/CONFIG/PROJECT_CONFIG.yaml << EOF
# 项目配置文件
project:
  name: "$PROJECT_NAME"
  description: "$PROJECT_DESC"
  owner: "$OWNER_NAME"
  created: "$TODAY"

roles:
  user: "$USER_ROLE"
  user_behavior: "主动理解意图，引导式、选择式交互"
  assistant: "AI Agent，负责需求分析、测试规划、状态跟踪"

branches:
  main: "$MAIN_BRANCH"
  feature: "$FEATURE_BRANCH"
  user_prefix: "$USER_PREFIX"
  merge_flow: "$MERGE_FLOW"

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
EOF

    echo -e "${GREEN}✓${NC} 创建: .pm/CONFIG/PROJECT_CONFIG.yaml"

    # 创建状态文件
    print_step 4 "创建状态文件..."

    cat > .pm/STATUS/current.md << EOF
# 当前状态

> 最后更新：$TODAY

## 当前阶段

需求收集 → 计划制定 → **测试验证** → 结果分析

## 阶段进度

- ⏳ 阶段 0：准备
- ⏳ 阶段 1：MVP
- ⏳ 阶段 2：深化集成

## 阻塞问题

无

## 下一步

- [ ] 初始化任务
EOF

    cat > .pm/STATUS/tasks.md << EOF
# 任务列表

> 最后更新：$TODAY

## 待办任务

### 阶段 0：准备

- [ ] **任务 1**
  - 描述：待添加
  - 负责人：
  - 依赖：

---

## 进行中任务

无

---

## 已完成

- [x] 项目初始化
EOF

    cat > .pm/STATUS/decisions.md << EOF
# 决策记录

| 日期 | 决策内容 | 原因 | 影响 |
|------|----------|------|------|
| $TODAY | 项目初始化 | 使用项目管理框架 v2.0 | 建立项目结构 |
EOF

    cat > .pm/STATUS/branches.md << EOF
# 分支管理策略

## 分支架构

| 分支 | 用途 | 负责人 | 状态 |
|------|------|--------|------|
| \`$MAIN_BRANCH\` | 主分支 | - | - |

## 合并流程

\`\`\`
$MERGE_FLOW
\`\`\`
EOF

    echo -e "${GREEN}✓${NC} 创建: .pm/STATUS/ 目录文件"

    # 创建主文件
    print_step 5 "创建主文件..."

    cat > CLAUDE.md << EOF
# CLAUDE.md

> 本项目使用 **项目管理框架 v2.0**，配置位于 \`.pm/CONFIG/PROJECT_CONFIG.yaml\`

## 核心文档

### \`.pm/CONFIG/PROJECT_CONFIG.yaml\`
- 项目元数据配置

### \`.pm/STATUS/\` 目录
- \`current.md\` - 当前状态
- \`tasks.md\` - 任务列表
- \`decisions.md\` - 决策记录
- \`branches.md\` - 分支策略

### \`.pm/ROADMAP.md\`
- 项目路线图

## 指令系统

| 指令 | 用途 |
|------|------|
| \`继续\` | 执行下一个待办任务 |
| \`状态\` | 查看当前项目状态 |
| \`计划\` | 查看待办任务列表 |

---

项目：$PROJECT_NAME
负责人：$OWNER_NAME
EOF

    cat > .pm/ROADMAP.md << EOF
# 项目路线图

## 第一阶段：方案设计（Week 1-4）

### Week 1
- [x] 项目初始化
- [ ] 需求分析

### Week 2-4
- [ ] 技术方案设计

## 里程碑

| 节点 | 目标 | 状态 |
|------|------|------|
| M1 | 需求分析 | ✅ |
| M2 | MVP | 🔄 |
EOF

    cat > .pm/LOG.md << EOF
# 操作日志

## $TODAY

- [项目初始化] 创建项目目录结构
- [配置] 初始化项目管理框架 v2.0
EOF

    echo -e "${GREEN}✓${NC} 创建: CLAUDE.md, .pm/ROADMAP.md, .pm/LOG.md"

    # 创建工作流文件
    print_step 6 "创建工作流文件..."

    cat > .pm/工作流/指令手册.md << 'EOF'
# 指令手册

## 继续

读取 .pm/STATUS/tasks.md，找到第一个待办任务并执行。

## 状态

读取 .pm/STATUS/current.md，显示当前阶段和阻塞问题。

## 计划

读取 .pm/STATUS/tasks.md，列出所有待办任务。
EOF

    echo -e "${GREEN}✓${NC} 创建: .pm/工作流/指令手册.md"

    # 复制脚本文件
    print_step 7 "复制脚本文件..."

    SCRIPT_DIR="$(dirname "$0")"
    if [ -f "$SCRIPT_DIR/feishu_sync.py" ]; then
        cp "$SCRIPT_DIR/feishu_sync.py" .pm/scripts/
        echo -e "${GREEN}✓${NC} 复制: feishu_sync.py"
    fi

    if [ -f "$SCRIPT_DIR/md2pdf.py" ]; then
        cp "$SCRIPT_DIR/md2pdf.py" .pm/scripts/
        echo -e "${GREEN}✓${NC} 复制: md2pdf.py"
    fi

    # 引导制定 Roadmap
    print_step 8 "引导制定 Roadmap..."

    echo ""
    echo "=================================================="
    echo " 📋 让我们帮你制定项目 Roadmap"
    echo "=================================================="
    echo ""
    echo "你可以输入项目信息，我会帮你生成 Roadmap。"
    echo "输入 'skip' 跳过，使用默认模板。"

    guide_choice=$(ask "是否现在制定 Roadmap? (y/n)" "y")

    if [ "$guide_choice" != "n" ]; then
        # 收集项目信息
        PROJECT_TYPE=$(ask "项目类型" "软件开发")
        PROJECT_SCALE=$(ask "项目规模 [小型/中型/大型]" "小型")

        # 根据规模设置阶段和周数
        if [ "$PROJECT_SCALE" = "小型" ]; then
            WEEKS_PER_STAGE=1
            DEFAULT_STAGES="需求分析,开发,测试,发布"
        elif [ "$PROJECT_SCALE" = "中型" ]; then
            WEEKS_PER_STAGE=2
            DEFAULT_STAGES="需求分析,设计,开发,测试,发布"
        else
            WEEKS_PER_STAGE=3
            DEFAULT_STAGES="需求分析,设计,开发,测试,部署,维护"
        fi

        STAGES_INPUT=$(ask "主要阶段（用逗号分隔）" "$DEFAULT_STAGES")
        DEADLINE=$(ask "预期完成日期（可选）" "")

        # 生成 Roadmap
        cat > .pm/ROADMAP.md << EOF
# 项目路线图

> 最后更新：$TODAY
> 项目类型：$PROJECT_TYPE
> 项目规模：$PROJECT_SCALE

## 项目概述

**项目名称**：$PROJECT_NAME
**项目描述**：$PROJECT_DESC
**负责人**：$OWNER_NAME
**预期完成**：${DEADLINE:-待定}

---

## 阶段规划
EOF

        # 生成各阶段
        STAGE_NUM=1
        IFS=','
        for STAGE in $STAGES_INPUT; do
            STAGE_NAME=$(echo "$STAGE" | xargs)
            WEEK_START=$(( ($STAGE_NUM - 1) * $WEEKS_PER_STAGE + 1 ))
            WEEK_END=$(( $STAGE_NUM * $WEEKS_PER_STAGE ))

            cat >> .pm/ROADMAP.md << STAGEEOF

### 第${STAGE_NUM}阶段：${STAGE_NAME}（Week ${WEEK_START}-${WEEK_END}）

**目标**：
- [ ] 待添加具体任务

**里程碑**：M${STAGE_NUM} - ${STAGE_NAME}完成

**交付物**：
- 待添加
STAGEEOF
            STAGE_NUM=$((STAGE_NUM + 1))
        done
        unset IFS

        # 生成里程碑表
        cat >> .pm/ROADMAP.md << EOF

---

## 里程碑总览

| 节点 | 目标 | 状态 | 预期完成 |
|------|------|------|----------|
EOF

        STAGE_NUM=1
        IFS=','
        for STAGE in $STAGES_INPUT; do
            STAGE_NAME=$(echo "$STAGE" | xargs)
            WEEK_END=$(( $STAGE_NUM * $WEEKS_PER_STAGE ))
            echo "| M${STAGE_NUM} | ${STAGE_NAME}完成 | ⏳ | Week ${WEEK_END} |" >> .pm/ROADMAP.md
            STAGE_NUM=$((STAGE_NUM + 1))
        done
        unset IFS

        if [ -n "$DEADLINE" ]; then
            echo "| 最终 | 项目完成 | ⏳ | ${DEADLINE} |" >> .pm/ROADMAP.md
        fi

        cat >> .pm/ROADMAP.md << EOF

---

## 备注

💡 提示：这是根据你提供的信息自动生成的 Roadmap。
可以根据实际情况调整任务、时间线和里程碑。
EOF

        echo -e "${GREEN}✓${NC} 创建: .pm/ROADMAP.md（已根据你的信息生成）"
    else
        # 创建默认 Roadmap
        cat > .pm/ROADMAP.md << EOF
# 项目路线图

> 最后更新：$TODAY

## 项目概述

**项目名称**：$PROJECT_NAME
**项目描述**：$PROJECT_DESC
**负责人**：$OWNER_NAME

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
EOF
        echo -e "${GREEN}✓${NC} 创建: .pm/ROADMAP.md（默认模板）"
    fi

    # 创建 README
    print_step 9 "创建 README..."

    cat > README.md << EOF
# $PROJECT_NAME

$PROJECT_DESC

---

## 项目管理

本项目使用 **项目管理框架 v2.0**，配置位于 \`.pm/\` 目录。

### 快速开始

- 查看状态：输入 \`状态\`
- 查看任务：输入 \`计划\`
- 继续任务：输入 \`继续\`

### 核心文档

- \`CLAUDE.md\` - 项目配置和指令系统
- \`.pm/CONFIG/PROJECT_CONFIG.yaml\` - 项目元数据
- \`.pm/STATUS/\` - 状态管理
- \`.pm/ROADMAP.md\` - 路线图

---

负责人：$OWNER_NAME
创建时间：$TODAY
EOF

    echo -e "${GREEN}✓${NC} 创建: README.md"

    # 完成
    echo ""
    echo "=================================================="
    echo -e "${GREEN}  初始化完成！${NC}"
    echo "=================================================="
    echo ""
    echo "📋 项目配置摘要:"
    echo "  项目名称: $PROJECT_NAME"
    echo "  负责人: $OWNER_NAME"
    echo "  主分支: $MAIN_BRANCH"
    echo ""
    echo "📁 目录结构:"
    echo "  CLAUDE.md           # 核心配置（根目录）"
    echo "  .pm/                # 项目管理目录"
    echo "  ├── CONFIG/         # 配置文件"
    echo "  ├── STATUS/         # 状态管理"
    echo "  ├── 工作流/         # 工作流定义"
    echo "  ├── 需求/           # 需求文档"
    echo "  ├── 方案/           # 方案文档"
    echo "  ├── 输出/           # 输出报告"
    echo "  ├── scripts/        # 工具脚本"
    echo "  └── LOGS/           # 日志目录"
    echo ""
    echo "📚 快速开始:"
    echo "  1. 查看当前状态：输入 \`状态\`"
    echo "  2. 查看待办任务：输入 \`计划\`"
    echo "  3. 开始第一个任务：输入 \`继续\`"
    echo ""
}

# 运行主函数
main
