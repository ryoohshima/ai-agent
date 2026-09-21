"""Run with uv run --no-project --with-requirements requirements.txt python3 test_install.py; never touches the real home directory."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import tomllib
from unittest.mock import patch

from install import REPO, install


with TemporaryDirectory(prefix="ai-agent-check-") as directory:
    home = Path(directory)
    (home / ".codex/skills").mkdir(parents=True)
    (home / ".agents/skills/git-commit").mkdir(parents=True)
    (home / ".claude").mkdir()
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
    (home / ".codex/hooks.json").write_text(json.dumps({"hooks": {"Stop": [existing_hook]}}))
    (home / ".agents/instructions.md").symlink_to(REPO / "shared/instructions.md")
    (home / ".agents/skills/write-a-skill").symlink_to(REPO / "shared/skills/write-a-skill")
    (home / ".agents/skills/coding-standards").mkdir()
    (home / ".agents/skills/coding-standards/custom.txt").write_text("keep custom skill")
    unrelated = home / "another-repo/shared/skills/write-a-skill"
    unrelated.mkdir(parents=True)
    (unrelated / "SKILL.md").write_text("keep unrelated skill")
    (home / ".codex/skills/write-a-skill").symlink_to(unrelated)
    before = {p.relative_to(home): p.read_bytes() for p in home.rglob("*") if p.is_file()}
    with redirect_stdout(io.StringIO()):
        install(home, dry=True)
    assert before == {p.relative_to(home): p.read_bytes() for p in home.rglob("*") if p.is_file()}
    assert not (home / ".local").exists()
    assert (home / ".agents/instructions.md").readlink() == REPO / "shared/instructions.md"
    assert (home / ".agents/skills/write-a-skill").is_symlink()
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
    assert not (home / ".agents/skills/write-a-skill").is_symlink()
    assert (home / ".agents/skills/coding-standards/custom.txt").read_text() == "keep custom skill"
    assert (home / ".codex/skills/write-a-skill").resolve() == unrelated.resolve()
    saved = list((home / ".local/state/ai-agent").glob("install-*"))
    assert len(saved) == 1
    assert (saved[0] / ".agents/instructions.md").readlink() == REPO / "shared/instructions.md"
    assert (saved[0] / ".agents/skills/git-commit/local.txt").read_text() == "custom skill"
    assert (saved[0] / ".agents/skills/write-a-skill").readlink() == REPO / "shared/skills/write-a-skill"
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

    # New files and nested directories must deploy without an installer edit.
    repo = (home / "repo").resolve()
    for folder in ("shared", "claude", "codex"):
        shutil.copytree(REPO / folder, repo / folder)
    added = {
        "shared/new-guide.md": (".agents/new-guide.md",),
        "claude/templates/new.txt": (".claude/templates/new.txt",),
        "codex/templates/new.txt": (".codex/templates/new.txt",),
        "shared/hooks/nested/new.sh": (".agents/hooks/nested/new.sh", ".claude/hooks/nested/new.sh"),
        "shared/skills/new-skill/SKILL.md": (".agents/skills/new-skill/SKILL.md", ".claude/skills/new-skill/SKILL.md"),
    }
    for source in added:
        path = repo / source
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("new content")
    for name in ("settings.json.bak", ".DS_Store", "draft~"):
        (repo / "claude" / name).write_text("not for deployment")
    fresh = home / "fresh"
    external = fresh / ".agents/skills/app-managed/SKILL.md"
    external.parent.mkdir(parents=True)
    external.write_text("app-owned")
    with patch("install.REPO", repo), redirect_stdout(io.StringIO()):
        install(fresh)
    for source, targets in added.items():
        for target in targets:
            assert (fresh / target).resolve() == repo / source
    assert (fresh / ".agents/skills/new-skill").is_symlink()
    assert not (fresh / ".claude/templates").is_symlink()
    assert external.read_text() == "app-owned"
    assert not (fresh / ".codex/config.toml").is_symlink()
    assert not (fresh / ".codex/hooks.json").is_symlink()
    for name in ("settings.json.bak", ".DS_Store", "draft~"):
        assert not (fresh / ".claude" / name).exists()
    output = io.StringIO()
    with patch("install.REPO", repo), redirect_stdout(output):
        install(fresh)
    assert not output.getvalue(), output.getvalue()

print("PASS: dry-run, backups, shared links, local data, config merge, idempotency, invalid input, automatic file discovery")
