// ProcessTaskForGB_test.cpp - 测试用 GB 函数文件

class CMyClass
{
public:
    void DoSimple(int nVal, int nOffset)
    {
        int nResult = nVal + nOffset;
        m_nTotal += nResult;
        if (nResult > 100)
            m_nOverflow++;
    }

    int CalcValue(int nA, int nB)
    {
        int nSum = nA + nB;
        int nProduct = nA * nB;
        return nSum + nProduct;
    }

    void NoParam()
    {
        m_nCount = 0;
        m_nTotal = 0;
    }

    void ComplexArgs(int nX, const char* pszName)
    {
        m_nCount += nX;
        OutputDebugString(pszName);
    }

    int m_nTotal;
    int m_nCount;
    int m_nOverflow;
};
