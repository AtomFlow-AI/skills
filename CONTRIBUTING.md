# Contributing

## Personal skills

Publish under `skills/<github-username>/<skill-name>/`. The username directory
communicates ownership; maintainers may request changes for security, naming, or
repository-wide compatibility.

Each skill must:

- use a globally unique lowercase hyphenated name;
- contain `SKILL.md` with YAML `name` and `description`;
- keep the folder name equal to the frontmatter `name`;
- state what the skill does and when it should trigger;
- keep scripts and assets self-contained;
- document runtime dependencies and validate bundled scripts;
- avoid secrets, destructive defaults, hidden network transmission, and unrelated
  repository documentation.

## Shared skills

`skills/shared/` is curated. Promote a skill when multiple contributors have used
it successfully and agree it should be a team default.

A promotion pull request should:

1. move the existing personal skill instead of duplicating it;
2. preserve history where possible;
3. include evidence from at least one realistic usage or smoke test;
4. remove contributor-specific paths, assumptions, and credentials;
5. identify maintainers in the pull request description.

## Validation

Run:

```bash
python scripts/validate_skills.py
npx skills add . --list
```

The first command enforces repository policy. The second confirms that the
standard installer discovers the catalog.

## Pull requests

Keep one skill or one catalog-level improvement per pull request. Describe:

- intended trigger and users;
- files or systems the skill may modify;
- external tools, packages, or services it requires;
- validation performed;
- whether the skill is personal or proposed for `shared`.

