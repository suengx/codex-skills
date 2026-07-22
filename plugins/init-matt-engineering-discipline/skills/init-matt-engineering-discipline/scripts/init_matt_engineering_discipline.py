#!/usr/bin/env python3
"""Initialize a repo with Matt skills and GitHub engineering scaffold."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = SKILL_DIR / "assets" / "templates"
LOCAL_SKILLS_DIR = SKILL_DIR / "assets" / "local-skills"


LABELS = [
    ("needs-triage", "D4C5F9", "等待维护者初筛"),
    ("needs-info", "F9D0C4", "等待提报者补充信息"),
    ("ready-for-agent", "0E8A16", "规格足够清楚，可交给 agent 执行"),
    ("ready-for-human", "1D76DB", "需要人类工程师处理"),
    ("wontfix", "FFFFFF", "明确不处理"),
    ("type:bug", "D73A4A", "Bug 或回归"),
    ("type:feature", "A2EEEF", "新能力或改进"),
    ("type:spec", "7057FF", "规格 issue"),
    ("type:task", "C2E0C6", "执行任务"),
    ("type:decision", "FBCA04", "需要先决策的问题"),
    ("type:refactor", "BFDADC", "重构"),
    ("type:docs", "0075CA", "文档"),
    ("type:chore", "EDEDED", "维护事务"),
    ("area:product", "BFD4F2", "产品和需求"),
    ("area:frontend", "BFD4F2", "前端"),
    ("area:backend", "BFD4F2", "后端"),
    ("area:api", "BFD4F2", "接口和服务契约"),
    ("area:data", "BFD4F2", "数据、模型或存储"),
    ("area:infra", "BFD4F2", "基础设施"),
    ("area:docs", "BFD4F2", "文档"),
    ("priority:p0", "B60205", "最高优先级"),
    ("priority:p1", "D93F0B", "高优先级"),
    ("priority:p2", "FBCA04", "中优先级"),
    ("priority:p3", "C5DEF5", "低优先级"),
    ("size:xs", "EDEDED", "很小"),
    ("size:s", "EDEDED", "小"),
    ("size:m", "EDEDED", "中"),
    ("size:l", "EDEDED", "大"),
    ("risk:high", "B60205", "高风险"),
    ("blocked", "000000", "存在阻塞"),
]


def print_step(message: str) -> None:
    print(f"\n==> {message}")


def run(
    cmd: list[str],
    *,
    cwd: Path,
    dry_run: bool = False,
    check: bool = True,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    printable = " ".join(cmd)
    if dry_run:
        print(f"[dry-run] {printable}")
        return subprocess.CompletedProcess(cmd, 0, "", "")
    print(f"$ {printable}")
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def output(cmd: list[str], *, cwd: Path, dry_run: bool = False) -> str:
    if dry_run:
        print(f"[dry-run] {' '.join(cmd)}")
        return ""
    result = run(cmd, cwd=cwd, capture=True)
    return result.stdout.strip()


def require_cmd(name: str, install_hint: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"Missing `{name}`. {install_hint}")


def ask(prompt: str, default: str | None = None, *, yes: bool = False) -> str:
    if yes:
        if default is None:
            raise SystemExit(f"Missing required value for non-interactive run: {prompt}")
        return default
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or (default or "")


def confirm(prompt: str, *, yes: bool = False, default: bool = False) -> bool:
    if yes:
        return True
    marker = "Y/n" if default else "y/N"
    value = input(f"{prompt} [{marker}]: ").strip().lower()
    if not value:
        return default
    return value in {"y", "yes"}


def current_branch(cwd: Path, dry_run: bool) -> str:
    branch = output(["git", "branch", "--show-current"], cwd=cwd, dry_run=dry_run)
    return branch or "main"


def active_github_user(cwd: Path, dry_run: bool) -> str:
    if dry_run:
        return "DRY_RUN_USER"
    run(["gh", "auth", "status"], cwd=cwd)
    login = output(["gh", "api", "user", "--jq", ".login"], cwd=cwd)
    if not login:
        raise SystemExit("Could not determine active GitHub user. Run `gh auth status`.")
    return login


def existing_github_remote(cwd: Path, remote_name: str, dry_run: bool) -> str | None:
    if dry_run:
        return None
    result = subprocess.run(
        ["git", "remote", "get-url", remote_name],
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        return None
    url = result.stdout.strip()
    if "github.com" not in url:
        return None
    return url


def copy_template_file(src: Path, dst: Path, *, force: bool, dry_run: bool, replacements: dict[str, str]) -> None:
    content = src.read_text(encoding="utf-8")
    for key, value in replacements.items():
        content = content.replace(key, value)

    if dst.exists() and not force:
        print(f"skip existing {dst.relative_to(Path.cwd()) if dst.is_relative_to(Path.cwd()) else dst}")
        return
    if dry_run:
        print(f"[dry-run] write {dst}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(content, encoding="utf-8")
    print(f"wrote {dst}")


def write_templates(cwd: Path, *, owner: str, repo_name: str, force: bool, dry_run: bool) -> None:
    replacements = {
        "OWNER_PLACEHOLDER": owner,
        "PROJECT_NAME_PLACEHOLDER": repo_name,
    }
    for src in sorted(TEMPLATE_DIR.rglob("*")):
        if src.is_dir():
            continue
        rel = src.relative_to(TEMPLATE_DIR)
        copy_template_file(src, cwd / rel, force=force, dry_run=dry_run, replacements=replacements)


def install_matt_skills(cwd: Path, *, skip: bool, dry_run: bool) -> None:
    if skip:
        print("skip Matt skills install")
        return
    if (cwd / "skills-lock.json").exists() and (cwd / ".agents" / "skills").exists():
        print("Matt skills already appear installed; skip")
        return
    require_cmd("npx", "Install Node.js/npm, then retry.")
    run(["npx", "skills@latest", "add", "mattpocock/skills"], cwd=cwd, dry_run=dry_run)


def copy_skill_tree(src: Path, dst: Path, *, force: bool, dry_run: bool) -> None:
    if dst.exists() and not force:
        print(f"skip existing local skill {dst}")
        return
    if dry_run:
        print(f"[dry-run] copy local skill {src} -> {dst}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    for path in sorted(src.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(src)
        if rel == Path("SKILL.template.md"):
            rel = Path("SKILL.md")
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    print(f"copied local skill {src.name} -> {dst}")


def install_bundled_local_skills(cwd: Path, *, include_source: bool, force: bool, dry_run: bool) -> None:
    if not LOCAL_SKILLS_DIR.exists():
        print("no bundled local skills")
        return
    for skill_dir in sorted(path for path in LOCAL_SKILLS_DIR.iterdir() if path.is_dir()):
        copy_skill_tree(skill_dir, cwd / ".agents" / "skills" / skill_dir.name, force=force, dry_run=dry_run)
        if include_source:
            copy_skill_tree(skill_dir, cwd / "skills" / "productivity" / skill_dir.name, force=force, dry_run=dry_run)


def ensure_git_repo(cwd: Path, *, dry_run: bool) -> None:
    if (cwd / ".git").exists():
        return
    run(["git", "init"], cwd=cwd, dry_run=dry_run)


def ensure_default_branch(cwd: Path, branch: str, *, dry_run: bool) -> None:
    current = current_branch(cwd, dry_run)
    if current == branch:
        return
    if current:
        run(["git", "branch", "-M", branch], cwd=cwd, dry_run=dry_run)


def ensure_remote(cwd: Path, repo: str, remote_name: str, *, create_repo: bool, description: str, visibility: str, dry_run: bool) -> None:
    existing = existing_github_remote(cwd, remote_name, dry_run)
    if existing:
        print(f"remote {remote_name} already exists: {existing}")
        return

    if create_repo:
        cmd = [
            "gh",
            "repo",
            "create",
            repo,
            f"--{visibility}",
            "--description",
            description,
            "--source",
            ".",
            "--remote",
            remote_name,
        ]
        run(cmd, cwd=cwd, dry_run=dry_run)
    else:
        run(["git", "remote", "add", remote_name, f"https://github.com/{repo}.git"], cwd=cwd, dry_run=dry_run)


def configure_labels(cwd: Path, repo: str, *, skip: bool, dry_run: bool) -> None:
    if skip:
        print("skip labels")
        return
    for name, color, description in LABELS:
        run(
            [
                "gh",
                "label",
                "create",
                name,
                "--repo",
                repo,
                "--color",
                color,
                "--description",
                description,
                "--force",
            ],
            cwd=cwd,
            dry_run=dry_run,
        )


def ensure_milestone(cwd: Path, repo: str, title: str, *, dry_run: bool) -> int | None:
    if dry_run:
        print(f"[dry-run] ensure milestone {title}")
        return None
    existing = output(
        ["gh", "api", "--method", "GET", f"repos/{repo}/milestones", "-f", "state=all", "--jq", f'.[] | select(.title=="{title}") | .number'],
        cwd=cwd,
    )
    if existing:
        print(f"milestone exists: {title} #{existing.splitlines()[0]}")
        return int(existing.splitlines()[0])
    number = output(
        [
            "gh",
            "api",
            f"repos/{repo}/milestones",
            "-f",
            f"title={title}",
            "-f",
            "description=初始化 GitHub 工程治理、Matt skills 和人类-agent 协作流程；不包含业务领域配置",
            "--jq",
            ".number",
        ],
        cwd=cwd,
    )
    print(f"created milestone {title} #{number}")
    return int(number)


def create_project(cwd: Path, owner: str, title: str, *, enabled: bool, dry_run: bool) -> None:
    if not enabled:
        print("skip GitHub Project")
        return
    run(["gh", "project", "create", "--owner", owner, "--title", title], cwd=cwd, dry_run=dry_run, check=False)


def create_governance_issue(cwd: Path, repo: str, milestone_title: str | None, *, skip: bool, dry_run: bool) -> None:
    if skip:
        print("skip governance issue")
        return
    title = "初始化 Matt skills 工程纪律"
    if not dry_run:
        existing = output(
            ["gh", "issue", "list", "--repo", repo, "--state", "open", "--search", title, "--json", "number,title", "--jq", f'.[] | select(.title=="{title}") | .number'],
            cwd=cwd,
        )
        if existing:
            print(f"governance issue already exists: #{existing.splitlines()[0]}")
            return

    body = """## 背景

本仓库需要建立 Matt Pocock skills、中文优先项目资产、worktree 协作纪律和 GitHub 标准工程治理。

## 目标

- [ ] Matt skills 已安装
- [ ] `worktree-agent-coordination` 已安装
- [ ] `AGENTS.md` / `CONTEXT.md` / `docs/agents/*` 已落地
- [ ] GitHub labels 已配置
- [ ] Issue templates / PR template 已配置
- [ ] CI workflow 已配置
- [ ] main 分支保护或 ruleset 已配置
- [ ] 第一版 Project / Milestone 已建立
- [ ] 业务领域信息已由目标仓库自行补入 README、CONTEXT 或 ADR；脚手架不内置业务域

## 工作流

Issue -> Execution Workspace -> Branch/Worktree -> PR -> CI -> Review -> Merge -> Release
"""
    cmd = [
        "gh",
        "issue",
        "create",
        "--repo",
        repo,
        "--title",
        title,
        "--body",
        body,
        "--label",
        "type:task",
        "--label",
        "ready-for-human",
    ]
    if milestone_title is not None:
        cmd += ["--milestone", milestone_title]
    run(cmd, cwd=cwd, dry_run=dry_run)


def apply_ruleset(cwd: Path, repo: str, *, enabled: bool, dry_run: bool) -> None:
    if not enabled:
        print("skip branch ruleset")
        return
    ruleset = {
        "name": "Protect default branch",
        "target": "branch",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "rules": [
            {"type": "deletion"},
            {"type": "non_fast_forward"},
            {
                "type": "pull_request",
                "parameters": {
                    "required_approving_review_count": 1,
                    "dismiss_stale_reviews_on_push": True,
                    "require_code_owner_review": False,
                    "require_last_push_approval": False,
                    "required_review_thread_resolution": True,
                },
            },
        ],
    }
    if dry_run:
        print("[dry-run] create ruleset:")
        print(json.dumps(ruleset, ensure_ascii=False, indent=2))
        return
    proc = subprocess.run(
        ["gh", "api", f"repos/{repo}/rulesets", "--input", "-"],
        cwd=str(cwd),
        input=json.dumps(ruleset),
        text=True,
    )
    if proc.returncode != 0:
        print("ruleset creation failed; configure branch protection manually in GitHub settings.")


def commit_and_push(
    cwd: Path,
    branch: str,
    remote_name: str,
    *,
    include_skill_source: bool,
    skip_commit: bool,
    skip_push: bool,
    dry_run: bool,
) -> None:
    if skip_commit:
        print("skip commit")
    else:
        candidates = [
            "AGENTS.md",
            "CONTEXT.md",
            "CONTRIBUTING.md",
            "CODEOWNERS",
            "README.md",
            "docs",
            ".github",
            ".agents",
            "skills-lock.json",
        ]
        if include_skill_source:
            candidates.append("skills")
        existing = [path for path in candidates if (cwd / path).exists()]
        if existing:
            run(["git", "add", *existing], cwd=cwd, dry_run=dry_run)
        else:
            print("no known governance paths to stage")
        if dry_run:
            print("[dry-run] commit if staged changes exist")
        else:
            status = output(["git", "status", "--short"], cwd=cwd)
            if status:
                run(["git", "commit", "-m", "chore: initialize repository scaffold"], cwd=cwd)
            else:
                print("no changes to commit")

    if skip_push:
        print("skip push")
        return
    run(["git", "push", "-u", remote_name, branch], cwd=cwd, dry_run=dry_run)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="GitHub repo in OWNER/REPO form")
    parser.add_argument("--description", default="Repository initialized with Matt skills and GitHub governance")
    parser.add_argument("--visibility", choices=["private", "public", "internal"], default="private")
    parser.add_argument("--create-repo", action="store_true", help="Create the GitHub repo if remote is missing")
    parser.add_argument("--bind-existing", action="store_true", help="Bind local repo to an existing GitHub repo")
    parser.add_argument("--remote-name", default="origin")
    parser.add_argument("--default-branch", default="main")
    parser.add_argument("--milestone", default="v0.1-project-governance")
    parser.add_argument("--create-project", action="store_true")
    parser.add_argument("--apply-ruleset", action="store_true")
    parser.add_argument("--skip-matt-install", action="store_true")
    parser.add_argument("--skip-labels", action="store_true")
    parser.add_argument("--skip-governance-issue", action="store_true")
    parser.add_argument("--skip-commit", action="store_true")
    parser.add_argument("--skip-push", action="store_true")
    parser.add_argument(
        "--include-local-skill-source",
        action="store_true",
        help="Also copy bundled local skill source into skills/productivity/. Default only installs runnable skills under .agents/skills/.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing template files")
    parser.add_argument("--yes", action="store_true", help="Run non-interactively with defaults/provided values")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cwd = Path.cwd()

    print_step("Checking tools and GitHub identity")
    require_cmd("git", "Install git, then retry.")
    require_cmd("gh", "Install GitHub CLI from https://cli.github.com/, then run `gh auth login`.")
    ensure_git_repo(cwd, dry_run=args.dry_run)
    user = active_github_user(cwd, args.dry_run)
    print(f"active GitHub user: {user}")

    print_step("Resolving repository target")
    repo = args.repo
    if not repo:
        default_repo = f"{user}/{cwd.name}"
        repo = ask("GitHub repo (OWNER/REPO)", default_repo, yes=args.yes)
    if "/" not in repo:
        repo = f"{user}/{repo}"
    owner, repo_name = repo.split("/", 1)
    print(f"target repo: {repo}")

    if not args.create_repo and not args.bind_existing:
        if args.yes:
            args.create_repo = True
        else:
            args.create_repo = confirm("Create GitHub repo if remote is missing?", default=True)
            args.bind_existing = not args.create_repo

    print_step("Writing local governance assets")
    write_templates(cwd, owner=owner, repo_name=repo_name, force=args.force, dry_run=args.dry_run)

    print_step("Installing Matt Pocock skills")
    install_matt_skills(cwd, skip=args.skip_matt_install, dry_run=args.dry_run)

    print_step("Installing bundled local skills")
    install_bundled_local_skills(
        cwd,
        include_source=args.include_local_skill_source,
        force=args.force,
        dry_run=args.dry_run,
    )

    print_step("Configuring git remote")
    ensure_default_branch(cwd, args.default_branch, dry_run=args.dry_run)
    ensure_remote(
        cwd,
        repo,
        args.remote_name,
        create_repo=args.create_repo,
        description=args.description,
        visibility=args.visibility,
        dry_run=args.dry_run,
    )

    print_step("Committing and pushing baseline")
    commit_and_push(
        cwd,
        args.default_branch,
        args.remote_name,
        include_skill_source=args.include_local_skill_source,
        skip_commit=args.skip_commit,
        skip_push=args.skip_push,
        dry_run=args.dry_run,
    )

    print_step("Configuring GitHub labels and milestone")
    configure_labels(cwd, repo, skip=args.skip_labels, dry_run=args.dry_run)
    milestone_number = ensure_milestone(cwd, repo, args.milestone, dry_run=args.dry_run)

    print_step("Configuring optional GitHub governance")
    create_project(cwd, owner, args.milestone, enabled=args.create_project, dry_run=args.dry_run)
    apply_ruleset(cwd, repo, enabled=args.apply_ruleset, dry_run=args.dry_run)
    create_governance_issue(cwd, repo, args.milestone if milestone_number is not None or args.dry_run else None, skip=args.skip_governance_issue, dry_run=args.dry_run)

    print_step("Done")
    print("Initialized repository scaffold.")
    print(f"Repo: https://github.com/{repo}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
