#!/usr/bin/env python3
"""Phase 2A Assertion Runner — spec-driven-data skill."""

import re, sys, os

ROOT  = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
BASE  = os.path.join(ROOT, "skills", "spec-driven-data")
def load(rel): return open(os.path.join(BASE, rel), encoding="utf-8").read()
SKILL    = load("SKILL.md")
TMPL     = load("references/templates.md")
CROSS    = load("references/capabilities-and-cross-ai.md")
PATTERNS = load("references/data-stack-patterns.md")
SW_SKILL = open(os.path.join(ROOT, "skills", "spec-driven-sw", "SKILL.md"), encoding="utf-8").read()

results = []
def a(id, desc, passed, note=""): results.append((id, desc, passed, note))

# ── Extractors ───────────────────────────────────────────────────────────────

def section(text, heading):
    """Body of a heading until the next ## heading."""
    m = re.search(rf"(?:^|\n)#+ {re.escape(heading)}[^\n]*\n", text)
    if not m: return ""
    start = m.end()
    stop = re.search(r"\n## ", text[start:])
    return text[start : start + stop.start()] if stop else text[start:]

def tmpl_section(heading):
    """Template section — stops at the next '## Template:' or '## The Universal' peer only."""
    m = re.search(rf"(?:^|\n)## {re.escape(heading)}[^\n]*\n", TMPL)
    if not m: return ""
    start = m.end()
    stop = re.search(r'\n## Template:|\n## The Universal', TMPL[start:])
    return TMPL[start : start + stop.start()] if stop else TMPL[start:]

def desc_field(text):
    m = re.search(r"description: >\n  (.+?)(?=\n---)", text, re.DOTALL)
    return m.group(1).replace("\n  ", " ").strip() if m else ""

def name_field(text):
    m = re.search(r"^name: (\S+)", text, re.MULTILINE)
    return m.group(1) if m else ""

def claude_turns(ex): return re.findall(r'> Claude: "([^"]*)"', ex)

# ── Pre-extract ──────────────────────────────────────────────────────────────
desc      = desc_field(SKILL)
step1     = section(SKILL, "Step 1: Interview the User")
gate      = section(SKILL, "Generation Gate (enforced between Step 1 and Step 2)")
step3     = section(SKILL, "Step 3: Generate `design.md`")
step4     = section(SKILL, "Step 4: Generate `tasks.md`")
step5     = section(SKILL, "Step 5: AI Agent Configuration Files")
retrofit  = section(SKILL, "Workflow: Existing Data Product (Retrofit)")
mistakes  = section(SKILL, "Common Mistakes to Prevent")
partial_m = re.search(r"Example of partial-answer handling:(.*?)(?=\n###|\n##|\Z)", SKILL, re.DOTALL)
partial_ex = partial_m.group(1) if partial_m else ""

req_tmpl  = tmpl_section("Template: requirements.md")
des_tmpl  = tmpl_section("Template: design.md")
task_tmpl = tmpl_section("Template: tasks.md")
uib_tmpl  = tmpl_section("The Universal AI Instruction Block")
ctx_tmpl  = tmpl_section("Template: CONTEXT.md")

# ════════════════════════════════════════════════════════════
# CATEGORY 1: TRIGGER
# ════════════════════════════════════════════════════════════
a("001","Skill name is 'spec-driven-data'",          name_field(SKILL) == "spec-driven-data", name_field(SKILL))
a("002","Name uses only lowercase, digits, hyphens", bool(re.fullmatch(r"[a-z0-9-]{1,64}", name_field(SKILL))))
a("003","Description ≤ 1024 chars",                  len(desc) <= 1024, f"{len(desc)} chars")
a("004","'data product' in description",             "data product" in desc)
a("005","'dbt model' in description",                "dbt model" in desc)
a("006","'dlt pipeline' in description",             "dlt pipeline" in desc)
a("007","'data app' in description",                 "data app" in desc)
a("008","'no specs yet' in description",             "no specs yet" in desc)
a("009","Description hands platform work to spec-driven-sw", "spec-driven-sw" in desc)
a("010","sw description hands data work to spec-driven-data", "spec-driven-data" in desc_field(SW_SKILL))

# ════════════════════════════════════════════════════════════
# CATEGORY 2: STACK
# ════════════════════════════════════════════════════════════
stack = section(SKILL, "The Stack Is Fixed")
a("011","Fixed stack section exists",                bool(stack))
a("012","Stack names dlt, dbt, DuckDB",              all(t in stack for t in ["dlt", "dbt", "DuckDB"]))
a("013","Stack names WASM data apps",                "WASM" in stack)
a("014","'Never ask which tools' rule",              "Never ask which tools" in stack)
a("015","Platform work hands off to spec-driven-sw", "spec-driven-sw" in stack)

# ════════════════════════════════════════════════════════════
# CATEGORY 3: GATE
# ════════════════════════════════════════════════════════════
a("016","Generation Gate section exists",            bool(gate))
a("017","Gate has exactly 4 □ items",                gate.count("□") == 4, f"found {gate.count('□')}")
a("018","'Only when all four' in gate",              "Only when all four" in gate)
a("019","Gate checks sources",                       "sources" in gate.lower())
a("020","Gate checks freshness",                     "freshness" in gate.lower())
a("021","Gate checks metrics and definitions",       "metrics" in gate.lower() and "definition" in gate.lower())
a("022","'source ≠ freshness' in gate",              "source ≠ freshness" in gate)
a("023","'concrete deliverable name' in gate",       "concrete deliverable name" in gate)

# ════════════════════════════════════════════════════════════
# CATEGORY 4: INTERVIEW
# ════════════════════════════════════════════════════════════
a("024","'exactly ONE question' in Step 1",          "exactly ONE question" in step1)
a("025","Sources/freshness split rationale",         "one does not imply the other" in step1)
a("026","Draft metric rule (never invent formula)",  "draft" in step1 and "never invent" in step1)
a("027","Correct pacing example exists",             "Example of correct pacing" in step1)
a("028","'never bundle them' in partial example",    "never bundle them" in partial_ex)
turns = claude_turns(partial_ex)
a("029","Partial example has ≥ 3 Claude turns",      len(turns) >= 3, f"found {len(turns)}")
a("030","No Claude turn asks about tool choice",     not any(re.search(r"which (tool|database|warehouse)", t, re.I) for t in claude_turns(step1)))

# ════════════════════════════════════════════════════════════
# CATEGORY 5: TEMPLATE
# ════════════════════════════════════════════════════════════
a("031","'shall' in requirements template",          "shall" in req_tmpl)
a("032","Metrics Glossary in requirements template", "Metrics Glossary" in req_tmpl and "METRIC-" in req_tmpl)
a("033","Glossary entry has formula, grain, owner, status",
    all(f in req_tmpl for f in ["_Formula_", "_Grain_", "_Owner_", "_Status_"]))
a("034","Sources table with owner in requirements",  "## Sources" in req_tmpl and "Owner" in req_tmpl)
a("035","'Out of Scope' in requirements template",   "Out of Scope" in req_tmpl)
a("036","design: dlt write disposition + cursor",    "Write disposition" in des_tmpl and "Incremental cursor" in des_tmpl)
a("037","design: dlt schema contract",               "Schema contract" in des_tmpl)
a("038","design: model grain + unique key",          "**Grain**" in des_tmpl and "**Unique key**" in des_tmpl)
a("039","design: metric parity check",               "Parity check" in des_tmpl)
a("040","design: data app as dbt exposure",          "dbt exposure" in des_tmpl)
a("041","design: payload budget",                    "Payload" in des_tmpl and "budget" in des_tmpl)
a("042","design: orchestration retry + backfill",    "Retry" in des_tmpl and "Backfill" in des_tmpl)
a("043","design: DuckDB access section",             "DuckDB access" in des_tmpl)
a("044","design: Open Questions",                    "Open Questions" in des_tmpl)
a("045","tasks: refs include METRIC",                "REQ/METRIC/NFR" in task_tmpl)
a("046","tasks: verify uses dbt build",              "_Verify_" in task_tmpl and "dbt build" in task_tmpl)

# ════════════════════════════════════════════════════════════
# CATEGORY 6: UIB
# ════════════════════════════════════════════════════════════
a("047","UIB header is DATA PRODUCT CONSTITUTION",   "DATA PRODUCT CONSTITUTION" in uib_tmpl)
for i, p in enumerate(["MANDATORY BEFORE ANY ACTION", "HARD CONSTRAINTS", "DIVERGENCE PROTOCOL"]):
    a(f"{48+i:03d}", f"'{p}' in UIB", p in uib_tmpl)
a("051","UIB step 0 reads product CONTEXT.md first",
    0 <= uib_tmpl.find("CONTEXT.md") < uib_tmpl.find("Read requirements.md"))
a("052","UIB: metrics only via METRIC entry",        "METRIC entry" in uib_tmpl)
a("053","UIB: apps never read raw/staging",          "raw or staging" in uib_tmpl)
a("054","UIB: grain changes need design.md first",   "grain" in uib_tmpl)
a("055","Stack commands section in templates",       "STACK COMMANDS" in TMPL and "Never invent" in TMPL)
a("056","Cross-AI file defers UIB to templates.md",  "references/templates.md" in CROSS and "DATA PRODUCT CONSTITUTION" in CROSS)
a("057","Cross-AI file has no stale PROJECT block",  "PROJECT CONSTITUTION" not in CROSS)
a("058","Per-agent templates paste stack commands",  CROSS.count("[paste Stack commands here]") >= 4)
a("059","Step 5 keeps the other skill's block",      "PLATFORM CONSTITUTION" in step5 and "Never remove" in step5)
a("060","sw Step 5 keeps the data block",            "DATA PRODUCT CONSTITUTION" in SW_SKILL)

# ════════════════════════════════════════════════════════════
# CATEGORY 7: DESIGN & TASK RULES
# ════════════════════════════════════════════════════════════
a("061","design rules: grain for every model",       "grain" in step3.lower())
a("062","design rules: one implementation per METRIC","exactly one implementation" in step3)
a("063","design rules: DuckDB single read-write",    "one read-write process" in step3)
a("064","task rules: data-flow order",               "dlt source → staging" in step4)
a("065","task rules: one model per task",            "one dbt model" in step4)
a("066","Patterns file covers write dispositions",   all(d in PATTERNS for d in ["`append`", "`replace`", "`merge`"]))
a("067","Patterns file covers DuckDB concurrency",   "DuckDB concurrency" in PATTERNS)
a("068","Patterns file covers non-additive metrics", "Non-additive" in PATTERNS)
a("069","Patterns file covers exposures",            "exposures:" in PATTERNS)

# ════════════════════════════════════════════════════════════
# CATEGORY 8: RETROFIT
# ════════════════════════════════════════════════════════════
a("070","Retrofit workflow exists",                  bool(retrofit))
nq = len(re.findall(r'^\d+\.', section(SKILL, "Retrofit Interview"), re.MULTILINE))
a("071","Retrofit interview has ≥ 5 numbered Qs",    nq >= 5, f"found {nq}")
a("072","Retrofit reads dbt manifest",               "manifest" in retrofit)
a("073","Retrofit reads information_schema",         "information_schema" in retrofit)
a("074","'[TO VERIFY]' in retrofit",                 "[TO VERIFY]" in retrofit)
a("075","'v0-retrofit' in retrofit",                 "v0-retrofit" in retrofit)
a("076","Retrofit Gap Flagging exists",              "Retrofit Gap Flagging" in retrofit)
a("077","Phase 1 is Spec Verification",              "Spec Verification" in retrofit)

# ════════════════════════════════════════════════════════════
# CATEGORY 9: CHANGE, CONTEXT, TASK CLOSE
# ════════════════════════════════════════════════════════════
a("078","Spec Presence Check exists",                "Spec Presence Check" in SKILL)
a("079","Metric change process uses dbt ls +",       "Metric changes" in SKILL and "dbt ls --select" in section(SKILL, "Metric changes"))
a("080","Task closing protocol exists",              "Task closing protocol" in SKILL)
a("081","Task closing forbids bundling",             "never bundle" in section(SKILL, "Task closing protocol"))
a("082","CONTEXT.md is per product",                 "specs/<product>/CONTEXT.md" in SKILL)
for i, p in enumerate(["Resume from here", "Session log", "Key decisions", "Open questions", "Divergences"]):
    a(f"{83+i:03d}", f"CONTEXT template has '{p}'", p in ctx_tmpl)
a("088","Quality checklist covers CONTEXT.md",       "CONTEXT.md" in section(SKILL, "Output Quality Checklist"))

# ════════════════════════════════════════════════════════════
# CATEGORY 10: ANTIPATTERN
# ════════════════════════════════════════════════════════════
for i, (p, label) in enumerate([
    ("just start coding",             "'just start coding'"),
    ("no stated grain",               "model with no stated grain"),
    ("same metric defined",           "metric defined in several places"),
    ("data looks right",              "'data looks right' acceptance"),
    ("non-idempotent",                "non-idempotent load"),
    ("backfill",                      "no backfill plan"),
    ("staging or raw",                "app reading staging/raw"),
    ("personal data",                 "unmasked personal data"),
    ("generating config files before spec exists", "config before spec"),
    ("fabricate",                     "fabricated content"),
    ("platform change",               "platform change handoff"),
]):
    a(f"{89+i:03d}", f"Anti-pattern: {label}", p in mistakes.lower())

# ════════════════════════════════════════════════════════════
# REPORT
# ════════════════════════════════════════════════════════════
cats = [("TRIGGER",1,10),("STACK",11,15),("GATE",16,23),("INTERVIEW",24,30),("TEMPLATE",31,46),
        ("UIB",47,60),("DESIGN",61,69),("RETROFIT",70,77),("SESSION",78,88),("ANTIPATTERN",89,99)]
passed = [r for r in results if r[2]]
failed = [r for r in results if not r[2]]
print(f"\n{'='*62}")
print(f"  SPEC-DRIVEN-DATA — PHASE 2A REPORT")
print(f"{'='*62}")
print(f"  Total: {len(results)}   Pass: {len(passed)}   Fail: {len(failed)}")
print(f"{'='*62}\n")
for cat, lo, hi in cats:
    items = [r for r in results if lo <= int(r[0]) <= hi]
    print(f"  [{cat}]  {sum(1 for r in items if r[2])}/{len(items)}")
    for id, desc, ok, note in items:
        ns = f"  ({note})" if note else ""
        print(f"    {'✓' if ok else '✗'} {id}: {desc}{ns}")
    print()
if failed:
    print(f"{'='*62}\n  FAILURES\n{'='*62}")
    for id, desc, ok, note in failed:
        print(f"\n  ✗ ASSERT-{id}: {desc}")
        if note: print(f"    → {note}")
    sys.exit(1)
print(f"{'='*62}\n  ALL ASSERTIONS PASSED — Phase 2A complete\n{'='*62}\n")
sys.exit(0)
