"""Demande un backtest distant (GitHub Actions) puis récupère le résultat.

    python scripts/request_backtest.py --from 2026-09-01 --to 2026-10-31 [--coins BTC,ETH] [--mode maker]
    python scripts/request_backtest.py --fetch <id>          # récupère le rapport quand il est prêt

La demande est un commit sur la branche `backtest-requests` (= main + request.json),
ce qui déclenche le workflow `backtest`. Le rapport arrive sur la branche
`backtest-results`, dans reports/<id>/.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def git(*args: str, cwd: Path = REPO, check: bool = True) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit(r.stderr)
    return r.stdout


def request(a) -> int:
    rid = f"bt-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}"
    req = {"id": rid, "from": a.start, "to": a.end, "coins": a.coins, "mode": a.mode,
           "with_trades": a.with_trades, "requested_by": a.by}
    git("fetch", "origin", "main")
    wt = REPO / ".backtest-request-worktree"
    if wt.exists():
        git("worktree", "remove", "--force", str(wt), check=False)
    git("worktree", "add", "--detach", str(wt), "origin/main")
    (wt / "request.json").write_text(json.dumps(req, indent=2) + "\n")
    git("add", "request.json", cwd=wt)
    git("commit", "-q", "-m", f"backtest request {rid}: {a.start} → {a.end} {a.coins} {a.mode}", cwd=wt)
    git("push", "--force", "origin", "HEAD:refs/heads/backtest-requests", cwd=wt)
    git("worktree", "remove", "--force", str(wt), check=False)
    print(json.dumps(req))
    return 0


def fetch(rid: str, wait_s: int) -> int:
    deadline = time.time() + wait_s
    while True:
        git("fetch", "origin", "backtest-results", check=False)
        names = git("ls-tree", "-r", "--name-only", "origin/backtest-results", check=False).splitlines()
        mine = [n for n in names if n.startswith(f"reports/{rid}/")]
        if mine:
            out = REPO / "data" / "remote_reports" / rid
            out.mkdir(parents=True, exist_ok=True)
            for n in mine:
                (out / Path(n).name).write_text(git("show", f"origin/backtest-results:{n}"))
            md = [p for p in out.glob("backtest_*.md")]
            print(md[0].read_text() if md else f"report files: {[Path(n).name for n in mine]}")
            return 0
        if time.time() >= deadline:
            print("not ready yet")
            return 1
        time.sleep(30)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--from", dest="start")
    p.add_argument("--to", dest="end")
    p.add_argument("--coins", default="BTC,ETH")
    p.add_argument("--mode", default="maker", choices=("maker", "taker"))
    p.add_argument("--with-trades", action="store_true")
    p.add_argument("--by", default="claude")
    p.add_argument("--fetch")
    p.add_argument("--wait-s", type=int, default=0)
    a = p.parse_args()
    if a.fetch:
        return fetch(a.fetch, a.wait_s)
    if not (a.start and a.end):
        p.error("--from and --to are required")
    return request(a)


if __name__ == "__main__":
    sys.exit(main())
