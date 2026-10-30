---
name: spec-driven-data
version: 1.0.0
description: >
  Spec Driven Development for data products on a dlt + dbt + DuckDB platform with a custom runner/orchestrator and React/WASM data apps. Scaffolds per-product requirements.md (with a metrics glossary), design.md (dlt sources, dbt models, data apps, orchestrator jobs), tasks.md, CONTEXT.md and cross-AI config files (CLAUDE.md, .cursorrules, .windsurfrules, .github/copilot-instructions.md). Triggers: 'data product', 'new source', 'ingest', 'dlt pipeline', 'dbt model', 'mart', 'metric definition', 'KPI', 'data app', 'report', 'dashboard', 'spec', 'requirements', 'SDD', 'spec driven', 'plan before building'. Retrofit triggers: 'document my dbt project', 'document my pipelines', 'describe my data model', 'no specs yet', 'I already have models'. Do NOT use for building the platform software itself (runner, orchestrator, API, React UI, WASM engine) — use spec-driven-sw for that.
---

# Spec Driven Development — Data Products

This skill specs and builds **data products** on the user's data platform. A data product is the
full path from source to screen:

```
source system → dlt pipeline → DuckDB (raw) → dbt staging → dbt marts → data app (React + API + WASM)
                       ↑ scheduled and run by the custom orchestrator and runner ↑
```

For each data product it creates, in `specs/<product>/`:
- `requirements.md` — what the product must deliver, including the **metrics glossary**
- `design.md` — sources, models, metrics, data apps and jobs that deliver it
- `tasks.md` — atomic, ordered implementation steps
- `CONTEXT.md` — the session journal for this product

And, once per repo, AI agent configuration files for Claude Code, Cursor, Windsurf, GitHub Copilot, and Aider.

**Reference files** (read when needed):
- `references/templates.md` — spec file, UIB and CONTEXT.md templates
- `references/data-stack-patterns.md` — dlt, dbt-on-DuckDB, metrics, data app and orchestration patterns
- `references/capabilities-and-cross-ai.md` — Claude Code capabilities, per-agent config templates
- `references/sdd-curriculum.md` — SDD teaching curriculum, newbie to hero

---

## When to Read Reference Files

| Situation | Read |
|---|---|
| You need template content to generate files | `templates.md` |
| Designing sources, models, metrics, apps or jobs | `data-stack-patterns.md` |
| User wants cross-AI config files | `capabilities-and-cross-ai.md` Part 2 |
| User is new to SDD and needs explanation | `sdd-curriculum.md` Levels 1–3 |

---

## The Stack Is Fixed

Never ask which tools to use. The platform is:

| Layer | Tool |
|---|---|
| Extract & load | dlt |
| Storage | DuckDB |
| Transform | dbt (dbt-duckdb adapter) |
| Run & schedule | custom runner and orchestrator |
| Consume | data apps — custom React UI + API + WASM engine for fast interactions |

If a request needs something outside this stack (a new storage engine, a change to the runner,
a new data app capability in the UI or WASM engine), that is **platform work**: say so and hand off
to `spec-driven-sw`. Record the dependency in the product's design.md Open Questions.

**Before the interview**, look at the repo if you have access: `dbt_project.yml`, `models/`,
`sources` YAML, dlt pipeline code, existing `specs/`, and existing config files (`CLAUDE.md` etc.).
Use what you find — don't ask the user for things the repo already answers.

---

## Workflow: New Data Product

### Step 1: Interview the User

**Conversational rule (non-negotiable):** Ask exactly ONE question, wait for the answer, then ask the next. Never present questions as a numbered list or bullet list — that feels like a form, not a conversation.

**The four required answers before any spec file is generated:**
1. Purpose and users — which decision or question the data app supports, and who uses it
2. Sources — which systems the data comes from, how they are accessed (API, database, files), and who owns each
3. Freshness and volume — how fresh the data must be in the app, and roughly how much data (rows per day, history needed)
4. Metrics — the headline metrics the app shows, and how each is defined (formula, grain, filters)

Sources and freshness are separate required answers because one does not imply the other. "It comes from our Postgres" says nothing about whether the app needs data from five minutes ago or last night. Both must be known independently.

Metrics are required because they are where data products drift most: three agents asked for "revenue" will produce three definitions. If the user can't define a metric yet, record it in the glossary with status `draft` and an Open Question — never invent a formula.

**If the user's opening message already answers some of these**, acknowledge what you know and ask only for what's missing — still one question at a time.

**Optional follow-ups** (ask only when the answers raise real ambiguity):
- "Does any of this data contain personal or sensitive information?"
- "How far back does the history need to go, and will we need to backfill?"
- "What should users be able to do in the app — filter, drill down, compare periods?"
- "What is explicitly out of scope for this first version?"

Example of correct pacing:
> User: "I want to build a sales performance data product"
> Claude: "Happy to help you spec it. Who will use the sales data app, and what decision should it help them make?"
> User: "Sales managers, to see which reps and regions are behind target each week"
> Claude: "Got it. Where does the data come from — which systems, and who owns them?"
> User: "Orders from our Postgres ERP, targets from a Google Sheet the sales ops team maintains"
> Claude: "How fresh does it need to be in the app, and roughly how many orders per day?"
> User: "Daily is fine, about 20k orders a day, two years of history"
> Claude: "Last thing — which metrics are on the screen, and how is each one calculated? For example, is revenue net of returns and discounts?"

Example of partial-answer handling:
> User: "I need a data app showing churn from our Stripe data"
> Claude: "Good start — Stripe noted as the source. Who uses the churn app, and what will they decide with it?"
> User: "The customer success team, to pick accounts to call"
> Claude: "How fresh does it need to be — is yesterday's data good enough?"
> User: "Yes, daily"
> Claude: "How exactly do you define churn — cancelled subscriptions, or no payment for some period? And per customer or per subscription?"
> *(answers partially given — ask for each missing part one at a time, never bundle them)*

### Generation Gate (enforced between Step 1 and Step 2)

**HARD RULE: No spec file may be generated until all four interview answers are in hand.**

This applies to `requirements.md`, `design.md`, `tasks.md`, `CONTEXT.md`, and to dlt or dbt code. There are no exceptions, including when:
- The user says "create a sales data product" (a domain name is not a product description)
- The user says "write a dbt model for revenue" (a concrete deliverable name is not permission to skip the interview)
- The user names a source but not the freshness need (source ≠ freshness — both are required separately)
- The user names metrics without definitions (ask how each is calculated, or mark it `draft`)

Do not generate placeholder files with `{{UNFILLED}}` tokens. Do not invent metric formulas, sources or SLAs from a domain name.

**Gate check before generating any file:**
```
□ Do I know the purpose and who uses the data app?       → if not, ask first
□ Do I know the sources, how they're accessed, owners?    → if not, ask first
□ Do I know the freshness need and rough data volume?     → if not, ask first
□ Do I know the headline metrics and their definitions?  → if not, ask first
Only when all four are ✓ → proceed to Step 2
```

---

### Step 2: Generate `requirements.md`

Read `references/templates.md` for the template. Fill in all `{{PLACEHOLDERS}}`.

**Quality rules for requirements.md:**
- Every functional requirement uses "shall" language (REQ-xxx: Actor/system shall verb object)
- Every acceptance criterion is checkable with the stack: a dbt test, a SQL query against DuckDB, a dlt load check, or a data app check. Never "data looks right".
- The **Metrics Glossary** has one entry per metric: METRIC-xxx, formula, grain, filters, owner, status (`agreed` / `draft`)
- NFRs are measurable: freshness ("marts updated by 06:00 daily"), completeness/reconciliation ("order count matches source within 0.1%"), app interaction latency, retention, PII handling
- Out of scope section is non-empty
- IDs are sequential starting at REQ-001, METRIC-001, NFR-001

**Output:** Create `specs/<product>/requirements.md`. Use a short snake_case product name; ask if the repo uses another spec convention.

---

### Step 3: Generate `design.md`

Read `references/templates.md` for the template and `references/data-stack-patterns.md` for the patterns.

**Quality rules for design.md:**
- **Sources (dlt):** every resource has write disposition (append / replace / merge), primary key, incremental cursor (or why full load), and schema contract
- **Models (dbt):** every model has layer (staging / intermediate / mart), **grain** stated in one sentence, unique key, materialization, and tests
- **Metrics:** every METRIC-xxx maps to exactly one implementation (a mart column or a single SQL definition). If the data app computes it client-side in WASM, design.md names the parity check against the dbt implementation
- **Data apps:** each app is a dbt exposure; design.md lists the marts it reads, payload size budget, views, filters/interactions, and which METRICs it shows
- **Jobs:** every orchestrator job lists what it runs (dlt pipeline / dbt selector), schedule, dependencies, retry and backfill behaviour
- **DuckDB access:** state how the job writes and how the app reads without conflicting — DuckDB allows one read-write process per file
- Every REQ maps to at least one source, model, metric, app or job
- Open Questions captures anything undecided — do not guess, ask

**Output:** Create `specs/<product>/design.md`.

---

### Step 4: Generate `tasks.md`

Read `references/templates.md` for the template.

**Quality rules for tasks.md:**
- Tasks follow the data flow: dlt source → staging models → intermediate/mart models → metrics → exposure and data app → orchestrator job → monitoring and backfill
- Every task references at least one REQ, METRIC or NFR **inline on the checkbox line**: `**TASK-{{id}}** [REQ-xxx, METRIC-xxx]`
- Every task has a concrete verification command or check: `dbt build --select <model>`, a SQL check against DuckDB, a dlt load check, a runner command, or a data app check
- Tasks are atomic — one dlt resource, one dbt model, one metric, one app view or one job per task
- Phase goals are stated in plain English

**Output:** Create `specs/<product>/tasks.md`, and `specs/<product>/CONTEXT.md` with the resume block pointing at the first task.

---

### Step 5: AI Agent Configuration Files (once per repo)

Config files are repo-level, not per product. Check whether they already exist.

- **They exist and already contain the `DATA PRODUCT CONSTITUTION` block:** do nothing — the block covers every product under `specs/`.
- **They exist with another block** (e.g. `PLATFORM CONSTITUTION` from `spec-driven-sw`): keep it untouched and add the data block alongside it. Never remove or rewrite the other skill's block.
- **They don't exist:** ask which AI coding tools the user uses (one question), then generate them.

**Always generate:** `CLAUDE.md`. **Based on the user's tools:** `.cursorrules`, `.windsurfrules`, `.github/copilot-instructions.md`, `.aider.conf.yml`. Read `references/capabilities-and-cross-ai.md` Part 2 for the per-agent wrappers and `references/templates.md` for the block itself.

**Quality rules for AI config files:**
- The Universal Instruction Block is IDENTICAL across all files — only agent-specific additions differ
- The stack commands section names the real commands (dbt, dlt, the runner) — read them from the repo or ask; never invent a runner command
- Agent-specific additions are no more than 5 lines

---

## Workflow: Existing Data Product (Retrofit)

Triggered by: "document my dbt project", "document my pipelines", "describe my data model", "no specs yet", "I already have models", or anything implying an existing data product without written specs.

### Retrofit Interview (ask one question at a time, conversationally)

1. "Which data product is this, and what does it deliver today — who uses it?"
2. "Which sources, models and data apps belong to it? (a dbt selector, folder or exposure name is enough)"
3. "Can I read the repo and the DuckDB file? I'll use the dbt manifest, source YAML, dlt pipeline code and information_schema rather than guessing."
4. "Which metrics does it show, and are their definitions written down anywhere?"
5. "What's the next change or feature you're planning? (This determines what tasks.md covers)"

Question 3 matters most — on this stack everything is code or queryable, so a retrofit can be read, not remembered.

### Retrofit Generation Process

**Step 1 — Read the real system** (when access is given)
- `dbt ls --select <selector> --resource-type model source exposure` and `target/manifest.json` for models, sources, exposures, tests
- dlt pipeline code and schemas for write dispositions, keys and incremental cursors
- `information_schema.columns` in DuckDB for actual column types
- Orchestrator job definitions for schedules and dependencies

**Step 2 — Reverse-engineer `requirements.md`**
- Turn what the product does into REQ-xxx statements; flag each inferred one: "I'm inferring REQ-004 from the `fct_orders` tests — is that a real requirement?"
- Build the Metrics Glossary from the mart columns and app definitions; mark every formula you read from code `status: draft` until the user confirms the business definition
- Mark the version `v0-retrofit`

**Step 3 — Reverse-engineer `design.md`**
- Fill sources, models, apps and jobs from what you read
- Anything not read from the system is marked `[TO VERIFY]`; never invent a grain or a key — mark it `[unknown]`

**Step 4 — Generate `tasks.md` for the NEXT phase only**
- Phase 1 is "Spec Verification": confirm grain, keys, metric definitions and freshness against the live system (e.g. a uniqueness query per stated grain)
- Phase 2 covers the planned change from question 5
- No tasks for work already done

### Retrofit Gap Flagging

After generating each file, list every assumption:
> "Please verify:
> - METRIC-002 `net_revenue`: I read `amount - discount` from `fct_orders`; returns are not subtracted — is that the business definition?
> - design.md § Models: grain of `int_customer_days` is [TO VERIFY] — I found no unique test"

In a new product the spec is the truth. In a retrofit, the code and the warehouse are the truth, and the spec must be verified against them.

---

## Workflow: Updating Specs (Change Request)

### Spec Presence Check (run before anything else)

When a request arrives to add a column, a model, a metric or an app view without spec context, do not implement it. Check first:

> "Before I add that to `fct_orders` — which data product does it belong to? If it has a spec under `specs/`, I'll check it's in scope and add it properly. If not, let's create one first."

- **Spec exists, in scope** → update requirements.md first, then design.md, then tasks.md, then implement
- **Spec exists, out of scope** → flag the conflict, ask whether to expand scope formally
- **No spec exists** → route to the Retrofit workflow

### Metric changes

A metric definition change is the highest-impact change on a data platform.
1. Update the METRIC-xxx entry in requirements.md first (bump spec version, note it in the changelog)
2. Find everything downstream: `dbt ls --select <model>+` and the exposures that depend on it
3. If the metric is also computed in the data app (WASM), list the app change and its parity check
4. If other data products reference the same metric, flag them — never fork a metric silently

### Task closing protocol ("update my tasks.md")

When a user asks to mark a task done, follow this exact two-step sequence — never bundle both steps into one message:

**Step 1 — Identify the task first:**
> "Which task did you just finish? Give me the TASK-id or a brief description."

**Step 2 — Divergence check after identification:**
> "Before I mark TASK-007 `[x]` — did its verification pass (`dbt build --select …` or the check listed), and did the implementation match design.md exactly — same grain, keys and columns? If anything drifted, we update design.md first."

**Why the order matters:** the divergence question only makes sense for a specific task.

---

## Session Management — CONTEXT.md

Each data product has its own `specs/<product>/CONTEXT.md`, so parallel work on two products never collides.

It holds a **resume block** (active task, phase, status, blocker), a **session log** (one row per session — summaries, never transcripts), **key decisions** (e.g. "merge on `order_id` because the ERP updates orders for 30 days"), **open questions**, and **divergences** from design.md.

**At the start of any session:**
1. Identify the data product being worked on (ask if unclear)
2. Read its CONTEXT.md first — before requirements.md, design.md, or tasks.md
3. Announce: "Session [N] resuming on [product]. Last worked on: [task]. Picking up at: [task]."

**At the end of any session where work was done:**
1. Add a row to the session log (date, one-line summary, files changed)
2. Update the resume block with the next active task
3. Move resolved open questions into design.md
4. Record divergences from design.md pending update

**Never:** record transcripts, or let the session log grow past 10 sessions without archiving to `CONTEXT_ARCHIVE.md`.

---

## Output Quality Checklist

Before presenting any generated file, verify:

**requirements.md**
- [ ] All functional requirements use "shall" language with unique sequential REQ IDs
- [ ] Every acceptance criterion is checkable with dbt, SQL, dlt or the data app
- [ ] Every metric has a METRIC-xxx glossary entry with formula, grain, owner and status
- [ ] NFRs include freshness and reconciliation targets
- [ ] Out of scope section is present

**design.md**
- [ ] Every dlt resource has write disposition, primary key and incremental cursor (or a reason for full load)
- [ ] Every dbt model states its grain, unique key, materialization and tests
- [ ] Every METRIC maps to exactly one implementation; client-side metrics have a parity check
- [ ] Every data app is a dbt exposure with its marts, payload budget and interactions
- [ ] Every job has schedule, dependencies, retry and backfill behaviour
- [ ] DuckDB write/read access is stated
- [ ] Every REQ maps to a design element; open questions captured, not assumed

**tasks.md**
- [ ] Tasks follow the data flow order
- [ ] Every task has an inline REQ/METRIC/NFR reference and a concrete verification command
- [ ] Each task is one resource, model, metric, app view or job

**CONTEXT.md**
- [ ] Resume block has a specific task ID and status
- [ ] Session log has a row for the current session
- [ ] No transcripts, no `{{PLACEHOLDER}}` tokens

**AI config files**
- [ ] Universal Instruction Block is present, complete and identical across files
- [ ] Stack commands are real, not invented
- [ ] Another skill's block, if present, is untouched

---

## Teaching Mode

If the user is new to SDD, offer to explain concepts using `references/sdd-curriculum.md`, translating its web-app examples to data products (an endpoint becomes a mart or app view; a data model field becomes a column at a stated grain). Always offer to generate the actual files after explaining.

---

## Common Mistakes to Prevent

| Anti-pattern | What to say |
|---|---|
| "Just start coding — write the model and we'll spec later" | "Let's take ten minutes for requirements.md first — the grain and metric definitions decide how every model is built." |
| Model with no stated grain | "What does one row of this model represent? Let's write the grain down and add a unique test for it." |
| Same metric defined in several places | "Revenue is computed in two models and the app. Let's define METRIC-xxx once and point everything at it." |
| Acceptance criterion "data looks right" | "How will we know? Let's make it a dbt test or a reconciliation query against the source." |
| Source with no owner | "Who do we call when this source changes its schema? Let's record an owner." |
| Merge load without a primary key, or a non-idempotent load | "If this job runs twice, do we get duplicates? Let's set a primary key and merge disposition." |
| No backfill plan | "If we find a bug in this model next month, how do we rebuild history? Let's write that into the job design." |
| Data app reading staging or raw tables | "The app should read marts only — staging can change shape at any time." |
| Personal data flowing unmasked into marts | "This column is personal data. Should it be masked or dropped before the mart?" |
| Feature request with no spec context | "Before I add that — which data product does it belong to? I want it to land in the right spec." |
| Generating config files before spec exists | Never produce CLAUDE.md, .cursorrules, or similar until a product's requirements.md is at least drafted. |
| Filling placeholders with invented content | If interview answers are missing, ask — never fabricate metric formulas, sources or SLAs from a domain name. |
| Out of scope section missing | "What won't this version do? Stating it prevents scope creep." |
| Platform change disguised as a data product | "That needs a change to the runner (or UI, or WASM engine) — let's spec that part with spec-driven-sw." |
