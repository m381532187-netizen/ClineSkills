#!/usr/bin/env python3
"""
step2_find_calls.py

Reads ProcessTask.cpp from stdin (via: cmd /c "type file.cpp | python this.py").
Scans for all calls to functions listed in gb_functions.json using a
character-level state machine with bracket counting.

Usage:
    cmd /c "type "TASK_FILE" | python "step2_find_calls.py" "gb_functions.json" "call_sites.json""
"""
import sys
import json
import re

IDENT_START = frozenset('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_')
IDENT_CHARS = frozenset('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_')


def split_args(arg_str):
    """
    Split argument string (the text between the outer parens of a call) into
    individual arguments. Uses a state machine to respect nesting, strings,
    char literals, and comments.
    """
    args = []
    current = []
    depth = 0
    in_string = False
    in_char = False
    in_lc = False   # line comment
    in_bc = False   # block comment
    i = 0
    s = arg_str

    while i < len(s):
        c = s[i]
        if in_lc:
            if c == '\n':
                in_lc = False
            current.append(c)
            i += 1
            continue
        if in_bc:
            if c == '*' and i + 1 < len(s) and s[i + 1] == '/':
                current.append('*/')
                in_bc = False
                i += 2
                continue
            current.append(c)
            i += 1
            continue
        if in_string:
            if c == '\\' and i + 1 < len(s):
                current.append(c)
                current.append(s[i + 1])
                i += 2
                continue
            if c == '"':
                in_string = False
            current.append(c)
            i += 1
            continue
        if in_char:
            if c == '\\' and i + 1 < len(s):
                current.append(c)
                current.append(s[i + 1])
                i += 2
                continue
            if c == "'":
                in_char = False
            current.append(c)
            i += 1
            continue
        # Normal context
        if c == '/' and i + 1 < len(s):
            if s[i + 1] == '/':
                in_lc = True
                current.append(c)
                i += 1
                continue
            if s[i + 1] == '*':
                in_bc = True
                current.append('/*')
                i += 2
                continue
        if c == '"':
            in_string = True
            current.append(c)
            i += 1
            continue
        if c == "'":
            in_char = True
            current.append(c)
            i += 1
            continue
        if c in '([{':
            depth += 1
        elif c in ')]}':
            depth -= 1
        elif c == ',' and depth == 0:
            args.append(''.join(current).strip())
            current = []
            i += 1
            continue
        current.append(c)
        i += 1

    last = ''.join(current).strip()
    if last:
        args.append(last)
    return args


def find_calls(source, name_set):
    """
    Single-pass character-level scanner over `source`.
    Returns list of call dicts: {line, col, func_name, full_call, args}
    line and col are 1-based.
    """
    results = []
    n = len(source)

    # Build line-start offset table for line/col calculation
    line_starts = [0]
    for idx in range(n):
        if source[idx] == '\n':
            line_starts.append(idx + 1)

    def offset_to_line_col(offset):
        lo, hi = 0, len(line_starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if line_starts[mid] <= offset:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1, offset - line_starts[lo] + 1  # 1-based

    # Scanner state
    in_lc = False
    in_bc = False
    in_str = False
    in_chr = False
    i = 0

    while i < n:
        c = source[i]

        if in_lc:
            if c == '\n':
                in_lc = False
            i += 1
            continue

        if in_bc:
            if c == '*' and i + 1 < n and source[i + 1] == '/':
                in_bc = False
                i += 2
            else:
                i += 1
            continue

        if in_str:
            if c == '\\':
                i += 2
            elif c == '"':
                in_str = False
                i += 1
            else:
                i += 1
            continue

        if in_chr:
            if c == '\\':
                i += 2
            elif c == "'":
                in_chr = False
                i += 1
            else:
                i += 1
            continue

        # Normal context: detect comment/string/char starts
        if c == '/' and i + 1 < n:
            if source[i + 1] == '/':
                in_lc = True
                i += 2
                continue
            if source[i + 1] == '*':
                in_bc = True
                i += 2
                continue

        if c == '"':
            in_str = True
            i += 1
            continue

        if c == "'":
            in_chr = True
            i += 1
            continue

        # Identifier detection
        if c in IDENT_START:
            j = i
            while j < n and source[j] in IDENT_CHARS:
                j += 1
            ident = source[i:j]

            # Skip optional whitespace to find '('
            k = j
            while k < n and source[k] in ' \t':
                k += 1

            if k < n and source[k] == '(' and ident in name_set:
                # Found a call. Extract full argument list by paren counting.
                call_start = i
                paren_start = k
                depth = 0
                m = paren_start
                p_in_str = False
                p_in_chr = False
                p_in_lc = False
                p_in_bc = False

                while m < n:
                    pc = source[m]
                    if p_in_lc:
                        if pc == '\n':
                            p_in_lc = False
                        m += 1
                        continue
                    if p_in_bc:
                        if pc == '*' and m + 1 < n and source[m + 1] == '/':
                            p_in_bc = False
                            m += 2
                        else:
                            m += 1
                        continue
                    if p_in_str:
                        if pc == '\\':
                            m += 2
                        elif pc == '"':
                            p_in_str = False
                            m += 1
                        else:
                            m += 1
                        continue
                    if p_in_chr:
                        if pc == '\\':
                            m += 2
                        elif pc == "'":
                            p_in_chr = False
                            m += 1
                        else:
                            m += 1
                        continue
                    if pc == '/' and m + 1 < n:
                        if source[m + 1] == '/':
                            p_in_lc = True
                            m += 2
                            continue
                        if source[m + 1] == '*':
                            p_in_bc = True
                            m += 2
                            continue
                    if pc == '"':
                        p_in_str = True
                        m += 1
                        continue
                    if pc == "'":
                        p_in_chr = True
                        m += 1
                        continue
                    if pc == '(':
                        depth += 1
                    elif pc == ')':
                        depth -= 1
                        if depth == 0:
                            m += 1
                            break
                    m += 1

                call_end = m
                full_call = source[call_start:call_end]
                arg_str = source[paren_start + 1:call_end - 1]
                args = split_args(arg_str) if arg_str.strip() else []

                line_num, col_num = offset_to_line_col(call_start)
                results.append({
                    'line': line_num,
                    'col': col_num,
                    'func_name': ident,
                    'full_call': full_call,
                    'args': args,
                })
                i = call_end
                continue
            else:
                i = j
                continue

        i += 1

    results.sort(key=lambda x: (x['line'], x['col']))
    return results


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: type file.cpp | python step2_find_calls.py "
            "<gb_functions.json> <call_sites.json>",
            file=sys.stderr
        )
        sys.exit(1)

    gb_json_file = sys.argv[1]
    out_file = sys.argv[2]

    with open(gb_json_file, 'r', encoding='utf-8') as f:
        gb_functions = json.load(f)

    func_names = list(gb_functions.keys())
    name_set = set(func_names)
    print(f"[step2] Searching for {len(func_names)} GB functions...", file=sys.stderr)

    raw_bytes = sys.stdin.buffer.read()
    try:
        source = raw_bytes.decode('utf-8', errors='replace')
    except Exception:
        source = raw_bytes.decode('gbk', errors='replace')

    # Normalize line endings before scanning (offsets computed on normalized text)
    source = source.replace('\r\n', '\n').replace('\r', '\n')

    call_sites = find_calls(source, name_set)

    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(call_sites, f, ensure_ascii=False, indent=2)

    print(f"[step2] Found {len(call_sites)} call sites -> {out_file}", file=sys.stderr)


if __name__ == '__main__':
    main()
