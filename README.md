# data_engineering_skills

Two Claude skills for spec-driven development of a data platform built on
**dlt + dbt + DuckDB**, a custom runner and orchestrator, and **React + API + WASM** data apps.

Both skills interview you one question at a time, then write `requirements.md`, `design.md`,
`tasks.md` and `CONTEXT.md` into `specs/<name>/`, plus matching config files for every AI coding
tool you use (`CLAUDE.md`, `.cursorrules`, `.windsurfrules`, `.github/copilot-instructions.md`,
`.aider.conf.yml`), so every agent works from the same plan.

| Skill | Use it for | Example prompts |
|---|---|---|
| [`spec-driven-data`](skills/spec-driven-data/SKILL.md) | Data products: sources, models, metrics, data apps, jobs | "new data product for sales performance", "add Stripe as a source", "document my dbt project" |
| [`spec-driven-sw`](skills/spec-driven-sw/SKILL.md) | The platform itself: runner, orchestrator, API, React UI, WASM engine | "spec a retry policy for the orchestrator", "new WASM cross-filter engine" |

Each skill hands off to the other when a request belongs there.

---

## What `spec-driven-data` adds

- **Fixed stack** — never asks which tools to use; asks about purpose, sources, freshness and metrics instead
- **Metrics glossary** — every metric defined once (`METRIC-xxx`: formula, grain, filters, owner, status), and the
  agents are not allowed to define metrics anywhere else
- **Data-shaped design** — dlt write disposition, keys, incremental cursor and schema contract per resource;
  grain, key, materialization and tests per dbt model; data apps as dbt exposures with payload and
  interaction budgets; orchestrator jobs with retry and backfill; an explicit DuckDB read/write pattern
- **Checkable acceptance** — every requirement and task is verified with `dbt build`, SQL, dlt or an app check
- **Retrofit from the real system** — reads the dbt manifest, dlt code and DuckDB `information_schema`

## What `spec-driven-sw` adds

- Interview and examples for the platform components
- **Component Contracts** in design.md — UI ↔ API, API ↔ WASM, orchestrator ↔ runner, DuckDB access
- **WASM boundary** — exports, data format, memory ownership, thread
- **Performance budgets** with data sizes for interactive paths

---

## Installation

### As a Claude Code plugin (recommended)

```bash
claude plugin marketplace add kakkurij/data_engineering_skills
claude plugin install data-engineering-skills@data-engineering-skills
```

Or inside a session:

```
/plugin marketplace add kakkurij/data_engineering_skills
/plugin install data-engineering-skills@data-engineering-skills
```

Update later with `claude plugin marketplace update data-engineering-skills`. The skills are then
available as `/data-engineering-skills:spec-driven-data` and `/data-engineering-skills:spec-driven-sw`,
and trigger automatically from their descriptions.

### Manually

Copy the skill folders into your Claude skills directory:

```bash
git clone git@github.com:kakkurij/data_engineering_skills.git
cp -r data_engineering_skills/skills/spec-driven-data ~/.claude/skills/
cp -r data_engineering_skills/skills/spec-driven-sw   ~/.claude/skills/
```

For Claude.ai / the desktop app, zip a skill folder and install it from Settings → Skills.

---

## Repository layout

```
.claude-plugin/                          ← plugin + marketplace manifests
skills/
├── spec-driven-data/
│   ├── SKILL.md
│   └── references/
│       ├── templates.md                 ← spec, UIB and CONTEXT.md templates
│       ├── data-stack-patterns.md       ← dlt, dbt-duckdb, metrics, data apps, orchestration
│       ├── capabilities-and-cross-ai.md ← per-agent config wrappers
│       └── sdd-curriculum.md            ← SDD teaching guide
└── spec-driven-sw/
    ├── SKILL.md
    └── references/
        ├── templates.md
        ├── capabilities-and-cross-ai.md
        └── sdd-curriculum.md
tests/
├── spec-driven-data/phase2a/            ← static assertions (99)
└── spec-driven-sw/
    ├── phase2a/                         ← static assertions (67)
    ├── phase2b/                         ← behavioral tests (manual, Claude Code)
    └── phase2c/                         ← generation quality + committed fixtures (53)
```

## Tests

```bash
PYTHONUTF8=1 python tests/spec-driven-sw/phase2a/run_assertions.py
PYTHONUTF8=1 python tests/spec-driven-data/phase2a/run_assertions.py
PYTHONUTF8=1 python tests/spec-driven-sw/phase2c/check_outputs.py
```

CI runs all three on every push and PR to `master`. Phase 2B (behavioral) and Phase 2C fixture
regeneration run in Claude Code by pasting the matching `KICKOFF.md`.

---

## Credits

Based on [spec-driven-development](https://github.com/FredAntB/Spec-Driven-Development) by
Frederick Antonio Balderrama Mendoza, MIT licensed. See [LICENSE](LICENSE).
