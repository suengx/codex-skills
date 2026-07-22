---
name: init-matt-engineering-discipline
description: Initialize a repository scaffold with Matt Pocock skills, Chinese-first agent discipline, worktree coordination, and GitHub-standard engineering governance. Use when the user wants to set up or bootstrap a repo for human-agent collaboration, install mattpocock/skills, create AGENTS.md/CONTEXT.md/docs/agents assets, configure GitHub repo/remote/labels/milestones/issues/templates/CI/PR workflow, or make the same engineering discipline reusable across projects or Macs.
---

# Repository Initialization Scaffold

Initialize a repo as a human-agent engineering system: Matt skills for process control, Chinese-first repo assets for team continuity, worktree/branch coordination for execution isolation, and GitHub entities for issues, PRs, CI, review, and release governance.

This is a generic repository scaffold. It must not encode a business domain such as law, finance, healthcare, or a product-specific ontology. Domain facts belong in the target repo's `README.md`, `CONTEXT.md`, `docs/adr/`, custom labels, or project-local skills maintained by that repo.

## Workflow

### 1. Ground the repo

Inspect the current directory before changing anything:

- `pwd`
- `git status --short --branch`
- `git remote -v`
- `gh auth status`
- existing `AGENTS.md`, `CONTEXT.md`, `docs/agents/`, `.github/`, `.agents/skills/`, `skills-lock.json`

Completion criterion: know whether this is a git repo, whether it already has a GitHub remote, which `gh` account is active, and which governance assets already exist.

### 2. Establish GitHub identity

Use local `gh` as the primary execution surface for repository setup.

- If `gh` is missing, tell the user to install GitHub CLI and stop before GitHub writes.
- If `gh auth status` fails, guide the user through `gh auth login` and stop before GitHub writes.
- If multiple accounts exist, use the active account from `gh api user --jq .login` unless the user explicitly chooses another account.

Completion criterion: one GitHub owner/account is selected and can perform repo writes.

### 3. Establish repo target

Collect or infer:

- repository full name: `OWNER/REPO`
- description
- visibility: `private` by default unless user asks for `public`
- whether to create a new GitHub repo or bind an existing one
- remote name: `origin` by default

If the local repo already has a GitHub remote, prefer that repo and ask only if the user wants to switch. If there is no remote, create or bind the target repo before pushing.

Completion criterion: local repo and GitHub repo identity are aligned.

### 4. Run the bootstrap script

Use `scripts/init_matt_engineering_discipline.py` from this skill. Prefer dry-run first:

```bash
python3 /path/to/init-matt-engineering-discipline/scripts/init_matt_engineering_discipline.py --dry-run
```

Then run for real with explicit repo values:

```bash
python3 /path/to/init-matt-engineering-discipline/scripts/init_matt_engineering_discipline.py \
  --repo OWNER/REPO \
  --description "..." \
  --visibility private \
  --create-repo \
  --yes
```

The script is intentionally idempotent. It writes missing repo assets, installs Matt skills when absent, installs bundled runtime skills such as `worktree-agent-coordination` under `.agents/skills/`, configures labels and milestone, optionally creates a GitHub Project and branch ruleset, commits the governance baseline, and pushes it.

By default, consumer repos do not receive local skill source under `skills/`. Use `--include-local-skill-source` only when the target repo is itself meant to author and maintain project-local skills.

Completion criterion: the script finishes or reports the exact blocked operation and the command/user action needed to resume.

### 4.1 Keep the scaffold domain-neutral

The generated baseline may require Chinese-first communication, GitHub governance, and worktree discipline. It must not write business-domain assumptions into the target repo.

Allowed:

- Chinese-first documentation and prompt preferences
- generic GitHub labels for triage, type, area, priority, size, and risk
- generic `CONTEXT.md` placeholders for project language
- worktree/branch/Codex task coordination rules

Not allowed:

- domain-specific area labels unless the user explicitly asks
- legal, finance, medical, ERP, AI-product, or other business assumptions
- README claims about what the product does beyond the repository name
- issue template fields that only make sense for one domain

### 5. Verify GitHub governance

After the script:

- Confirm `git remote -v` points at the intended GitHub repo.
- Confirm labels exist.
- Confirm issue templates and PR template exist.
- Confirm CI workflow exists.
- Confirm the governance issue exists.
- If `--apply-ruleset` was used, confirm the default branch cannot be changed without PR checks/review.

Completion criterion: the repo can accept work through issue -> execution workspace -> branch/worktree -> PR -> CI -> review -> merge -> release.

## What the script creates

Local repo assets:

- `AGENTS.md`
- `CONTEXT.md`
- `CONTRIBUTING.md`
- `CODEOWNERS`
- `README.md` if missing
- `docs/agents/*`
- `docs/adr/.gitkeep`
- `.github/ISSUE_TEMPLATE/*.yml`
- `.github/pull_request_template.md`
- `.github/workflows/ci.yml`
- `.agents/skills/*` and `skills-lock.json` through `npx skills@latest add mattpocock/skills` when absent
- `.agents/skills/worktree-agent-coordination` from this scaffold's bundled local skills
- optionally `skills/productivity/worktree-agent-coordination` only when `--include-local-skill-source` is set

GitHub assets:

- repo remote
- triage/type/area/priority/size/risk labels
- first milestone: `v0.1-project-governance`
- optional GitHub Project
- optional default-branch ruleset
- initial governance issue

## GitHub details

Read `references/github-governance.md` when the user asks what each GitHub entity means, wants to adjust labels/templates/rules, or needs a manual fallback for permissions.

## Safety rules

- Never ask for GitHub tokens in chat. Use `gh auth login`.
- Never overwrite non-empty user files silently. The script writes missing files and can overwrite only with `--force`.
- Never push without a commit summary and explicit user intent or `--yes`.
- Treat branch rulesets, Projects, and org-owned repos as permission-sensitive. Try them only when requested; report failures cleanly.
- Keep Chinese-first project assets, but preserve code identifiers, commands, API names, file paths, and external protocol names in English.
- Keep the scaffold domain-neutral. If the user wants domain-specific labels or docs, treat that as target-repo customization after initialization.
