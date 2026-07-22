#!/usr/bin/env python3
"""Read-only guard for branch/worktree multi-agent coordination."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


DEFAULT_MAIN = "origin/main"


def run(cmd: list[str], cwd: Path, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def out(cmd: list[str], cwd: Path, default: str = "") -> str:
    result = run(cmd, cwd)
    if result.returncode != 0:
        return default
    return result.stdout.strip()


def lines(cmd: list[str], cwd: Path) -> list[str]:
    text = out(cmd, cwd)
    return [line for line in text.splitlines() if line.strip()]


def is_git_repo(cwd: Path) -> bool:
    return run(["git", "rev-parse", "--is-inside-work-tree"], cwd).returncode == 0


def git_root(cwd: Path) -> Path | None:
    root = out(["git", "rev-parse", "--show-toplevel"], cwd)
    return Path(root) if root else None


def maybe_fetch(cwd: Path, no_fetch: bool) -> bool:
    if no_fetch:
        return False
    if run(["git", "rev-parse", "--verify", "origin"], cwd).returncode != 0:
        return False
    return run(["git", "fetch", "--prune", "origin"], cwd).returncode == 0


def rev_exists(cwd: Path, rev: str) -> bool:
    return run(["git", "rev-parse", "--verify", rev], cwd).returncode == 0


def ahead_behind(cwd: Path, upstream: str) -> tuple[int | None, int | None]:
    if not rev_exists(cwd, "HEAD") or not rev_exists(cwd, upstream):
        return None, None
    output = out(["git", "rev-list", "--left-right", "--count", f"HEAD...{upstream}"], cwd)
    if not output:
        return None, None
    left, right = output.split()
    return int(left), int(right)


def in_progress_state(git_dir: Path) -> list[str]:
    states: list[str] = []
    markers = {
        "MERGE_HEAD": "merge",
        "CHERRY_PICK_HEAD": "cherry-pick",
        "REVERT_HEAD": "revert",
    }
    for marker, label in markers.items():
        if (git_dir / marker).exists():
            states.append(label)
    if (git_dir / "rebase-merge").exists() or (git_dir / "rebase-apply").exists():
        states.append("rebase")
    return states


@dataclass
class Status:
    repo: str
    cwd: str
    git_root: str | None
    branch: str
    head: str
    origin_main: str | None
    fetched: bool
    dirty: bool
    dirty_files: list[str]
    detached_head: bool
    in_progress: list[str]
    ahead_origin_main: int | None
    behind_origin_main: int | None
    commits_ahead: list[str]
    commits_behind: list[str]
    remotes: list[str]
    worktree_path: str
    risk_level: str
    recommendations: list[str]


def collect_status(cwd: Path, *, no_fetch: bool = False, upstream: str = DEFAULT_MAIN) -> Status:
    if not is_git_repo(cwd):
        return Status(
            repo="not-a-git-repo",
            cwd=str(cwd),
            git_root=None,
            branch="",
            head="",
            origin_main=None,
            fetched=False,
            dirty=False,
            dirty_files=[],
            detached_head=False,
            in_progress=[],
            ahead_origin_main=None,
            behind_origin_main=None,
            commits_ahead=[],
            commits_behind=[],
            remotes=[],
            worktree_path=str(cwd),
            risk_level="red",
            recommendations=["当前目录不是 git repo，不能执行 worktree 协调。"],
        )

    root = git_root(cwd)
    assert root is not None
    fetched = maybe_fetch(root, no_fetch)

    branch = out(["git", "branch", "--show-current"], root)
    detached = not bool(branch)
    has_head = rev_exists(root, "HEAD")
    head = out(["git", "rev-parse", "--short", "HEAD"], root) if has_head else "(unborn)"
    origin_main = out(["git", "rev-parse", "--short", upstream], root) if rev_exists(root, upstream) else None
    dirty_files = lines(["git", "status", "--short"], root)
    dirty = bool(dirty_files)
    ahead, behind = ahead_behind(root, upstream)
    commits_ahead = lines(["git", "log", "--oneline", f"{upstream}..HEAD", "--max-count=10"], root) if rev_exists(root, upstream) else []
    commits_behind = lines(["git", "log", "--oneline", f"HEAD..{upstream}", "--max-count=10"], root) if rev_exists(root, upstream) else []
    remotes = lines(["git", "remote", "-v"], root)
    git_dir_text = out(["git", "rev-parse", "--git-dir"], root)
    git_dir = (root / git_dir_text).resolve() if git_dir_text else root / ".git"
    progress = in_progress_state(git_dir)

    risk = "green"
    recommendations: list[str] = []
    if not has_head:
        risk = "yellow"
        recommendations.append("当前分支还没有提交；先建立初始提交后再进行 branch/worktree 收敛判断。")
    if detached and has_head:
        risk = "red"
        recommendations.append("当前是 detached HEAD；开始或交付前先建立明确 branch。")
    if progress:
        risk = "red"
        recommendations.append(f"当前存在进行中的 git 操作：{', '.join(progress)}；先完成或恢复该状态。")
    if dirty:
        risk = "yellow" if risk == "green" else risk
        recommendations.append("工作区有未提交变更；rebase/merge/switch branch 前先保护这些变更。")
    if branch == "main" and dirty:
        risk = "red"
        recommendations.append("当前在 main 上有改动；建议切出 issue branch/worktree 后继续。")
    if behind and behind > 0:
        risk = "yellow" if risk == "green" else risk
        recommendations.append(f"{upstream} 领先当前分支 {behind} 个 commits；继续或交付前需要纳入 latest main 并重新验证。")
    if ahead == 0 and not dirty:
        recommendations.append("当前分支没有本地提交且工作区干净。")
    if not origin_main:
        risk = "yellow" if risk == "green" else risk
        recommendations.append(f"未找到 {upstream}；检查 remote 或默认分支。")

    return Status(
        repo=root.name,
        cwd=str(cwd),
        git_root=str(root),
        branch=branch or "(detached)",
        head=head,
        origin_main=origin_main,
        fetched=fetched,
        dirty=dirty,
        dirty_files=dirty_files,
        detached_head=detached,
        in_progress=progress,
        ahead_origin_main=ahead,
        behind_origin_main=behind,
        commits_ahead=commits_ahead,
        commits_behind=commits_behind,
        remotes=remotes,
        worktree_path=str(root),
        risk_level=risk,
        recommendations=recommendations,
    )


def print_human(status: Status, mode: str) -> None:
    print(f"Mode: {mode}")
    print(f"Risk: {status.risk_level}")
    print(f"Repo: {status.repo}")
    print(f"Worktree: {status.worktree_path}")
    print(f"Branch: {status.branch}")
    print(f"HEAD: {status.head}")
    print(f"origin/main: {status.origin_main or '(missing)'}")
    print(f"Fetched: {'yes' if status.fetched else 'no'}")
    print(f"Ahead origin/main: {status.ahead_origin_main}")
    print(f"Behind origin/main: {status.behind_origin_main}")
    print(f"Dirty: {'yes' if status.dirty else 'no'}")
    if status.dirty_files:
        print("Dirty files:")
        for item in status.dirty_files[:20]:
            print(f"  {item}")
    if status.in_progress:
        print(f"In-progress git operation: {', '.join(status.in_progress)}")
    if status.commits_ahead:
        print("Commits ahead:")
        for commit in status.commits_ahead:
            print(f"  {commit}")
    if status.commits_behind:
        print("Commits behind:")
        for commit in status.commits_behind:
            print(f"  {commit}")
    if status.recommendations:
        print("Recommendations:")
        for rec in status.recommendations:
            print(f"  - {rec}")


def list_worktrees(cwd: Path, *, json_output: bool) -> None:
    if not is_git_repo(cwd):
        raise SystemExit("Not a git repository.")
    root = git_root(cwd) or cwd
    output = out(["git", "worktree", "list", "--porcelain"], root)
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in output.splitlines():
        if not line:
            if current:
                entries.append(current)
                current = {}
            continue
        if " " in line:
            key, value = line.split(" ", 1)
        else:
            key, value = line, "true"
        current[key] = value
    if current:
        entries.append(current)

    if json_output:
        print(json.dumps(entries, ensure_ascii=False, indent=2))
        return
    for entry in entries:
        print(f"{entry.get('worktree', '')}  {entry.get('branch', entry.get('detached', ''))}  {entry.get('HEAD', '')}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "mode",
        choices=["status", "start", "sync-check", "finish", "list-worktrees"],
        help="Guard mode to run.",
    )
    parser.add_argument("--upstream", default=DEFAULT_MAIN)
    parser.add_argument("--no-fetch", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cwd = Path.cwd()
    if args.mode == "list-worktrees":
        list_worktrees(cwd, json_output=args.json)
        return 0

    status = collect_status(cwd, no_fetch=args.no_fetch, upstream=args.upstream)
    if args.json:
        print(json.dumps(asdict(status), ensure_ascii=False, indent=2))
    else:
        print_human(status, args.mode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
