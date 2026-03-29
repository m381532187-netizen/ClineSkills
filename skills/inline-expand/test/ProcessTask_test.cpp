// ProcessTask_test.cpp - 测试用主文件（包含对 GB 函数的调用）

void CMyClass::Process()
{
    // 用例1：简单独立调用，实参为变量
    DoSimple(m_nCount, 10);

    // 用例2：调用在赋值语句右侧（非独立语句）
    int nVal = CalcValue(m_nCount, m_nTotal);

    // 用例3：实参含表达式（应自动加括号）
    DoSimple(m_nCount + 1, nVal * 2);

    // 用例4：无参调用
    NoParam();

    // 用例5：嵌套调用（CalcValue 的实参里有另一个函数调用）
    DoSimple(CalcValue(1, 2), 5);

    // 用例6：实参含字符串字面量
    ComplexArgs(m_nCount, "hello, world");
}
