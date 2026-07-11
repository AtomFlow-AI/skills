# Bootstrap Codex skills

Use the repository bootstrap script to reproduce the supported skill setup on a
new Codex installation.

```bash
git clone https://github.com/AtomFlow-AI/skills.git
cd skills
bash scripts/bootstrap_codex_skills.sh
```

Preview every command without changing the machine:

```bash
bash scripts/bootstrap_codex_skills.sh --dry-run
```

## What is installed

The default profile installs:

1. every discoverable skill in `AtomFlow-AI/skills` for Codex;
2. the official `larksuite/cli` skill suite;
3. these optional Codex Marketplace plugins:
   - `github@openai-curated`
   - `gmail@openai-curated`
   - `build-web-apps@openai-curated`
   - `build-web-data-visualization@openai-curated`
   - `zotero@openai-curated`

Use `--skip-lark` or `--skip-plugins` when a machine does not need those
capabilities.

## What is deliberately not copied

- Codex `.system` skills are bundled with Codex.
- `openai-primary-runtime` and `openai-bundled` skills are supplied by the
  installed Codex version.
- Plugin cache directories are generated artifacts and may contain multiple
  stale versions.
- Local skills with no reviewed upstream source or repository entry are not
  silently copied into this public repository.
- Credentials, OAuth sessions, API keys, and Lark login state are never synced.

The Lark skills depend on `lark-cli`. Install that CLI separately if it is not
already available, then authenticate on the new machine:

```bash
lark-cli auth login
```

Restart Codex after bootstrap so the next session discovers newly installed
skills and plugins.

## Maintaining the setup

Publish a personal skill under `skills/<github-username>/`, or under a package
directory when it belongs to a suite. Once merged, rerunning the same bootstrap
command installs the updated catalog on another Codex machine.

