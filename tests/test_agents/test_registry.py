from minimythos.agents.registry import resolve_command


def test_resolve_named_opencode():
    cmd = resolve_command("opencode", "fix the bug")
    assert cmd == ["opencode", "run", "fix the bug"]


def test_resolve_named_claude():
    cmd = resolve_command("claude", "fix the bug")
    assert cmd == ["claude", "-p", "fix the bug", "--dangerously-skip-permissions"]


def test_resolve_list_command():
    cmd = resolve_command(["python", "agent.py"], "hello")
    assert cmd == ["python", "agent.py", "--prompt", "hello"]


def test_resolve_unknown_string_fallback():
    cmd = resolve_command("aider", "do stuff")
    assert cmd == ["aider", "--prompt", "do stuff"]
