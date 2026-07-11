# Installation catalog

Use current list output to verify every identifier before installing it.

## AtomFlow repository

List:

```bash
npx skills add AtomFlow-AI/skills --list --full-depth
```

Install one:

```bash
npx skills add AtomFlow-AI/skills --skill <skill-name> \
  --global --agent codex --yes --full-depth
```

Install multiple by repeating `--skill` only if the installed `skills` CLI help
confirms that form. Otherwise install them one at a time so failures are isolated.

## Official Lark suite

List or install through `larksuite/cli`:

```bash
npx skills add larksuite/cli --list --full-depth
npx skills add larksuite/cli --skill <lark-skill> \
  --global --agent codex --yes --full-depth
```

For the full suite, omit `--skill` after confirming the selection with the user.
The skills require `lark-cli`; check it with `lark-cli doctor` and authenticate
with `lark-cli auth login`. Never copy authentication state between machines.

## Codex Marketplace plugins

Discover current identifiers:

```bash
codex plugin list --available --json
```

Install one selected plugin:

```bash
codex plugin add <plugin-id>@<marketplace>
```

Common optional choices include GitHub, Gmail, `build-web-apps`,
`build-web-data-visualization`, and Zotero. Treat these as suggestions, not a
default bundle. Some plugins require authentication during or after installation.

## Codex-managed capabilities

Do not copy these from another machine:

- `.system` skills such as skill creation and installation helpers;
- primary-runtime document, spreadsheet, presentation, PDF, and template skills;
- bundled browser, computer-use, Sites, LaTeX, and visualization skills;
- any directory under the plugin cache.

Use `codex update`, `codex doctor`, and marketplace inspection to diagnose these
capabilities on a new installation.

## Unmanaged local skills

For a skill found only in a local directory:

1. inspect its metadata and provenance;
2. locate its upstream repository and license;
3. install from that reviewed upstream, or publish it to the contributor's
   AtomFlow area in a separate change;
4. never silently copy it into this public repository.
