---
name: setup-codex-skills
description: Inspect, compare, install, update, or restore Codex skills and plugins from the AtomFlow catalog, official Lark suite, and Codex marketplaces. Use when setting up a new Codex machine, reproducing another installation, listing missing capabilities, choosing skill bundles, or adding one skill or plugin without using a fixed bootstrap script.
---

# Set up Codex skills

Treat installation as an interactive environment-management task. Adapt the
selection to the user's work instead of installing a hard-coded bundle.

## Workflow

1. Read [references/catalog.md](references/catalog.md).
2. Inspect before changing anything:
   - confirm `codex`, `node`, and `npx` availability;
   - list discoverable AtomFlow skills with
     `npx skills add AtomFlow-AI/skills --list --full-depth`;
   - inspect installed and available plugins with
     `codex plugin list --available --json`;
   - inspect `${CODEX_HOME:-$HOME/.codex}/skills` and `$HOME/.agents/skills`
     when those directories exist.
3. Summarize what is present, missing, duplicated, or supplied by Codex itself.
4. Ask the user to choose among relevant suites or individual capabilities when
   their request does not already specify the selection. Recommend a small set
   based on their work, but keep every item independently selectable.
5. Show the exact sources and planned mutations before installation. Never copy
   plugin caches, credentials, OAuth sessions, API keys, or unknown local skill
   directories.
6. Install the approved selection with the commands in the catalog. Use the
   current installer output rather than assuming names or marketplace IDs remain
   unchanged.
7. Re-list the environment, report failures per item, and tell the user whether
   Codex must restart or an external tool must authenticate.

## Selection rules

- Prefer installing a named skill over an entire suite when the user needs one
  capability.
- Offer suite installation when the skills have cross-references or shared
  runtime dependencies, especially Lark.
- Treat `.system`, `openai-primary-runtime`, and `openai-bundled` skills as
  Codex-managed. Diagnose their absence through Codex installation or plugin
  state; do not vendor them into AtomFlow.
- Install marketplace plugins through `codex plugin add`, never by copying their
  cache directories.
- Install repository skills through `npx skills add`. Include `--full-depth`
  because the AtomFlow repository contains packaged and standalone layouts.
- Do not claim a local-only skill is reproducible until it has a reviewed
  repository source. Offer to publish it separately when appropriate.
- Do not persist secrets. Authentication is a separate, user-controlled step.

## Flexible requests

Interpret requests such as these directly:

- “Restore my usual Codex setup” → inspect, compare, then propose groups.
- “Only install Web development skills” → list Web-related choices and install
  the user's selection.
- “Set up Lark” → install the Lark suite, check `lark-cli`, and guide login.
- “Make this machine match another one” → obtain a redacted inventory from the
  source machine, compare names and sources, then reconcile approved differences.
- “What am I missing?” → audit only; do not mutate unless asked.
