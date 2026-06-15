# codex-skills

Cross-platform agent capabilities packaged as installable tools plus Codex marketplace adapters.

## Included

- `plugins/douyin-content-capture/`
  - `python-package/`: installable CLI package
  - `skills/douyin-content-capture/`: Codex skill adapter
  - `.codex-plugin/plugin.json`: Codex plugin manifest

## Install the CLI

With `pipx`:

```bash
pipx install "git+https://github.com/suengx/codex-skills.git#subdirectory=plugins/douyin-content-capture/python-package[transcribe]"
```

With `uv`:

```bash
uv tool install "git+https://github.com/suengx/codex-skills.git#subdirectory=plugins/douyin-content-capture/python-package[transcribe]"
```

Then run:

```bash
douyin-capture doctor --json
```

Install without `[transcribe]` when you only need metadata resolution and download helpers.

## Install the Codex marketplace

```bash
codex plugin marketplace add suengx/codex-skills
```

The marketplace exposes the `douyin-content-capture` plugin from this repository.

## Repository design

- Core logic is shipped as a normal Python package with a stable CLI contract.
- Codex-specific manifests and skill instructions live in the plugin adapter layer.
- The marketplace file is committed so the repository itself can be used as the install source.
