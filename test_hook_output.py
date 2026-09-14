"""Check patched security-guidance output: python3 test_hook_output.py <hook.py>."""
import ast
from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace

source = ast.parse(Path(sys.argv[1]).read_text())
functions = [node for node in source.body if isinstance(node, ast.FunctionDef)
             and node.name in ("emit_json", "emit_metrics")]
assert len(functions) == 2
for codex in (False, True):
    namespace = {"os": SimpleNamespace(environ={"PLUGIN_ROOT": "/plugin"} if codex else {}),
                 "json": json, "sys": sys, "_PV": 20008, "_usage_metrics": lambda: {}}
    exec(compile(ast.Module(body=functions, type_ignores=[]), "hook-output", "exec"), namespace)
    for event in ("Stop", "SubagentStop", "PostToolUse"):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            namespace["emit_metrics"]({"skipped": False}, rewake_summary="Review needed",
                                      additional_context="Security finding", hook_event_name=event)
        output = json.loads(stdout.getvalue())
        assert ("metrics" in output) == (not codex)
        assert ("rewakeSummary" in output) == (not codex)
        if codex:
            assert output["systemMessage"] == "Review needed"
        if event in ("Stop", "SubagentStop"):
            assert output["decision"] == "block"
            assert output["reason"] == stderr.getvalue() == "Security finding"
        else:
            assert output["hookSpecificOutput"]["additionalContext"] == "Security finding"
    output = io.StringIO()
    with redirect_stdout(output):
        namespace["emit_json"]({"metrics": {"bash_hook_dedup": True}})
    assert json.loads(output.getvalue()) == ({} if codex else {"metrics": {"bash_hook_dedup": True}})
print("PASS: Codex output, security findings, continuation decisions, Claude telemetry")
