"""Envoie une commande de supervision au bot (via la branche GitHub `control`).

    python scripts/supervise.py ping --reason "contrôle de routine"
    python scripts/supervise.py pause --reason "volatilité anormale sur ETH"
    python scripts/supervise.py resume --reason "marché revenu au calme"
    python scripts/supervise.py flatten --reason "flux Hyperliquid instable"
    python scripts/supervise.py set_risk_scale --scale 0.5 --reason "drawdown 3 %"
    python scripts/supervise.py disable_coin --coin ETH --reason "spread anormal"
    python scripts/supervise.py go_live_report --reason "bilan hebdo"
    python scripts/supervise.py list

Chaque commande devient un commit sur la branche `control` (journal d'audit).
Le bot accuse réception (événement PostHog `command_ack`) puis confirme
l'application (`command_applied`), en général en moins d'une minute.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agents.control_agent import ALL_CMDS, validate_command  # noqa: E402

BRANCH = "control"
PATH = "control/commands.json"
KEEP = 100


def git(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, check=check, capture_output=True, text=True)


def worktree(repo: Path) -> Path:
    wt = repo / ".control-worktree"
    remote_exists = git("fetch", "origin", BRANCH, cwd=repo, check=False).returncode == 0
    if not (wt / ".git").exists():
        if remote_exists:
            git("worktree", "add", "-B", BRANCH, str(wt), f"origin/{BRANCH}", cwd=repo)
        else:
            git("worktree", "add", "--detach", str(wt), cwd=repo)
            git("checkout", "--orphan", BRANCH, cwd=wt)
            git("rm", "-rf", "--quiet", ".", cwd=wt, check=False)
    elif remote_exists:
        git("reset", "--hard", f"origin/{BRANCH}", cwd=wt)
    return wt


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=sorted(ALL_CMDS | {"list"}))
    p.add_argument("--reason", default="")
    p.add_argument("--scale", type=float)
    p.add_argument("--coin")
    p.add_argument("--by", default="claude")
    p.add_argument("--repo-dir", default=str(Path(__file__).resolve().parents[1]))
    p.add_argument("--ttl-min", type=int, default=60)
    a = p.parse_args()

    repo = Path(a.repo_dir)
    wt = worktree(repo)
    f = wt / PATH
    doc = json.loads(f.read_text()) if f.exists() else {"commands": []}
    if a.cmd == "list":
        print(json.dumps(doc["commands"][-20:], indent=2, ensure_ascii=False))
        return 0

    now = datetime.now(timezone.utc)
    args = {}
    if a.scale is not None:
        args["scale"] = a.scale
    if a.coin:
        args["coin"] = a.coin
    cmd = {"id": f"c-{now:%Y%m%dT%H%M%S}-{uuid.uuid4().hex[:6]}", "cmd": a.cmd, "args": args,
           "reason": a.reason, "issued_by": a.by, "issued_at": now.isoformat(timespec="seconds"),
           "expires_at": (now + timedelta(minutes=a.ttl_min)).isoformat(timespec="seconds")}
    why = validate_command(cmd, ["*any*"] if a.coin is None else [a.coin])
    if why:
        print(f"refused locally: {why}", file=sys.stderr)
        return 2
    doc["commands"] = (doc["commands"] + [cmd])[-KEEP:]
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    readme = wt / "README.md"
    if not readme.exists():
        readme.write_text("# Canal de supervision hl-swarm\n\nBranche lue par le bot (lecture seule). "
                          "Chaque commit = une commande ; voir scripts/supervise.py sur main.\n")
    git("add", "-A", cwd=wt)
    git("commit", "-q", "-m", f"control: {a.cmd} {json.dumps(args) if args else ''} — {a.reason}".strip(), cwd=wt)
    push = git("-c", "push.negotiate=true", "push", "-u", "origin", BRANCH, cwd=wt, check=False)
    if push.returncode != 0:
        print(push.stderr, file=sys.stderr)
        return 1
    print(json.dumps(cmd, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
