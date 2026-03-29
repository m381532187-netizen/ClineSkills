---
name: inline-expand
description: Inline-expands all C++ functions from ProcessTaskForGB.cpp into their call sites in ProcessTask.cpp, producing ProcessTask_inlined.cpp for diff comparison. Designed for encrypted Windows environments where Python cannot open files directly (uses ctags + type-pipe pattern).
---

# inline-expand

将 `ProcessTaskForGB.cpp` 中所有函数实现内联展开到 `ProcessTask.cpp` 的对应调用处，生成 `ProcessTask_inlined.cpp`，供 Diff 比对验证手动重构的正确性。

## 适用场景

当用户提到以下任意情形时激活此 skill：
- "内联展开"、"inline expand"
- 将 ProcessTaskForGB 的函数内联回 ProcessTask
- 验证手动提取接口是否正确

## 环境约束（极重要）

1. **加密文件**：C++ 源文件在磁盘上被企业加密（亿赛通），Python 进程无法直接 `open()` 读取。
   - 解决方案：通过 Windows `type` 命令管道传给 Python：`cmd /c "type file.cpp | python script.py"`
2. **ctags.exe** 是白名单应用，可直接读取加密文件。
3. **禁止用 `read_file` 直接读取**原始 `.cpp` 文件（文件体积巨大，会撑爆上下文）。
4. 中间产物 JSON 文件（非加密）可以用 `read_file` 读取用于调试。

## 路径变量约定

在开始前，确定以下路径（全部使用绝对路径，末尾无斜杠）：

| 变量 | 说明 | 示例 |
|------|------|------|
| `WORKSPACE_ROOT` | 工作区根目录 | `D:\MyProject` |
| `GBFILE` | ProcessTaskForGB.cpp 完整路径 | `D:\MyProject\src\ProcessTaskForGB.cpp` |
| `TASKFILE` | ProcessTask.cpp 完整路径 | `D:\MyProject\src\ProcessTask.cpp` |
| `SRCDIR` | 两文件所在目录 | `D:\MyProject\src` |
| `OUTFILE` | 输出文件 | `SRCDIR\ProcessTask_inlined.cpp` |
| `TMPDIR` | 临时目录 | `SRCDIR\.agents_tmp\inline-expand` |
| `CTAGS` | ctags 可执行路径 | `WORKSPACE_ROOT\tools\ctags.exe` |
| `SCRIPTS` | 脚本目录 | `WORKSPACE_ROOT\.agents\skills\inline-expand\scripts` |

**获取路径**：询问用户 `GBFILE` 和 `TASKFILE` 的完整路径，其余变量自行推导。

---

## 执行步骤

### Step 1：创建临时目录

```
cmd /c "mkdir "TMPDIR" 2>nul"
```

### Step 2：ctags 提取函数元数据

ctags 是白名单应用，直接读取加密文件，无需 type 管道。

```
"CTAGS" --output-format=json --fields=+neS --kinds-C++=f --language-force=C++ -f "TMPDIR\ctags_output.json" "GBFILE"
```

**验证**：确认 `TMPDIR\ctags_output.json` 存在且非空。

### Step 3：提取函数体 → gb_functions.json

通过 type 管道读取加密的 GBFILE：

```
cmd /c "type "GBFILE" | python "SCRIPTS\step1_extract_bodies.py" "TMPDIR\ctags_output.json" "TMPDIR\gb_functions.json""
```

脚本从 stdin 读取明文内容（type 命令负责解密），用 ctags 的 `line`/`end` 字段直接切片，提取函数体和参数名。

**验证**：可用 `read_file` 读取 `TMPDIR\gb_functions.json`（非加密），确认函数列表和参数名正确。

### Step 4：扫描调用点 → call_sites.json

通过 type 管道读取加密的 TASKFILE：

```
cmd /c "type "TASKFILE" | python "SCRIPTS\step2_find_calls.py" "TMPDIR\gb_functions.json" "TMPDIR\call_sites.json""
```

脚本使用字符级状态机 + 括号栈扫描，识别对 GB 函数的所有调用，提取实参列表。

**验证**：可用 `read_file` 读取 `TMPDIR\call_sites.json`，确认调用数量合理。

### Step 5：生成内联展开文件

```
cmd /c "type "TASKFILE" | python "SCRIPTS\step3_inline_expand.py" "TMPDIR\gb_functions.json" "TMPDIR\call_sites.json" > "OUTFILE""
```

脚本对每个调用行：
- 用实参替换形参（word-boundary 正则，含表达式的实参自动加括号）
- 去掉函数体外层 `{ }`，直接平铺函数体内容
- 重新缩进到调用处的缩进级别
- 整行替换（无论该调用是否为独立语句）

### Step 6：向用户报告结果

读取 stderr 输出，汇报：
- 从 ProcessTaskForGB.cpp 提取了多少个函数
- 在 ProcessTask.cpp 中找到多少个调用点
- 内联展开了多少处
- 输出文件路径：`OUTFILE`
- 任何警告（如同名函数冲突、实参/形参数量不匹配等）

---

## 内联格式说明

原始调用行（无论是否为独立语句）**整行被替换**为函数体内部内容：

```cpp
// ProcessTask.cpp 原始代码（调用处）
    DoProcess(m_pData, nCount);

// ProcessTask_inlined.cpp（展开后）
    int nResult = m_pData->Validate(nCount);
    if (nResult < 0)
        return FALSE;
    m_nProcessed += nResult;
```

- 无注释、无花括号包裹
- 形参名被实参文本替换
- 缩进与原调用处对齐

---

## 常见问题与处理

| 问题 | 处理 |
|------|------|
| 输出中文乱码 | 在三个脚本中将 `decode('utf-8', ...)` 改为 `decode('gbk', ...)` |
| ctags 未找到 end 字段 | 脚本自动 fallback 到括号栈计数提取函数体 |
| 同名函数（不同类） | stderr 输出警告，后者覆盖前者；检查 gb_functions.json |
| 调用行有多个 GB 函数调用 | 按列序依次展开所有函数体，均替换到该行位置 |
| ctags.exe 路径不对 | 确认 `WORKSPACE_ROOT\tools\ctags.exe` 存在；路径含空格时需引号 |

---

## 调试技巧

- **仅看特定函数**：在 `gb_functions.json` 中搜索函数名，确认 `params` 和 `body_lines` 正确
- **仅看特定调用**：在 `call_sites.json` 中搜索函数名，确认 `args` 解析正确
- **局部验证**：在 `ProcessTask_inlined.cpp` 中搜索函数名（应不再出现调用，已被替换）
