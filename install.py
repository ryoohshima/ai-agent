#!/usr/bin/env python3
"""Link shared settings; preserve local credentials, runtime data and integrations."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import tempfile
import tomllib

import tomlkit

REPO = Path(__file__).resolve().parent


def install(home, dry=False):
    backup = home / ".local/state/ai-agent" / datetime.now().strftime("install-%Y%m%d-%H%M%S-%f")
    # Validate inputs before creating links or changing any existing settings.
    config_path = home / ".codex/config.toml"
    original = config_path.read_text() if config_path.exists() else ""
    config = tomllib.loads(original)
    defaults = tomllib.loads((REPO / "codex/config.toml").read_text())
    servers = json.loads((REPO / "shared/mcp-servers.json").read_text())["mcpServers"]
    claude_path = home / ".claude.json"
    claude = json.loads(claude_path.read_text()) if claude_path.exists() else {}
    hooks_path = home / ".codex/hooks.json"
    hooks = json.loads(hooks_path.read_text()) if hooks_path.exists() else {}
    hook_defaults = json.loads((REPO / "codex/hooks.json").read_text())["hooks"]

    additions = "".join(f"{key} = {json.dumps(value)}\n" for key, value in defaults.items() if key not in config)
    config = tomlkit.parse(additions + original)
    codex_servers = {}
    for name, server in servers.items():
        codex_servers[name] = {key: server[key] for key in ("command", "args", "url", "env") if key in server}
        if "timeout" in server:
            codex_servers[name]["tool_timeout_sec"] = server["timeout"] / 1000
    # Replace repo-owned servers in both clients; retain local-only servers.
    for document, key, definitions in (
        (config, "mcp_servers", codex_servers),
        (claude, "mcpServers", servers),
    ):
        current = document.setdefault(key, {})
        changed = {name: server for name, server in definitions.items() if current.get(name) != server}
        # Remove old tables before adding any, preserving TOML dotted-key scopes.
        for name in changed:
            current.pop(name, None)
        current.update(changed)
    merged = tomlkit.dumps(config)
    if tomllib.loads(merged) != config.unwrap():
        raise ValueError("TOML serialization changed settings")

    def save(path, move=False):
        dest = backup / path.relative_to(home)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if move:
            path.rename(dest)
        else:
            shutil.copy2(path, dest)

    def link(source, target):
        if target.is_symlink() and target.resolve() == source.resolve():
            return
        print(f"link: {target} -> {source}")
        if dry:
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() or target.is_symlink():
            save(target, move=True)
        target.symlink_to(source, target_is_directory=source.is_dir())

    def write(path, content):
        if path.exists() and path.read_text() == content:
            return
        print(f"update: {path}")
        if dry:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            save(path)
        # Preserve symlinks installed by other tools and restrict credential files.
        destination = path.resolve()
        with tempfile.NamedTemporaryFile(mode="w", dir=destination.parent, delete=False) as stream:
            temporary = Path(stream.name)
            try:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
                os.replace(temporary, destination)
            finally:
                temporary.unlink(missing_ok=True)

    # A legacy whole-directory link must be migrated before installing file links.
    for name in (".claude", ".codex", ".agents"):
        if (home / name).is_symlink():
            raise ValueError(f"{home / name} is a directory symlink; migrate its runtime data first")

    for source, target in [
        ("shared/instructions.md", ".agents/instructions.md"),
        ("claude/CLAUDE.md", ".claude/CLAUDE.md"),
        ("claude/RTK.md", ".claude/RTK.md"),
        ("claude/settings.json", ".claude/settings.json"),
        ("shared/mcp-servers.json", ".claude/mcp-servers.json"),
        ("claude/statusline.sh", ".claude/statusline.sh"),
        ("codex/AGENTS.md", ".codex/AGENTS.md"),
    ]:
        link(REPO / source, home / target)
    for path in sorted((REPO / "shared/rules").glob("*.md")):
        link(path, home / ".agents/rules" / path.name)
        link(path, home / ".claude/rules" / path.name)
    for path in sorted((REPO / "codex/rules").glob("*.rules")):
        link(path, home / ".codex/rules" / path.name)
    for folder, targets in [
        ("shared/hooks", (".agents/hooks", ".claude/hooks")),
        ("claude/hooks", (".claude/hooks",)),
    ]:
        for path in sorted((REPO / folder).iterdir()):
            for target in targets:
                link(path, home / target / path.name)
    for path in sorted((REPO / "shared/skills").iterdir()):
        if not (path / "SKILL.md").is_file():
            continue
        for target in (".agents/skills", ".claude/skills"):
            link(path, home / target / path.name)
        legacy = home / ".codex/skills" / path.name
        if legacy.exists() or legacy.is_symlink():
            print(f"backup duplicate skill: {legacy}")
            if not dry:
                save(legacy, move=True)

    write(config_path, merged)

    if not claude_path.exists() or claude != json.loads(claude_path.read_text()):
        write(claude_path, json.dumps(claude, indent=2, ensure_ascii=False) + "\n")

    for event, groups in hook_defaults.items():
        current = hooks.setdefault("hooks", {}).setdefault(event, [])
        for group in groups:
            if group not in current:
                current.append(group)
    if not hooks_path.exists() or hooks != json.loads(hooks_path.read_text()):
        write(hooks_path, json.dumps(hooks, indent=2, ensure_ascii=False) + "\n")
    if backup.exists():
        print(f"Backup: {backup}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("--home", type=Path, default=Path.home(), help="alternate home for testing")
    args = parser.parse_args()
    install(args.home.expanduser().resolve(), args.dry_run)
