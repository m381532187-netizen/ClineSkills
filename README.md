# 🦁 ClineSkills

> Curated high-quality Cline skills, rules, and workflows for AI-assisted coding.

This repository aggregates the best open-source Cline (VSCode AI coding agent) skills and rules, organized for easy discovery and installation.

---

## 📁 Repository Structure

```
ClineSkills/
├── .clinerules/                    # ⭐ Official Cline rules (34 files)
│   ├── baby-steps.md               #   Small-step incremental development
│   ├── memory-bank.md              #   Persistent project memory system
│   ├── self-improving-cline.md     #   Self-reflection and improvement protocol
│   ├── security-audit.md           #   Security audit workflow
│   ├── code-review.md              #   Code review rules
│   ├── testing-strategy.md         #   Testing strategy guidance
│   ├── workflow-rules.md           #   General workflow rules
│   ├── general-development-rules.md
│   ├── codebase-onboarding.md      #   New code context onboarding
│   ├── create-documentation.md
│   ├── mcp-development-protocol.md
│   ├── cline-continuous-improvement-protocol.md
│   └── ... (34 files total)
│
├── cline-official-workflows/       # ⭐ Official Cline workflows (7 files)
│   ├── self-improving-cline.md
│   ├── pr-review-cline.md
│   ├── create-new-workflow.md
│   ├── ai-dlc-construction.md
│   ├── ai-dlc-inception.md
│   ├── setup-ci-cd-pipeline.md
│   └── ci-cd-with-cline-cli.md
│
└── third-party/                    # Community-contributed skills
    ├── rules-template/             #   ⭐ 1063 stars - Agile dev + Memory Bank
    ├── vscode-clinerules/          #   ⭐ 40 stars - VSCode plugin + Rule Bank
    ├── cline-prompts-tips-tricks/  #   ⭐ 33 stars - Prompts & workflows
    └── oci-ai-architect-skills/   #   Enterprise-grade cross-platform skills
```

---

## 🚀 Quick Start

### Option 1: Use Official Rules Only (Recommended for Beginners)

```bash
# Copy official rules to your project
cp -r .clinerules/ /path/to/your-project/
```

### Option 2: Use with VSCode Plugin (Easiest)

Install the **"Cline Rules"** VSCode plugin from the Marketplace:
- Search: "Cline Rules" by henryalps
- Right-click → "Add Project Rule from Bank" → choose from 19 preset categories

### Option 3: Clone and Reference

```bash
# Add as a submodule or reference directly in your .clinerules/
git clone https://github.com/m381532187-netizen/ClineSkills.git
```

---

## 🏆 Featured Skills

### 🥇 Official `.clinerules` (from `cline/prompts`)

These are the official rules maintained by the Cline team. High quality, battle-tested.

| File | Purpose |
|------|---------|
| `baby-steps.md` | Break large tasks into small, verifiable increments |
| `memory-bank.md` | Maintain persistent project context across sessions |
| `self-improving-cline.md` | Self-reflection loop to improve outputs over time |
| `security-audit.md` | Systematic security review workflow |
| `code-review.md` | Structured code review process |
| `testing-strategy.md` | Define and execute testing strategy |
| `cline-continuous-improvement-protocol.md` | Learning from mistakes |

### 🥈 `rules-template` — Agile + Memory Bank (⭐1063)

Cross-platform (Cline + Cursor + RooCode + Windsurf), built on Agile methodology.

**Structure:**
- `.clinerules/rules` — Core rules (always loaded)
- `.clinerules/plan` — Planning workflow
- `.clinerules/implement` — Implementation workflow
- `.clinerules/debug` — Debug workflow
- Memory files: `docs/`, `tasks/`, `tasks/rfc/`

### 🥉 `thinking-partner` (⭐113, in third-party)

150+ mental models to challenge assumptions and sharpen decisions. Works with any AI coding assistant.

---

## 📦 Installation Per Skill

### Official Rules
```bash
# Per-project
cp -r .clinerules/ your-project/

# Or global (~/ means your home directory)
cp -r .clinerules/ ~
# Then reference in Cline settings
```

### VSCode Plugin (Cline Rules)
1. Search "Cline Rules" in VSCode Marketplace
2. Install the plugin by henryalps
3. Right-click in Explorer → "Add Project Rule from Bank"
4. Choose: React / Vue / Django / Spring Boot / Express / iOS / Android / ...

### Rules Template
```bash
git clone https://github.com/Bhartendu-Kumar/rules_template.git
cp -r rules_template/.clinerules/ your-project/
cp -r rules_template/.cursor/ your-project/  # Optional: Cursor rules too
```

---

## 🔗 Related Resources

- [Official Cline Repository](https://github.com/cline/cline) — ⭐59k
- [Official Cline Prompts](https://github.com/cline/prompts) — ⭐1.1k (source of .clinerules/)
- [Awesome Cursor Rules](https://github.com/PatrickJS/awesome-cursorrules) — ⭐38k (most rules also work with Cline)

---

## 📊 Skill Comparison

| Skill Set | Stars | Tokens/Use | Best For |
|-----------|-------|------------|----------|
| Official `.clinerules` | ⭐1.1k | Low | All-purpose coding |
| Rules Template (Agile) | ⭐1k | Medium | Structured team dev |
| Cline Rules Plugin | ⭐40 | Low | Framework-specific (React, Django, etc.) |
| Thinking Partner | ⭐113 | Medium | Decision-making |

---

*Maintained by Lion 🦁 — contributions welcome!*
