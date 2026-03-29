#!/usr/bin/env python3
"""
step1_extract_bodies.py

Reads ProcessTaskForGB.cpp from stdin (via: cmd /c "type file.cpp | python this.py").
Reads function metadata from ctags NDJSON output.
Produces gb_functions.json with function body lines and parameter names.

Usage:
    cmd /c "type "GB_FILE" | python "step1_extract_bodies.py" "ctags_output.json" "gb_functions.json""
"""
import sys
import json
import re


CPP_KEYWORDS = {
    'const', 'volatile', 'unsigned', 'signed', 'short', 'long',
    'int', 'char', 'float', 'double', 'bool', 'void', 'struct',
    'class', 'enum', 'typename', 'template', 'inline', 'static',
    'extern', 'register', 'auto', 'mutable', 'explicit', 'virtual',
    'BOOL', 'BYTE', 'WORD', 'DWORD', 'LPCTSTR', 'LPTSTR', 'LPVOID',
    'HANDLE', 'HWND', 'HRESULT', 'TRUE', 'FALSE', 'NULL',
}


def parse_params(signature):
    """
    Extract parameter names from a C++ function signature string.
    signature: e.g. "(int count, const char* name, float& val)"
    Returns list of param name strings (one per parameter).
    """
    if not signature:
        return []
    sig = signature.strip()
    if sig.startswith('('):
        sig = sig[1:]
    if sig.endswith(')'):
        sig = sig[:-1]
    sig = sig.strip()
    if not sig or sig.lower() == 'void':
        return []

    # Split on commas at depth 0 (skip template params like std::map<int,int>)
    parts = []
    depth = 0
    current = []
    for ch in sig:
        if ch in '(<':
            depth += 1
            current.append(ch)
        elif ch in ')>':
            depth -= 1
            current.append(ch)
        elif ch == ',' and depth == 0:
            parts.append(''.join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        parts.append(''.join(current).strip())

    names = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Strip default value
        if '=' in part:
            part = part[:part.index('=')].strip()
        # Strip array brackets
        part = re.sub(r'\[.*?\]', '', part).strip()
        # Strip ellipsis
        part = part.replace('...', '').strip()
        # Get all word tokens
        tokens = re.findall(r'[A-Za-z_]\w*', part)
        # The parameter name is the last non-keyword token
        name_tokens = [t for t in tokens if t not in CPP_KEYWORDS]
        if name_tokens:
            names.append(name_tokens[-1])
        else:
            names.append('')
    return names


def extract_body_by_brace_count(lines, start_idx):
    """
    Fallback: extract function body by brace counting from start_idx (0-based).
    Properly handles string literals, char literals, // and /* */ comments.
    Returns list of lines from signature line through closing brace (inclusive).
    """
    result = []
    depth = 0
    found_open = False
    in_block_comment = False
    in_string = False
    in_char = False

    for i in range(start_idx, len(lines)):
        line = lines[i]
        result.append(line)
        j = 0
        in_line_comment = False
        while j < len(line):
            c = line[j]
            if in_line_comment:
                break
            if in_block_comment:
                if c == '*' and j + 1 < len(line) and line[j + 1] == '/':
                    in_block_comment = False
                    j += 2
                    continue
                j += 1
                continue
            if in_string:
                if c == '\\':
                    j += 2
                    continue
                if c == '"':
                    in_string = False
                j += 1
                continue
            if in_char:
                if c == '\\':
                    j += 2
                    continue
                if c == "'":
                    in_char = False
                j += 1
                continue
            # Normal context
            if c == '/' and j + 1 < len(line):
                if line[j + 1] == '/':
                    in_line_comment = True
                    break
                if line[j + 1] == '*':
                    in_block_comment = True
                    j += 2
                    continue
            if c == '"':
                in_string = True
            elif c == "'":
                in_char = True
            elif c == '{':
                depth += 1
                found_open = True
            elif c == '}':
                depth -= 1
                if found_open and depth == 0:
                    return result
            j += 1

    return result


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: type file.cpp | python step1_extract_bodies.py "
            "<ctags_output.json> <gb_functions.json>",
            file=sys.stderr
        )
        sys.exit(1)

    ctags_file = sys.argv[1]
    out_file = sys.argv[2]

    # --- Load ctags NDJSON ---
    func_meta = {}  # bare_name -> metadata dict

    with open(ctags_file, 'r', encoding='utf-8', errors='replace') as f:
        for raw_line in f:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                obj = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            # Universal Ctags NDJSON has _type=="tag" for tag entries
            if obj.get('_type') == 'tag' and obj.get('kind') == 'function':
                full_name = obj.get('name', '')
                start_line = obj.get('line', 0)
                end_line = obj.get('end', 0)
                signature = obj.get('signature', '')
                bare_name = full_name.split('::')[-1]
                if bare_name in func_meta:
                    print(
                        f"WARNING: duplicate bare name '{bare_name}' "
                        f"('{full_name}' vs '{func_meta[bare_name]['full_name']}'). "
                        f"Overwriting.",
                        file=sys.stderr
                    )
                params = parse_params(signature)
                func_meta[bare_name] = {
                    'full_name': full_name,
                    'start_line': start_line,
                    'end_line': end_line,
                    'params': params,
                    'signature': signature,
                    'body_lines': [],
                }

    if not func_meta:
        print("WARNING: No functions found in ctags output.", file=sys.stderr)

    # --- Read source from stdin ---
    raw_bytes = sys.stdin.buffer.read()
    try:
        source = raw_bytes.decode('utf-8', errors='replace')
    except Exception:
        source = raw_bytes.decode('gbk', errors='replace')

    lines = source.splitlines()  # normalizes \r\n and \n

    # --- Collect body lines using ctags line ranges ---
    # ctags line numbers are 1-based; end==0 means ctags didn't provide it
    for bare_name, meta in func_meta.items():
        start = meta['start_line']
        end = meta['end_line']
        if end > 0:
            # Direct slice: lines[start-1 .. end-1] inclusive (0-based indexing)
            body_lines = lines[start - 1: end]
        else:
            # Fallback: brace counting from start line
            body_lines = extract_body_by_brace_count(lines, start - 1)
        meta['body_lines'] = body_lines

    # --- Write output ---
    output = {}
    for bare_name, meta in func_meta.items():
        output[bare_name] = {
            'full_name': meta['full_name'],
            'params': meta['params'],
            'signature': meta['signature'],
            'body_lines': meta['body_lines'],
            'source_start_line': meta['start_line'],
            'source_end_line': meta['end_line'],
        }

    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"[step1] Extracted {len(output)} functions -> {out_file}", file=sys.stderr)


if __name__ == '__main__':
    main()
