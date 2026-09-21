"""Run with uv run --no-project --with-requirements requirements.txt python3 test_install.py; never touches the real home directory."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import tomllib

from install import REPO, install


with TemporaryDirectory(prefix="ai-agent-check-") as directory:
    home = Path(directory)
    (home / ".codex/skills/git-commit").mkdir(parents=True)
    (home / ".agents/skills/git-commit").mkdir(parents=True)
    (home / ".claude").mkdir()
    (home / ".codex/skills/git-commit/local.txt").write_text("legacy skill")
    (home / ".agents/skills/git-commit/local.txt").write_text("custom skill")
    config = '''# keep this comment
model = "local-model"
[mcp_servers.context7]
command = "stale-command"
args = ["stale"]
url = "https://local.example/mcp"
enabled = false
[mcp_servers.context7.env]
OLD = "remove-me"
[mcp_servers.private]
command = "private-server" # keep private comment
[profiles.local]
model = "profile-model"
'''
    (home / ".codex/config.toml").write_text(config)
    (home / ".codex/auth.json").write_text("local auth sentinel")
    (home / ".claude/history.jsonl").write_text("history sentinel")
    (home / ".claude/settings.local.json").write_text('{"local": true}')
    (home / ".claude.json").write_text('{"local": true, "mcpServers": {"private": {"command": "private-server"}, "context7": {"url": "stale", "env": {"OLD": "remove-me"}, "command": "stale-command"}}}')
    existing_hook = {"hooks": [{"type": "command", "command": "echo external-hook"}]}
    legacy_sound = {"type": "command", "command": "afplay /System/Library/Sounds/Frog.aiff"}
    safe_sound = {"type": "command", "command": legacy_sound["command"] + " 2>/dev/null || :"}
    (home / ".codex/hooks.json").write_text(json.dumps({"hooks": {"Stop": [
        {"hooks": [legacy_sound]}, {"hooks": [safe_sound, *existing_hook["hooks"]]},
    ]}}))
    (home / ".agents/instructions.md").symlink_to(REPO / "shared/instructions.md")
    before = {p.relative_to(home): p.read_bytes() for p in home.rglob("*") if p.is_file()}
    with redirect_stdout(io.StringIO()):
        install(home, dry=True)
    assert before == {p.relative_to(home): p.read_bytes() for p in home.rglob("*") if p.is_file()}
    assert not (home / ".local").exists()
    assert (home / ".agents/instructions.md").readlink() == REPO / "shared/instructions.md"
    with redirect_stdout(io.StringIO()):
        install(home)
    common = home / ".agents/AGENTS.md"
    assert common.resolve() == REPO / "shared/AGENTS.md"
    assert (home / ".agents/instructions.md").samefile(common)
    assert "@~/.agents/AGENTS.md" in (home / ".claude/CLAUDE.md").read_text()
    assert "`~/.agents/AGENTS.md`" in (home / ".codex/AGENTS.md").read_text()
    assert (home / ".claude").is_dir() and not (home / ".claude").is_symlink()
    for name in (".agents", ".claude"):
        assert (home / name / "skills/git-commit").resolve() == REPO / "shared/skills/git-commit"
    assert not (home / ".codex/skills/git-commit").exists()
    saved = list((home / ".local/state/ai-agent").glob("install-*"))
    assert len(saved) == 1
    assert (saved[0] / ".agents/instructions.md").readlink() == REPO / "shared/instructions.md"
    assert (saved[0] / ".agents/skills/git-commit/local.txt").read_text() == "custom skill"
    assert (saved[0] / ".codex/skills/git-commit/local.txt").read_text() == "legacy skill"
    for name in (".codex/auth.json", ".claude/history.jsonl", ".claude/settings.local.json"):
        assert (home / name).read_bytes() == before[Path(name)]
    result = tomllib.loads((home / ".codex/config.toml").read_text())
    assert result["mcp_servers"]["context7"] == {"url": "https://mcp.context7.com/mcp"}
    assert result["mcp_servers"]["private"] == {"command": "private-server"}
    assert result["model"] == "local-model"
    assert result["profiles"]["local"]["model"] == "profile-model"
    assert result["mcp_servers"]["agenttakt"]["tool_timeout_sec"] == 1800
    assert result["project_doc_fallback_filenames"] == ["CLAUDE.md"]
    assert result["notify"] == ["bash", "-lc", "afplay /System/Library/Sounds/Bottle.aiff"]
    rendered = (home / ".codex/config.toml").read_text()
    assert "# keep this comment" in rendered
    assert 'command = "private-server" # keep private comment' in rendered
    assert (saved[0] / ".codex/config.toml").read_text() == config
    claude_servers = json.loads((home / ".claude.json").read_text())["mcpServers"]
    assert claude_servers["private"]["command"] == "private-server"
    assert claude_servers["context7"] == json.loads((REPO / "shared/mcp-servers.json").read_text())["mcpServers"]["context7"]
    assert json.loads((home / ".codex/hooks.json").read_text())["hooks"]["Stop"] == [existing_hook]
    output = io.StringIO()
    with redirect_stdout(output):
        install(home)
    assert not output.getvalue(), output.getvalue()
    # Valid TOML representations must all replace the entire owned server.
    for index, source in enumerate((
        'mcp_servers = {context7 = {url = "stale", env = {OLD = "old"}}, private = {command = "private-server"}}\n',
        'mcp_servers.context7.url = "stale"\nmcp_servers.context7.env.OLD = "old"\nmcp_servers.private.command = "private-server"\n',
        '[mcp_servers."context7".env]\nOLD = "old"\n[mcp_servers.private]\ncommand = "private-server"\n[mcp_servers."context7"]\nurl = "stale"\n',
    )):
        alternate = home / f"representation-{index}"
        (alternate / ".codex").mkdir(parents=True)
        target = alternate / ".codex/config.toml"
        target.write_text(source)
        with redirect_stdout(io.StringIO()):
            install(alternate)
        parsed = tomllib.loads(target.read_text())
        assert parsed["mcp_servers"]["context7"] == {"url": "https://mcp.context7.com/mcp"}
        assert parsed["mcp_servers"]["private"] == {"command": "private-server"}
        output = io.StringIO()
        with redirect_stdout(output):
            install(alternate)
        assert not output.getvalue(), output.getvalue()

    # Invalid existing config must fail before any links are installed.
    bad_home = home / "invalid"
    (bad_home / ".codex").mkdir(parents=True)
    (bad_home / ".codex/config.toml").write_text("[broken")
    try:
        install(bad_home)
        raise AssertionError("Invalid TOML accepted")
    except tomllib.TOMLDecodeError:
        assert not (bad_home / ".agents").exists()

print("PASS: dry-run, backups, shared links, local data, config merge, idempotency, invalid input")
