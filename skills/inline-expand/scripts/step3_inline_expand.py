#!/usr/bin/env python3
"""
step3_inline_expand.py

Reads ProcessTask.cpp from stdin (via: cmd /c "type file.cpp | python this.py").
For every call site listed in call_sites.json, replaces the entire source line
with the inlined function body (parameter names substituted with actual arguments,
re-indented to match the call site).

Output goes to stdout; redirect to ProcessTask_inlined.cpp.

Usage:
    cmd /c "type "TASK_FILE" | python "step3_inline_expand.py" "gb_functions.json" "call_sites.json" > "ProcessTask_inlined.cpp""
"""
import sys
import json
import re


def is_simple_expr(s):
    """
    Return True if `s` is safe to substitute directly without extra parentheses.
    Conservative: only simple identifiers, member-access chains, pointer deref,
    array subscript, and plain literals qualify.
    Anything containing operators (+, -, *, /, etc.) at the top level gets wrapped.
    """
    s = s.strip()
    if re.fullmatch(r'[A-Za-z_]\w*', s):
        return True
    if re.fullmatch(r'[A-Za-z_][\w.\->\[\]]*', s):
        return True
    if re.fullmatch(r'[&*]+[A-Za-z_]\w*', s):
        return True
    # Integer / float / string / char literals
    if re.fullmatch(r'[-+]?\d[\d.uUlLfF]*', s):
        return True
    if re.fullmatch(r'"[^"]*"', s):
        return True
    if re.fullmatch(r"'[^']*'", s):
        return True
    return False


def make_replacement(arg):
    """Wrap arg in parens if it contains operators, to preserve precedence."""
    a = arg.strip()
    if not a:
        return a
    if is_simple_expr(a):
        return a
    return f'({a})'


def get_body_interior(body_lines):
    """
    Given the raw body_lines from gb_functions.json (which includes the
    function signature line(s) and the outer { }), return only the interior
    lines between the opening brace and the closing brace.
    """
    open_idx = None
    for i, line in enumerate(body_lines):
        stripped = re.sub(r'//.*', '', line)
        stripped = re.sub(r'/\*.*?\*/', '', stripped)
        if '{' in stripped:
            open_idx = i
            break

    if open_idx is None:
        return body_lines

    interior = body_lines[open_idx + 1:]

    # Remove trailing closing-brace line(s) and blank lines after last real content
    while interior and interior[-1].strip() in ('}', '};', ''):
        interior = interior[:-1]

    return interior


def compute_original_indent(interior_lines):
    """
    Detect the common leading whitespace of the function body interior.
    Returns the indent string of the first non-blank line.
    """
    for line in interior_lines:
        if line.strip():
            m = re.match(r'^(\s*)', line)
            return m.group(1) if m else ''
    return ''


def substitute_params(line, params, args):
    """
    Replace each formal parameter name in `line` with the corresponding
    actual argument, using word-boundary matching to avoid partial replacements.
    """
    for i, param in enumerate(params):
        if not param:
            continue
        if i < len(args):
            replacement = make_replacement(args[i])
        else:
            replacement = ''
        line = re.sub(r'\b' + re.escape(param) + r'\b', replacement, line)
    return line


def reindent_line(line, orig_indent, call_indent):
    """
    Re-indent a body line by replacing the function's original indentation
    with the call site's indentation.
    """
    if not line.strip():
        return ''
    if orig_indent and line.startswith(orig_indent):
        return call_indent + line[len(orig_indent):]
    return call_indent + line.lstrip()


def build_inline_lines(func_name, func_info, args, call_indent):
    """
    Build the list of output lines that replace a single call site.
    Returns a list of strings (no trailing newline).
    """
    params = func_info.get('params', [])
    body_lines = func_info.get('body_lines', [])

    interior = get_body_interior(body_lines)
    if not interior:
        return []

    orig_indent = compute_original_indent(interior)

    result = []
    for line in interior:
        line = substitute_params(line, params, args)
        line = reindent_line(line, orig_indent, call_indent)
        result.append(line)

    return result


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: type file.cpp | python step3_inline_expand.py "
            "<gb_functions.json> <call_sites.json> > ProcessTask_inlined.cpp",
            file=sys.stderr
        )
        sys.exit(1)

    gb_json_file = sys.argv[1]
    call_sites_file = sys.argv[2]

    with open(gb_json_file, 'r', encoding='utf-8') as f:
        gb_functions = json.load(f)

    with open(call_sites_file, 'r', encoding='utf-8') as f:
        call_sites = json.load(f)

    # Index call sites by source line number (1-based)
    calls_by_line = {}
    for cs in call_sites:
        ln = cs['line']
        calls_by_line.setdefault(ln, []).append(cs)
    for ln in calls_by_line:
        calls_by_line[ln].sort(key=lambda x: x['col'])

    # Read source from stdin
    raw_bytes = sys.stdin.buffer.read()
    try:
        source = raw_bytes.decode('utf-8', errors='replace')
    except Exception:
        source = raw_bytes.decode('gbk', errors='replace')

    source_lines = source.splitlines()

    output_lines = []
    inlined_count = 0

    for line_idx, line in enumerate(source_lines):
        line_num = line_idx + 1  # 1-based

        if line_num not in calls_by_line:
            output_lines.append(line)
            continue

        m = re.match(r'^(\s*)', line)
        call_indent = m.group(1) if m else ''

        site_list = calls_by_line[line_num]
        for cs in site_list:
            fname = cs['func_name']
            args = cs.get('args', [])
            if fname not in gb_functions:
                output_lines.append(line)
                break
            func_info = gb_functions[fname]
            expanded = build_inline_lines(fname, func_info, args, call_indent)
            output_lines.extend(expanded)
            inlined_count += 1

    print(
        f"[step3] Inlined {inlined_count} call sites. "
        f"Output: {len(output_lines)} lines.",
        file=sys.stderr
    )

    # Write to stdout using Windows line endings
    result = '\r\n'.join(output_lines)
    if result and not result.endswith('\r\n'):
        result += '\r\n'
    sys.stdout.buffer.write(result.encode('utf-8'))


if __name__ == '__main__':
    main()
