# codex-skills

Cross-platform agent capabilities packaged as installable tools plus Codex marketplace adapters.

## Included

- `plugins/douyin-content-capture/`
  - `python-package/`: installable CLI package
  - `skills/douyin-content-capture/`: Codex skill adapter
  - `.codex-plugin/plugin.json`: Codex plugin manifest

## Install the CLI

Verified remote install for the full transcript-capable build:

```bash
python -m pip install "douyin-capture[transcribe] @ git+https://github.com/suengx/codex-skills.git@v1.0.0#subdirectory=plugins/douyin-content-capture/python-package"
douyin-capture doctor --json
```

For metadata-only usage, omit `[transcribe]`:

```bash
python -m pip install "douyin-capture @ git+https://github.com/suengx/codex-skills.git@v1.0.0#subdirectory=plugins/douyin-content-capture/python-package"
```

Tools such as `pipx` or `uv tool` can generally reuse the same PEP 508 direct URL spec.

## Install the Codex marketplace

```bash
codex plugin marketplace add suengx/codex-skills
```

The marketplace exposes the `douyin-content-capture` plugin from this repository.

## Repository design

- Core logic is shipped as a normal Python package with a stable CLI contract.
- Codex-specific manifests and skill instructions live in the plugin adapter layer.
- The marketplace file is committed so the repository itself can be used as the install source.
