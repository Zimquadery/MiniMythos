AGENT_COMMANDS: dict[str, list[str]] = {
    "opencode": ["opencode", "run", "$PROMPT"],
    "claude": ["claude", "-p", "$PROMPT", "--dangerously-skip-permissions"],
}


def resolve_command(command: str | list[str], prompt: str) -> list[str]:
    if isinstance(command, list):
        return [*command, "--prompt", prompt]
    if command in AGENT_COMMANDS:
        return [arg.replace("$PROMPT", prompt) for arg in AGENT_COMMANDS[command]]
    return [command, "--prompt", prompt]
