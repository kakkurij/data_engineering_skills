# Data Stack Patterns — dlt, dbt on DuckDB, metrics, data apps, orchestration

Read this when filling in design.md or tasks.md. These are defaults; when the repo already does
something differently, follow the repo and note it in design.md.

---

## 1. Ingestion with dlt

### Write disposition — choose per resource

| Disposition | Use when | Needs |
|---|---|---|
| `append` | Immutable events (clicks, log lines, ledger entries) | Nothing — but reruns duplicate, so pair with an incremental cursor |
| `replace` | Small reference data, or sources with no reliable change tracking | Nothing; full reload every run |
| `merge` | Mutable records (orders, customers, subscriptions) | `primary_key` (and optionally `merge_key`) |

`merge` also supports an `scd2` strategy that keeps history in the raw table. Pick **one** place for
history per source — dlt `scd2` or dbt snapshots — and record which in design.md.

### Incremental loading

```python
@dlt.resource(primary_key="order_id", write_disposition="merge")
def orders(updated_at=dlt.sources.incremental("updated_at", initial_value="2024-01-01")):
    ...
```

- The cursor state is stored by dlt in the destination, so reruns pick up where they left off.
- Choose a cursor the source updates on every change (`updated_at`, not `created_at`) for mutable data.
- Late-arriving updates: if the source can change records older than the cursor, add a lookback window
  and rely on `merge` to deduplicate. Record the window in design.md.

### Schema contracts

`schema_contract` controls what happens when the source schema changes:

| Mode | Effect |
|---|---|
| `evolve` | Accept new tables/columns (default) |
| `freeze` | Fail the load on change |
| `discard_row` | Drop rows that don't fit |
| `discard_value` | Drop the non-conforming values, keep the row |

Default to `evolve` for tables and `freeze` for `data_type` on sources that feed metrics, so type
changes stop the pipeline instead of silently changing numbers.

### Load metadata

dlt adds `_dlt_load_id` and `_dlt_id` to every row and writes a `_dlt_loads` table
(`load_id`, `status`, `inserted_at`). Use it for freshness and reconciliation checks.

Useful commands: `dlt pipeline <name> info`, `dlt pipeline <name> trace`.

---

## 2. Transformation with dbt on DuckDB

### Layers and naming

| Layer | Prefix | Purpose | Materialization default |
|---|---|---|---|
| Staging | `stg_<source>__<entity>` | 1:1 with a raw table: rename, cast, dedupe, mask personal data | view |
| Intermediate | `int_<entity>_<verb>` | Joins and reshaping not exposed to apps | view or table |
| Mart | `fct_<process>` / `dim_<entity>` | What data apps read; stable contract | table or incremental |

Data apps read **marts only**.

### Grain and keys

Every model's grain is written as one sentence ("one row per order line"). Enforce it:

```yaml
models:
  - name: fct_order_lines
    columns:
      - name: order_line_id
        data_tests: [unique, not_null]
```

For composite grains, use `dbt_utils.unique_combination_of_columns` if dbt_utils is installed, or a
singular test that groups by the grain columns and asserts no count > 1.

### Incremental models on DuckDB

dbt-duckdb supports the `append` and `delete+insert` incremental strategies; check your adapter
version before relying on `merge`. Use `unique_key` with `delete+insert` for mutable data.
Rebuild history with `dbt build --select <model> --full-refresh`.

### External materialization

dbt-duckdb can write a model to Parquet (`materialized='external'`). This is a clean way to hand marts
to the data app without the app opening the DuckDB file (see §5).

### Tests to include by default

- `unique` + `not_null` on every grain key
- `relationships` from facts to dimensions
- `accepted_values` on status/category columns that drive filters or metrics
- A reconciliation test per source: row count or sum in the mart vs. raw, within the NFR tolerance
- dbt unit tests (dbt ≥ 1.8) for non-trivial metric logic

### Freshness

Declare `freshness` on sources with a `loaded_at_field` (a source timestamp such as `updated_at`), and run
`dbt source freshness` in the job. If the source has no reliable timestamp, check `_dlt_loads.inserted_at`
with a singular test instead.

---

## 3. Metrics

- The **definition** lives once in requirements.md (METRIC-xxx): formula, grain, filters, owner.
- The **implementation** lives once: a mart column, or a single macro/SQL definition reused by marts.
- Additive metrics (sums, counts) can be pre-aggregated in marts and re-aggregated by the app.
  Non-additive metrics (ratios, distinct counts, averages) must ship their components
  (numerator and denominator, or distinct keys) so the app can compute them correctly at any filter.
- If the data app computes a metric client-side in the WASM engine, design.md names a **parity check**:
  the same fixture data computed in dbt and in the app must give the same number.
- Changing a metric definition is a spec change: bump the version and run `dbt ls --select <model>+`
  to find every downstream model and exposure.

---

## 4. Data apps

Each data app is declared as a dbt exposure so lineage reaches the screen:

```yaml
exposures:
  - name: sales_performance_app
    type: application
    maturity: medium
    owner:
      name: Sales Ops
    depends_on:
      - ref('fct_order_lines')
      - ref('dim_sales_rep')
```

`dbt build --select +exposure:sales_performance_app` builds and tests everything the app depends on.

For each app, design.md records:
- **Marts it reads** — at the grain the interactions need (pre-aggregate to keep payloads small)
- **Payload budget** — max rows or MB shipped to the browser for the WASM engine
- **Views, filters, interactions** — what the user can do
- **Metrics shown** — METRIC refs, and whether each is computed in dbt or in the app
- **Interaction budget** — e.g. cross-filter < 100 ms p95 at the payload budget

If an interaction needs something the UI or WASM engine can't do yet, that's platform work for spec-driven-sw.

---

## 5. Orchestration and DuckDB access

### Jobs

A typical job for one product:

```
dlt pipeline <source>  →  dbt source freshness  →  dbt build --select source:<source>+  →  publish for apps
```

Every job in design.md states: what it runs, schedule, dependencies on other jobs, retry policy, and how
history is rebuilt (backfill). Jobs must be **idempotent** — running twice gives the same result.

### DuckDB concurrency

A DuckDB database file can be opened by **one process in read-write mode**, or by **several processes
read-only** — not both at once. The design must say how jobs and apps share data. Common patterns:

| Pattern | How | Trade-off |
|---|---|---|
| Single writer, serialized jobs | The runner holds the only read-write connection; jobs never overlap | Simple; app can't read during loads |
| Parquet hand-off | Marts written as external Parquet; the API/app reads Parquet | App never touches the DB file; extra storage |
| Snapshot publish | After a successful job, copy the DB file; the API opens the copy read-only | Consistent reads; copy cost grows with size |

Record the chosen pattern in design.md § Orchestration → DuckDB access.

---

## 6. Verification commands for tasks.md

| Task output | Verify with |
|---|---|
| dlt resource | Run the pipeline, then a row-count query on the raw table and `dlt pipeline <name> info` |
| Staging/mart model | `dbt build --select <model>` |
| Grain | Uniqueness query or the model's `unique` test |
| Metric | Unit test or a SQL check against a known value; parity check if computed in the app |
| Exposure / data app | `dbt build --select +exposure:<name>` and an app check against the interaction budget |
| Job | Run it through the runner twice; results identical (idempotency) |
| Backfill | Full-refresh run reproduces the same totals as the incremental history |
