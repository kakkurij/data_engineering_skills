# SDD Data Product Templates

These templates are used by the spec-driven-data skill to scaffold a data product's specification.
Fill in the `{{PLACEHOLDER}}` values from the interview and from what you read in the repo.
All spec files for a product live in `specs/{{PRODUCT}}/`.

---

## Template: requirements.md

```markdown
# requirements.md
> {{PRODUCT_NAME}} — Version {{VERSION}} — {{DATE}}

## Overview
{{ONE_PARAGRAPH_DESCRIPTION — the decision or question this product supports}}

## Actors
{{#each ACTORS}}
- **{{name}}**: {{description}}
{{/each}}

## Sources
| Source | System | Access | Owner |
|---|---|---|---|
{{#each SOURCES}}
| {{name}} | {{system}} | {{api / database / files}} | {{owner}} |
{{/each}}

## Functional Requirements

{{#each FEATURE_GROUPS}}
### {{group_name}}
{{#each requirements}}
- **REQ-{{id}}**: {{actor_or_system}} shall {{action}}.
  - _Acceptance_: {{check — dbt test, SQL against DuckDB, dlt load check or data app check}}
{{/each}}
{{/each}}

## Metrics Glossary
Every metric shown anywhere in this product is defined here, once.

{{#each METRICS}}
- **METRIC-{{id}}**: `{{metric_name}}` — {{business_description}}
  - _Formula_: {{formula}}
  - _Grain_: {{grain — the level it is computed at, e.g. per order line, per customer per day}}
  - _Filters_: {{filters — inclusions and exclusions}}
  - _Owner_: {{owner}}
  - _Status_: {{agreed | draft}}
{{/each}}

## Non-Functional Requirements
{{#each NFR}}
- **NFR-{{id}}**: {{description}}
  - _Measurement_: {{how_to_measure}}
{{/each}}

<!-- Always cover: freshness, reconciliation/completeness, app interaction latency,
     retention/history, personal data handling. -->

## Out of Scope ({{VERSION}})
{{#each OUT_OF_SCOPE}}
- {{item}}
{{/each}}

## Changelog
| Version | Date | Change |
|---|---|---|
| {{VERSION}} | {{DATE}} | Initial spec |
```

---

## Template: design.md

```markdown
# design.md
> {{PRODUCT_NAME}} — Version {{VERSION}} — {{DATE}}

## Overview
{{ARCHITECTURE_DESCRIPTION}}

## Lineage
```mermaid
flowchart LR
  {{SOURCE}} --> {{RAW_TABLE}} --> {{STG_MODEL}} --> {{MART_MODEL}} --> {{EXPOSURE}}
```

## Sources (dlt)

| Pipeline | Resource | Write disposition | Primary key | Incremental cursor | Schema contract | REQ |
|---|---|---|---|---|---|---|
{{#each RESOURCES}}
| {{pipeline}} | {{resource}} | {{append / replace / merge}} | {{primary_key}} | {{cursor or "full load: reason"}} | {{evolve / freeze / discard_row / discard_value}} | {{req_ref}} |
{{/each}}

**Raw dataset (DuckDB schema)**: {{dataset_name}}

## Models (dbt)

{{#each MODELS}}
### {{model_name}}
- **Layer**: {{staging / intermediate / mart}}
- **Grain**: {{one sentence — what one row represents}}
- **Unique key**: {{columns}}
- **Materialization**: {{view / table / incremental (strategy)}}
- **Built from**: {{refs and sources}}
- **Tests**: {{unique, not_null, relationships, accepted_values, custom}}
- **REQ / METRIC**: {{refs}}

| Column | Type | Description | Notes |
|---|---|---|---|
{{#each columns}}
| {{name}} | {{type}} | {{description}} | {{notes — PII, METRIC-xxx}} |
{{/each}}
{{/each}}

## Metric Implementations

| METRIC | Implemented in | Also computed in app? | Parity check |
|---|---|---|---|
{{#each METRICS}}
| METRIC-{{id}} | {{model.column or SQL definition}} | {{yes / no}} | {{check or "n/a"}} |
{{/each}}

## Data Apps

{{#each APPS}}
### {{app_name}}
- **dbt exposure**: `{{exposure_name}}` (type: application, owner: {{owner}})
- **Reads marts**: {{marts}}
- **Payload**: {{format}} — budget {{max rows / MB shipped to the browser}}
- **Views**: {{views}}
- **Filters & interactions**: {{filters, drill-downs, cross-filters}}
- **Metrics shown**: {{METRIC refs}}
- **Interaction budget**: {{e.g. filter < 100 ms p95}}
- **REQ**: {{refs}}
{{/each}}

## Orchestration

| Job | Runs | Schedule | Depends on | Retry | Backfill |
|---|---|---|---|---|---|
{{#each JOBS}}
| {{job}} | {{dlt pipeline / dbt selector}} | {{schedule}} | {{dependencies}} | {{retry policy}} | {{how history is rebuilt}} |
{{/each}}

### DuckDB access
{{How the job writes and how the data app reads without conflicting — one read-write process per file}}

## Data Quality & Monitoring
{{#each CHECKS}}
- {{check}} — {{where it runs}} — {{what happens on failure}} — {{NFR ref}}
{{/each}}

## Security & Personal Data
{{Which columns are personal data, where they are masked or dropped, who can see which app}}

## File Structure
```
{{PROJECT_ROOT}}/
{{FILE_TREE — pipelines/, models/staging/{{product}}/, models/marts/{{product}}/, apps/, specs/{{product}}/}}
```

## Open Questions
{{#each OPEN_QUESTIONS}}
- [ ] {{question}}
{{/each}}

## Changelog
| Version | Date | Change |
|---|---|---|
| {{VERSION}} | {{DATE}} | Initial design |
```

---

## Template: tasks.md

```markdown
# tasks.md
> {{PRODUCT_NAME}} — Version {{VERSION}} — {{DATE}}

## Legend
- [ ] Not started
- [~] In progress
- [x] Complete
- [!] Blocked — reason noted inline

---

{{#each PHASES}}
## Phase {{phase_number}}: {{phase_name}}
*Goal*: {{phase_goal}}

{{#each tasks}}
- [ ] **TASK-{{id}}** [{{REQ/METRIC/NFR refs}}]: {{description}}
  - _Output_: {{expected_output — one resource, model, metric, app view or job}}
  - _Verify_: {{command or check — e.g. `dbt build --select stg_orders`, SQL uniqueness query, dlt load check}}
{{/each}}

{{/each}}

<!-- Typical phases: 1 Ingestion (dlt) → 2 Staging → 3 Marts & metrics →
     4 Data app & exposure → 5 Orchestration, monitoring & backfill -->

---

## Completed Tasks Archive
<!-- Move [x] tasks here at the end of each phase -->
```

---

## The Universal AI Instruction Block

This block goes into every AI agent config file in the repo, once. It covers every data product under `specs/`.

```
═══════════════════════════════════════════════════════════
SPEC DRIVEN DEVELOPMENT — DATA PRODUCT CONSTITUTION
Project: {{PROJECT_NAME}}
Version: {{SPEC_VERSION}}
═══════════════════════════════════════════════════════════

Data products in this repo are specified in specs/<product>/:

  requirements.md  — What the product must deliver,
                     including the Metrics Glossary
  design.md        — Sources, models, metrics, apps, jobs
  tasks.md         — The ordered implementation plan

MANDATORY BEFORE ANY ACTION:
  0. Identify the data product. If specs/<product>/CONTEXT.md
     exists, read it first — it has session state
  1. Read requirements.md in full
  2. Read design.md in full
  3. Read tasks.md — identify the next incomplete [ ] task

HARD CONSTRAINTS:
  ✗ Never implement requirements not in requirements.md
  ✗ Never add or change a source, model, column, key or
    grain without updating design.md first
  ✗ Never define or change a metric except through its
    METRIC entry in requirements.md
  ✗ Never let a data app read raw or staging tables
  ✗ Never mark a task [x] without running its verification
  ✗ Never guess when a requirement is ambiguous — ask instead

AFTER COMPLETING A TASK:
  1. Run the verification step listed in tasks.md
  2. Mark the task [x] in tasks.md
  3. Report what was done and which REQ/METRIC/NFR it satisfies

DIVERGENCE PROTOCOL:
  If implementation must deviate from design.md:
    → Stop immediately
    → Describe the conflict clearly
    → Wait for explicit user approval
    → Update design.md BEFORE writing code
═══════════════════════════════════════════════════════════
```

### Stack commands (append after the block in every config file)

```
STACK COMMANDS:
  Build and test a model:   dbt build --select {{model}}
  Downstream impact:        dbt ls --select {{model}}+
  Source freshness:         dbt source freshness
  Run a dlt pipeline:       {{DLT_RUN_COMMAND}}
  Run a job via the runner: {{RUNNER_COMMAND}}
  Query DuckDB:             {{DUCKDB_QUERY_COMMAND}}
```

Fill the `{{...COMMAND}}` values from the repo (README, Makefile, runner CLI help) or ask. Never invent them.

---

## Template: CONTEXT.md

```markdown
# CONTEXT.md
> {{PRODUCT_NAME}} — Live session journal
> Last updated: {{DATE}} — Session {{SESSION_NUMBER}}

## ⚡ Resume from here

**Active task:** {{CURRENT_TASK_ID}} — {{CURRENT_TASK_DESCRIPTION}}
**Phase:** {{CURRENT_PHASE}}
**Status:** {{in progress | blocked | ready for next task}}
**Blocker (if any):** {{BLOCKER_DESCRIPTION or none}}

> On session start: read this file first, then requirements.md,
> design.md, and tasks.md in this folder. Do not ask what to work
> on — resume the active task above unless the user says otherwise.

---

## Session log

| # | Date | What was done | Files changed |
|---|---|---|---|
| {{SESSION_NUMBER}} | {{DATE}} | {{SUMMARY_ONE_LINE}} | {{FILES}} |

*(most recent first)*

---

## Key decisions

| Decision | Rationale | Session |
|---|---|---|
| {{DECISION}} | {{WHY}} | {{SESSION_NUMBER}} |

---

## Open questions

{{#each OPEN_QUESTIONS}}
- [ ] {{question}}
{{/each}}

---

## Divergences from design.md

{{#each DIVERGENCES}}
- {{location}}: {{what differs}} — {{resolution_status}}
{{/each}}
```
