# Inline Expand C++ Implementations

将 SOURCE_FILE 中的函数实现，内联展开到 TARGET_FILE 的调用点。

## 用法
```
/inline-expand <SOURCE_FILE> <TARGET_FILE> [函数名1 函数名2 ...]
```
- 若不指定函数名，则自动分析 TARGET_FILE 中所有来自 SOURCE_FILE 的调用并展开。

---

## 执行步骤

### 第一步：用 ctags 提取符号表

> 注意：直接用脚本读取文件内容会因加密失败，必须通过 ctags.exe（白名单）+ Read 工具（AI 直接读取）来处理大文件。

运行以下命令，获取 SOURCE_FILE 的所有函数符号及行号范围：

```bash
ctags.exe -f - --sort=no --fields=+ne --c++-kinds=+p --output-format=u-ctags "$SOURCE_FILE"
```

解析输出，建立映射表：`函数名 → {文件, 起始行, 结束行}`

### 第二步：确定要内联的函数列表

- 若用户指定了函数名，使用该列表。
- 否则，用 Grep 在 TARGET_FILE 中搜索 SOURCE 符号表中的函数名（按批次搜索，避免一次读取整个文件）。

### 第三步：逐函数读取实现体

对每个要内联的函数，利用 ctags 给出的 `line`（起始行）和 `end:` 字段（结束行）：

```
Read(SOURCE_FILE, offset=start_line-1, limit=end_line-start_line+1)
```

这样只读取该函数的片段，不受大文件限制。

### 第四步：在 TARGET_FILE 中定位调用点

```bash
grep -n "函数名\s*(" "$TARGET_FILE"
```

对每个调用点，用 Read 工具读取上下文（调用点前后各 ~20 行）以理解参数列表和缩进风格。

### 第五步：构造内联展开代码

```cpp
// 原调用：result = FuncName(arg1, arg2);
// 内联展开：
{
    // inlined: FuncName
    auto param1 = arg1;
    auto param2 = arg2;
    // ... 函数体 ...
    result = <return_expr>;
}
```

处理规则：
1. **参数替换**：将形参替换为实参（简单情况直接文本替换，复杂情况用临时变量）
2. **return 语句**：转换为对返回值变量的赋值，或直接替换调用表达式
3. **多处调用**：每处独立展开，变量名加序号避免冲突
4. **递归/复杂控制流**：如遇递归或复杂 goto，提示用户该函数不适合内联并跳过

### 第六步：写入 TARGET_FILE

使用 Edit 工具，将每个调用点替换为内联展开后的代码块。

---

## 注意事项

- **分批处理**：如果要内联的函数数量多，每次处理 3~5 个，中途汇报进度
- **保守策略**：遇到不确定的情况（模板函数、虚函数、含宏的函数体），跳过并提示用户
- **只读 SOURCE**：不修改 SOURCE_FILE，所有改动只在 TARGET_FILE
- **加密文件限制**：严禁调用 Python/脚本读取文件内容，所有文件读取必须通过 AI Read 工具或 ctags.exe 白名单工具

---

## 示例

```
/inline-expand src/math_utils.cpp src/renderer.cpp computeMatrix transformVertex
```

AI 将：
1. 用 ctags 定位函数在 math_utils.cpp 中的行范围
2. 逐个读取其实现
3. 在 renderer.cpp 中找到所有调用点
4. 将调用替换为内联展开的代码块
