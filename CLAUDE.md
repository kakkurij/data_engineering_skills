# CLAUDE.md

This repo holds two Claude skills for spec-driven development of a data platform.
It is a skills repo, not an SDD project — there is no requirements.md here.

| Skill | Path | For |
|---|---|---|
| `spec-driven-data` | `skills/spec-driven-data/` | Data products: dlt sources, dbt models, metrics, data apps, orchestrator jobs |
| `spec-driven-sw` | `skills/spec-driven-sw/` | Platform software: runner, orchestrator, API, React UI, WASM engine |

## Rules for changing the skills

- Each skill folder must be self-contained — it is installed on its own. Shared reference files
  (`sdd-curriculum.md`, `capabilities-and-cross-ai.md`) are copied into both; change both copies.
- Skill `name` fields use lowercase letters, digits and hyphens only.
- Keep the two descriptions pointing at each other, so the right skill triggers.
- Both skills write specs to `specs/<name>/` and their config blocks must coexist
  (`PLATFORM CONSTITUTION` and `DATA PRODUCT CONSTITUTION`).

## Tests

Run after every skill change:

```bash
PYTHONUTF8=1 python tests/spec-driven-sw/phase2a/run_assertions.py
PYTHONUTF8=1 python tests/spec-driven-data/phase2a/run_assertions.py
PYTHONUTF8=1 python tests/spec-driven-sw/phase2c/check_outputs.py
```

If a change adds behavior, add an assertion for it. Behavioral (2B) and generation (2C) runs are
started by pasting the matching `KICKOFF.md` into Claude Code.
