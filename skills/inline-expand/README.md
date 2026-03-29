# inline-expand-skill

一个 Claude Code / Cline skill，用于将大型 C++ 文件中的函数实现内联展开到另一个 C++ 文件的调用点。

## 背景与约束

- 目标文件均为大型 C++ 文件（不能整体读取）
- 文件受亿赛通加密保护，只有白名单应用可读取内容
  - **白名单**：VSCode、Cline（Claude Code）、ctags.exe
  - **非白名单**：Python 及其他脚本解释器
- 因此，所有文件访问必须通过 AI Read 工具或 ctags.exe

## 核心技术方案

```
ctags.exe  →  符号表（函数名 + 精确行号范围）
                ↓
[type file.cpp | python step1/2/3]  →  管道绕过加密限制
                ↓
ProcessTask_inlined.cpp  →  供 Diff 比对验证
```

## 文件结构

```
skills/inline-expand/
  README.md                    ← 本文件
  SKILL.md                     ← Cline skill 激活入口（Python 管道方案）
  design.md                    ← 详细设计文档
  commands/
    inline-expand.md           ← Slash command 版本（AI Read 工具方案）
  scripts/
    step1_extract_bodies.py    ← 提取 GB 函数体和参数名
    step2_find_calls.py        ← 扫描调用点
    step3_inline_expand.py     ← 生成内联展开文件
  test/
    ProcessTaskForGB_test.cpp  ← 测试用 GB 函数文件
    ProcessTask_test.cpp       ← 测试用调用方文件
    run_test.bat               ← 端到端测试脚本
```

## 使用方法

将 `SKILL.md` 放入项目的 `.clinerules/` 目录，Cline 遇到"内联展开"等关键词时自动激活。

也可使用 slash command 版本，在 Claude Code 中输入：

```
/inline-expand <SOURCE_FILE> <TARGET_FILE> [函数名...]
```

## ctags 安装

需要 [Universal Ctags](https://github.com/universal-ctags/ctags-win32/releases)，确保 `ctags.exe` 在工作区 `tools/` 目录下或系统 PATH 中。
