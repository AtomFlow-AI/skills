# AtomFlow Skills

Shared Agent Skills for AtomFlow-AI. This repository gives every contributor a
personal publishing area and provides a reviewed shared catalog for skills the
team recommends broadly.

## Repository layout

```text
skills/
├── shared/
│   ├── <skill-name>/SKILL.md
│   └── <package-name>/<skill-name>/SKILL.md
└── <github-username>/
    ├── <skill-name>/SKILL.md
    └── <package-name>/<skill-name>/SKILL.md
```

- `skills/shared/`: reviewed, reusable skills recommended to the whole team.
- `skills/<github-username>/`: contributor-owned skills that may be experimental,
  specialized, or awaiting wider adoption.
- The optional `<package-name>/` level groups skills that are maintained or
  distributed as one upstream suite. Individual skill names remain globally
  unique and independently installable.
- Skill names are globally unique across the repository. Promote a personal skill
  by moving it into `shared`, not by copying it.

Both layouts are discovered by the standard `skills` CLI without requiring
recursive-search flags.

## Install

List every available skill:

```bash
npx skills add AtomFlow-AI/skills --list
```

Install one skill globally for Codex:

```bash
npx skills add AtomFlow-AI/skills \
  --skill rdkit-svg-emphasis \
  --global --agent codex --yes
```

Install one skill globally for Claude Code:

```bash
npx skills add AtomFlow-AI/skills \
  --skill rdkit-svg-emphasis \
  --global --agent claude-code --yes
```

Install interactively and choose the target agent:

```bash
npx skills add AtomFlow-AI/skills
```

Use a skill once without installing it:

```bash
npx skills use AtomFlow-AI/skills --skill rdkit-svg-emphasis
```

## Publish a personal skill

1. Create `skills/<your-github-username>/<skill-name>/`, or use
   `skills/<your-github-username>/<package-name>/<skill-name>/` for a suite.
2. Add a valid `SKILL.md`; keep scripts, references, and assets inside that skill.
3. Run `python scripts/validate_skills.py`.
4. Open a pull request and explain the skill's purpose, dependencies, and tests.

See [CONTRIBUTING.md](CONTRIBUTING.md) for naming, ownership, and shared-promotion
rules.

## Security

Skills can execute instructions and bundled scripts. Review every dependency,
command, network action, and credential boundary before merging or installing.
Never commit secrets, tokens, private keys, `.env` files, or proprietary data.

