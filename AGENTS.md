# Guideline for agents

## Must Follow Rules
- Avoid over-engineering, prefer simple and robust approach
- Ensure no cascading issue arises after implementation
- Keep cross-platform compatibility in consideration
- Use only ASCII characters in Python source code and CLI output; avoid Unicode symbols (e.g., arrows, checkmarks, em-dashes) that may fail on Windows terminals with non-UTF-8 encoding. Use ASCII equivalents instead (`->`, `[OK]`, `[FAIL]`, `-`)