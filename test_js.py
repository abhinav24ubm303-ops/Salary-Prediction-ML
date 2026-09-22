"""
test_js.py - Validates basic bracket matching and syntax balance of static/js/app.js
"""
def check():
    with open('static/js/app.js', 'r', encoding='utf-8') as f:
        code = f.read()

    stack = []
    pairs = {')': '(', '}': '{', ']': '['}
    lines = code.splitlines()

    for line_no, line in enumerate(lines, 1):
        in_str = False
        str_q = ''
        i = 0
        while i < len(line):
            c = line[i]
            if in_str:
                if c == '\\':
                    i += 2
                    continue
                if c == str_q:
                    in_str = False
            else:
                if c in ('"', "'", '`'):
                    in_str = True
                    str_q = c
                elif c == '/' and i + 1 < len(line) and line[i+1] == '/':
                    break
                elif c in ('(', '{', '['):
                    stack.append((c, line_no))
                elif c in (')', '}', ']'):
                    if not stack:
                        print(f"Error: unmatched {c} at line {line_no}")
                        return False
                    top, t_line = stack.pop()
                    if top != pairs[c]:
                        print(f"Mismatch: {top} (line {t_line}) closed by {c} (line {line_no})")
                        return False
            i += 1

    if stack:
        print(f"Unclosed: {stack[-3:]}")
        return False
    print("app.js syntax balance verification: PASS!")
    return True

if __name__ == '__main__':
    assert check()
