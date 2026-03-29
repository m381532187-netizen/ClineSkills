# inline-expand：C++ 源码级内联展开工具

## 项目背景与需求

### 用户需求

用户在一个使用企业加密软件（亿赛通 DLP）的 Windows 开发环境中，手动将 `ProcessTask.cpp` 中的大量代码块重构提取为独立函数，存入新文件 `ProcessTaskForGB.cpp`。重构完成后，需要验证提取是否完整、无遗漏——即将 `ProcessTaskForGB.cpp` 中所有函数"内联还原"回 `ProcessTask.cpp` 的调用处，生成 `ProcessTask_inlined.cpp`，与原始 `ProcessTask.cpp` 进行 Diff 比对。

### 核心目标

- **输入**：`ProcessTaskForGB.cpp`（函数实现）+ `ProcessTask.cpp`（调用方）
- **输出**：`ProcessTask_inlined.cpp`（所有 GB 函数调用被替换为对应函数体）
- **用途**：代码 Diff 比对，不要求内联后可编译

### 内联格式要求

- 无注释包裹、无花括号边界标记
- 函数体直接平铺替换调用行（含缩进重对齐）
- 对实参做文本级参数替换：形参名 → 实参表达式
  - 简单标识符直接替换
  - 含运算符的实参自动加括号，防止优先级问题
- 非独立语句调用（如 `if(Foo(x))`）也强制整行替换

---

## 关键环境约束

| 约束 | 影响 | 解决方案 |
|------|------|---------|
| 亿赛通企业加密 | Python `open()` 读取 .cpp 文件得到乱码 | 通过 Windows `type` 命令管道传给 Python stdin |
| ctags.exe 在白名单中 | ctags 可直接读取加密文件 | 用 ctags 提取函数元数据（行号、签名） |
| 文件体积超大（1M+ tokens） | 不能直接 read_file 读取 | 流式管道处理，分步产出中间 JSON |
| C++03 语法 + 嵌套调用 | 简单正则无法正确解析 | 字符级状态机 + 括号栈算法 |
| 无 Node.js 环境 | npx 类工具不可用 | 使用 Python 脚本 + ctags 预编译二进制 |

---

## 系统架构

### 五阶段管道

```
[ctags.exe 直接读加密文件]
    ↓ ctags_output.json（函数名、起始行、结束行、签名）
[type GBFILE | python step1]
    ↓ gb_functions.json（函数体逐行文本 + 参数名列表）
[type TASKFILE | python step2]
    ↓ call_sites.json（调用位置、函数名、实参列表）
[type TASKFILE | python step3]
    ↓ ProcessTask_inlined.cpp（最终输出）
```

---

## 各脚本详细设计

### step1_extract_bodies.py

**职责**：从 `type` 管道读取 ProcessTaskForGB.cpp 明文，利用 ctags 给出的行号范围直接切片提取函数体。

**关键设计**：
- `sys.stdin.buffer.read()` 读取 stdin（管道明文），decode UTF-8（fallback GBK）
- 用 ctags 的 `line`/`end` 字段做 `lines[start-1:end]` 直接切片，无需自行解析 C++ 括号
- 若 ctags 缺少 `end` 字段，fallback 到括号栈计数（正确处理字符串/注释内的括号）
- 参数名提取：从 ctags `signature` 字段按深度 0 处逗号分割，取每个参数最后一个非关键字 `\w+` token

**输出格式（gb_functions.json）**：
```json
{
  "FuncName": {
    "full_name": "CMyClass::FuncName",
    "params": ["param1", "param2"],
    "signature": "(int param1, MyClass* param2)",
    "body_lines": ["void CMyClass::FuncName(...)", "{", "    ...", "}"],
    "source_start_line": 42,
    "source_end_line": 87
  }
}
```
键为裸函数名（去 `ClassName::` 前缀），便于调用点匹配。

### step2_find_calls.py

**职责**：全文字符级扫描 ProcessTask.cpp，找出所有对 GB 函数的调用。

**核心算法（字符级状态机 + 括号栈）**：
1. 追踪上下文：`in_line_comment` / `in_block_comment` / `in_string` / `in_char`
2. 在正常上下文中，识别 `identifier(` 模式
3. identifier 在 GB 函数集合中 → 启动括号栈提取实参
4. 实参分割：`split_args()` 同样使用状态机，仅在 depth==0 时按 `,` 分割

**输出格式（call_sites.json）**：
```json
[
  {
    "line": 123,
    "col": 8,
    "func_name": "FuncName",
    "full_call": "FuncName(arg1, obj->method())",
    "args": ["arg1", "obj->method()"]
  }
]
```

### step3_inline_expand.py

**职责**：将 ProcessTask.cpp 中每个调用行替换为对应函数体（参数替换 + 重缩进）。

**参数替换示例**：
```
函数定义：void DoSimple(int nVal, int nOffset)
调用：DoSimple(m_nCount + 1, nVal * 2)

替换前：int nResult = nVal + nOffset;
替换后：int nResult = (m_nCount + 1) + (nVal * 2);
```

---

## Edge Cases 处理

| 情况 | 处理方式 |
|------|---------|
| ctags 无 `end` 字段 | fallback 括号栈从 start_line 扫描到结束 `}` |
| 同一裸名函数重复（不同类） | stderr 警告，后者覆盖前者 |
| 形参无名称（`int`） | parse_params 返回空串，替换跳过 |
| 实参数量 ≠ 形参数量 | 多余实参忽略，缺少实参用空串 |
| GBK 编码文件 | 将 `decode('utf-8')` 改为 `decode('gbk')` |
| Windows CRLF | `splitlines()` 规范化，输出显式 `\r\n` |
| 同行多个 GB 函数调用 | 按列序依次平铺展开，均替换到该行位置 |

---

## 测试验证结果

| 用例 | 说明 | 结果 |
|------|------|------|
| 简单变量实参 | `DoSimple(m_nCount, 10)` | ✅ 直接替换 |
| 赋值右侧调用 | `int nVal = CalcValue(...)` | ✅ 整行替换 |
| 表达式实参 | `DoSimple(m_nCount + 1, nVal * 2)` | ✅ 自动加括号 |
| 无参函数 | `NoParam()` | ✅ 正常展开 |
| 嵌套调用实参 | `DoSimple(CalcValue(1, 2), 5)` | ✅ 完整提取嵌套调用 |
| 含逗号字符串 | `ComplexArgs(m_nCount, "hello, world")` | ✅ 字符串未被逗号分割 |
