# 🦁 ClineSkills

> 精选高质量 Cline Skills、Rules 和 Workflows，让 AI 编程助手真正成为你的开发搭档。

**ClineSkills** 汇集了 GitHub 上最优质的 Cline（VSCode AI 编程 Agent）扩展规则和工作流，开源免费，持续更新。

---

## ⭐ 快速上手

### 方式一：复制到项目（最简单）

```bash
# 克隆仓库
git clone https://github.com/m381532187-netizen/ClineSkills.git

# 复制官方规则到你的项目
cp -r ClineSkills/.clinerules /你的项目路径/

# 或复制全部内容到用户目录（全局生效）
cp -r ClineSkills/ ~
```

### 方式二：VSCode 插件安装（图形化管理）

1. 在 VSCode 插件市场搜索 **"Cline Rules"**
2. 安装 henryalps 开发的插件
3. 右键 → **"Add Project Rule from Bank"** → 选择预设规则

### 方式三：按需引用单个文件

不需要复制全部文件，直接在 Cline 中引用特定规则文件即可：
```
@/path/to/ClineSkills/.clinerules/baby-steps.md
```

---

## 📁 仓库结构

```
ClineSkills/
├── .clinerules/                    # ⭐ 官方规则（34个文件）
│   ├── baby-steps.md               #   小步增量开发
│   ├── memory-bank.md              #   持久化项目记忆
│   ├── self-improving-cline.md     #   自我反思改进协议
│   ├── security-audit.md           #   安全审计工作流
│   ├── code-review.md              #   代码审查规则
│   ├── testing-strategy.md         #   测试策略指导
│   ├── mermaid-plans.md           #   Mermaid 流程图生成
│   └── ...（共34个）
│
├── cline-official-workflows/        # ⭐ 官方工作流（7个文件）
│   ├── self-improving-cline.md
│   ├── pr-review-cline.md
│   ├── setup-ci-cd-pipeline.md
│   └── ...
│
└── third-party/                   # 社区精选
    ├── rules-template/             #   Agile开发+Memory Bank（⭐1063）
    ├── vscode-clinerules/          #   VSCode插件+19类预设（⭐40）
    ├── cline-prompts-tips-tricks/  #   提示词合集（⭐33）
    ├── oci-ai-architect-skills/    #   企业级跨平台技能库
    ├── thinking-partner/            #   150+思维模型（⭐113）
    └── nexus-skills/              #   代码库知识图谱（⭐139）
```

---

## 🏆 核心内容详解

### 官方规则 (.clinerules)

来自 [cline/prompts](https://github.com/cline/prompts)（⭐1.1k），Cline 官方维护，质量最高。

| 文件 | 用途 |
|------|------|
| `baby-steps.md` | 把大任务拆成小步骤，每步可验证 |
| `memory-bank.md` | 跨会话持久化项目上下文 |
| `self-improving-cline.md` | 错误反思→改进输出质量 |
| `security-audit.md` | 系统性代码安全审计流程 |
| `code-review.md` | 结构化代码审查规则 |
| `testing-strategy.md` | 定义和执行测试策略 |
| `mermaid-plans.md` | 用 Mermaid 语法生成流程图 |
| `cline-continuous-improvement-protocol.md` | 从错误中学习的协议 |
| `general-development-rules.md` | 通用开发规范 |

### 官方工作流 (Workflows)

自动化复杂任务的标准流程模板：

| 文件 | 用途 |
|------|------|
| `pr-review-cline.md` | Pull Request 审查流程 |
| `setup-ci-cd-pipeline.md` | CI/CD 流水线配置 |
| `self-improving-cline.md` | 自我改进循环 |
| `create-new-workflow.md` | 如何创建新工作流 |

### third-party / rules-template（⭐1063）

**强烈推荐**——Agile 开发方法论 + Memory Bank 持久化记忆系统。

```
rules-template/
├── .clinerules/           # Cline 规则（符号链接指向 .cursor/rules/）
│   ├── rules.mdc          #   核心规则
│   ├── plan.mdc           #   计划工作流
│   ├── implement.mdc      #   实施工作流
│   └── debug.mdc          #   调试工作流
├── docs/                  # 项目文档
│   ├── architecture.md    #   系统架构文档
│   ├── technical.md       #   技术规格说明
│   └── product_requirement_docs.md  # PRD
├── tasks/                 # 任务管理
│   ├── tasks_plan.md      #   任务待办列表
│   └── active_context.md  #   当前开发上下文
└── memory.mdc             # 记忆文件规范
```

**特点**：
- 跨平台兼容（Cline + Cursor + RooCode + Windsurf）
- 三档规则（Basic / Standard / Strict）按需选用
- 符号链接机制，一处编辑多端同步
- 专为 Agile 团队设计

### third-party / thinking-partner（⭐113）

150+ 思维模型，让 AI 不仅执行，还能**挑战你的假设**。

```
thinking-partner/
└── skills/thinking-partner/
    ├── SKILL.md           # 技能定义
    └── references/
        ├── model-catalog.md     # 150+思维模型目录
        └── thinking-diagnostics.md  # 思维诊断
```

**使用场景**：
- "帮我分析这个方案的风险"
- "我遗漏了什么？"
- "用第一性原理重新审视这个问题"
- SWOT / 5 Whys / Pre-mortem / Inversion 等

### third-party / nexus-skills（⭐139）

代码库感知技能，为 AI 生成**持久化知识图谱**。

```
nexus-skills/
└── skills/
    ├── nexus-mapper/      # 生成代码库结构图
    └── nexus-query/       # 查询依赖关系和改动影响半径
```

**使用场景**：
- 快速理解新项目结构
- 查询某个改动会影响哪些文件
- 生成代码库的依赖图

### third-party / vscode-clinerules（⭐40）

VSCode 插件形式的规则预设库，图形化安装。

```
vscode-clinerules/rules/
├── web-react/           # React 开发规则
├── web-vue/             # Vue.js 开发规则
├── web-nextjs/          # Next.js 开发规则
├── backend-django/       # Django 后端规则
├── backend-express/      # Express.js 后端规则
├── backend-springboot/   # Spring Boot 后端规则
├── backend-rails/        # Rails 后端规则
├── app-ios/             # iOS 开发规则
├── app-android/         # Android 开发规则
├── local-python/        # Python 开发规则
├── general/             # 通用规则
└── ...（共19个分类）
```

---

## 🛠️ 使用指南

### 按场景选择规则

| 场景 | 推荐规则 |
|------|---------|
| 通用编程 | `.clinerules/general-development-rules.md` |
| 代码审查 | `.clinerules/code-review.md` + `pr-review-cline.md` |
| 安全敏感项目 | `.clinerules/security-audit.md` |
| 测试驱动开发 | `.clinerules/testing-strategy.md` |
| 复杂多步骤任务 | `rules-template/`（Agile 工作流）|
| 流程图/架构图 | `.clinerules/mermaid-plans.md` |
| 新项目接手 | `.clinerules/codebase-onboarding.md` |

### 让 Cline 加载特定规则

在 Cline 对话框中引用：
```
@/path/to/ClineSkills/.clinerules/baby-steps.md
```

或在项目根目录创建 `.clinerules` 目录并放入需要的文件。

---

## 🔗 相关资源

| 资源 | 地址 | 说明 |
|------|------|------|
| Cline 官方仓库 | [github.com/cline/cline](https://github.com/cline/cline) | ⭐59k，VSCode AI Agent 主体 |
| Cline 官方规则 | [github.com/cline/prompts](https://github.com/cline/prompts) | ⭐1.1k，官方规则和工作流 |
| Awesome Cursor Rules | [github.com/PatrickJS/awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) | ⭐38k，大部分规则兼容 Cline |
| ClawHub (OpenClaw Skills) | [clawhub.com](https://clawhub.com) | OpenClaw 的 Skills 市场 |

---

## 📝 贡献

欢迎提交 Pull Request！贡献前请阅读：

- 规则文件使用 Markdown 格式
- 优先提交官方 cline/prompts 的更新
- 社区规则需注明来源和 Stars 数量
- 新增规则请同步更新本 README

---

## 📄 许可证

MIT License——可自由使用、修改和分发。

---

*🦁 Maintained by Lion — Kevin's AI Coding Assistant*
