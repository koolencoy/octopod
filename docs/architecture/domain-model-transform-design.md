# Domain-model transform — design

**Status:** Proposed v0.1 — for review. Each section is marked
**Decided** (follows from existing architecture rules), **Proposed**
(this document's recommendation, open to challenge), or **Open**
(needs a decision before build).

**Depends on:** `docs/spec/raise-an-alert-domain-model.md` (the format
itself, Draft v0.1) and `docs/architecture/architecture.md` (the rules
this design must not break). Terminology is defined there.

---

## 1. What this designs, in one paragraph

The spec defines a tool-neutral document format for alert requests.
This document designs the *machinery*: how Ansible recognizes,
validates, and translates those documents into each monitoring tool's
native format at activation time — and how old-format and new-format
files coexist while the migration happens. It is the build plan for
the "translator" boxes in the architecture doc's section 5.

## 2. The pipeline, before and after

Today (built, verified):

```
fetch from Bitbucket ──► parse path ──► PUT probeConfigKeys as-is
```

After this design:

```
fetch from Bitbucket ──► parse path ──► detect format ──┬─► wire format: pass through (unchanged)
                                                        └─► domain model: validate ──► transform ──► aggregate ──► PUT
```

Nothing upstream (trigger modes, Bitbucket reads) or downstream (the
PUT call, retries, notifications) changes. The transform is a new
middle stage inside `dxuim_config_sync`, between
`fetch_from_bitbucket.yml` and `post_to_dxuim.yml`.

## 3. Format detection and coexistence — **Proposed**

Both formats will exist in the config repo simultaneously, possibly
for a long time. Detection is per file, by an unambiguous marker:

| File contains | Treated as | Behavior |
|---|---|---|
| `schemaVersion` key | Domain model | Validate → transform → PUT |
| `probeConfigKeys` key (no `schemaVersion`) | Wire format (legacy) | Pass through exactly as today |
| Both keys | Invalid | Per-file failure (§6) — a file must be one thing |
| Neither (empty `{}`) | Placeholder | Skipped, as today ("not configured yet") |

Rules:

- **No flag days.** Existing wire-format files keep working unmodified,
  forever if necessary. Migration of old files is optional and manual
  (a human PR converting a file — Ansible never writes git, so it
  cannot convert files itself).
- **`schemaVersion` gate.** Only `"1.0"` is accepted. An unknown
  version is a per-file failure, not a guess — a newer document shape
  must never be half-applied by an older translator.
- **The wizard switches last.** The wizard starts committing
  domain-model documents only after the transform is deployed and
  verified (§8). Order matters: deploy the reader before the writer.

## 4. File layout: one document per file — **Open, recommendation below**

The spec (§7.1) models one document per alert (one process, one metric,
one filepath), but today's repo layout is one file per *probe*
(`processes.json` holds every process watcher for the robot). These
don't line up, and the transform design must pick a layout:

**Option A — keep one file per probe**, holding an array of domain
documents. Keeps the current 1 file = 1 PUT mapping, so Ansible barely
changes. But every request for the same robot+probe edits the same
file, so concurrent requests conflict at the git level — aggravating
the branch-collision problem we already have — and a PR diff shows an
edit to a shared file rather than a self-contained addition.

**Option B — one document per file**, e.g.
`dxuim-config/UAT/ulaeiapos0a/processes/java-watchdog.json`. Each
request adds (or removes) its own file: clean PRs, no concurrent-edit
conflicts, and **deletion becomes a first-class operation** — removing
an alert is deleting a file, something the current one-file-per-probe
layout cannot express (today an empty file means "never configured,"
and there is no way to say "remove this one watcher"). The cost:
Ansible must *aggregate* — when any file under a robot changes, it
re-reads that robot's full folder and rebuilds each affected probe's
complete payload before the PUT (the DX UIM API takes the whole probe
config in one call).

**Recommendation: Option B.** The aggregation step is modest, contained
Ansible work; in exchange we fix the concurrent-request conflict at the
storage layer and gain a real deletion path — both are known gaps that
would otherwise need separate solutions. The re-aggregation rule also
strengthens idempotency: the PUT payload is always derived from the
complete current state of the robot folder on `main`, never from a
diff.

Consequence to accept explicitly: with Option B, a changed-file trigger
(webhook) causes Ansible to re-read the whole robot folder, not just
the changed file. That is a few extra Bitbucket reads per sync — noise
at current scale.

## 5. Where the translation logic lives — **Proposed**

A **custom Ansible filter plugin** (Python) inside the role:

```
ansible/roles/dxuim_config_sync/
└── filter_plugins/
    └── dxuim_transform.py     # domain document(s) → probeConfigKeys
```

Called from the role as
`{{ robot_documents | dxuim_transform }}`, replacing nothing — the
existing Jinja payload template still renders the final JSON body from
whatever `probeConfigKeys` it is given.

Why a filter plugin and not more Jinja/`set_fact` logic:

- **Testable outside Ansible.** The mapping (spec §8.1) is pure
  data-in/data-out. As a Python function it gets unit tests with golden
  files (`pytest`, no Ansible runtime needed) — the same way the
  mapping tables in the spec are written.
- **Readable at review time.** The Process mapping alone is six keys
  with conditional logic on `expectedState`; in Jinja that becomes the
  unmaintainable string-assembly the domain model exists to avoid.
- **The pattern scales to the other tools.** The future ELK and
  SolarWinds roles get their own sibling plugins
  (`elk_transform.py`, `solarwinds_transform.py`) with the same
  signature: validated domain documents in, tool-native payload out.
  The contract is the spec; the plugins are per-tool implementations
  of it.

One plugin per tool, one mapping module per category inside it
(process / cmd / log), because that's how the spec's §8 is structured
and how vendor verification will proceed (Process is verified; CMD and
Log are not — see §7).

## 6. Validation and failure behavior — **Proposed**

Validation runs *before* transform, per file, against a JSON Schema
committed next to the spec (`docs/spec/raise-an-alert-domain-model.schema.json`
— to be generated from the spec's tables, and versioned with it).

Failure behavior extends the existing "failure is loud, twice" rule,
with one addition — **a bad file must not block good files**:

| Event | Behavior |
|---|---|
| File fails validation (bad schema, unknown `schemaVersion`, both-format file) | Skip *this file*; notify its requester (critical, "your request could not be applied — config invalid"); continue with remaining files; fail the job at the end. |
| Transform raises (a valid document the mapping can't handle) | Same as validation failure — this is a platform bug, so the notification wording differs ("platform error, SRE attention"), but isolation is identical. |
| PUT fails | Unchanged from today: retry ×3, notify requester, fail job. |

Rationale: a full poll re-syncs every robot; one malformed file in one
robot's folder must not stop fifty healthy robots from syncing. Per-file
isolation with an end-of-run job failure keeps both properties: broken
things are loud, healthy things still ship.

## 7. What must be verified before each mapping ships — **Decided** (already backlog policy)

- **Process** — mapping verified against the real committed
  `processes.json`. Buildable now.
- **CMD and Log** — the spec's key sketches are explicitly unverified;
  there is no populated real example. **Gate: do not implement these
  two mappings until the key structure is confirmed** against Broadcom
  probe documentation or a hand-configured real example (this is
  already a current-milestone task — filling `cdm.json` / `logmon.json`
  for the first robot serves both purposes). Shipping a guessed mapping
  would write wrong config to production monitoring — worse than no
  automation.

## 8. Migration sequence — **Proposed**

Each phase is independently shippable and reversible:

1. **Phase 0 (today):** wire-format passthrough only.
2. **Phase 1 — dual-read:** deploy detection + validation + Process
   transform + aggregation. No domain-model files exist yet in the
   repo, so behavior is provably unchanged (verified against the stub).
   Hand-commit one domain-model process document in UAT; confirm
   end-to-end.
3. **Phase 2 — wizard switches:** the Scaffolder template starts
   committing domain-model documents (Process first). Owned by the
   Backstage repo; octopod's part is done in Phase 1.
4. **Phase 3 — CMD/Log mappings:** after the §7 verification gate
   clears.
5. **Phase 4 (optional, unhurried):** manually convert legacy
   wire-format files via normal PRs, robot by robot. No deadline; the
   dual-read keeps both working.

## 9. Out of scope here

- The ELK and SolarWinds translators themselves (the *pattern* is §5;
  their mappings need their own verified specs first).
- The wizard-side change (Phase 2) — Backstage repo.
- Backfilling `metadata` into legacy files.

## 10. Open questions for review

1. **File layout (§4)** — Option B is recommended but changes the repo
   convention; needs sign-off since the wizard and the guide both
   encode the current layout.
2. **Schema file ownership** — generate the JSON Schema from the spec
   by hand once, or treat the schema file as the source of truth and
   the spec's tables as documentation of it? (Recommend the latter —
   one machine-checkable truth.)
3. **Aggregation and legacy coexistence** — if a robot has *both* a
   legacy `processes.json` and new `processes/*.json` documents, which
   wins? Proposed: that state is invalid (per-file failure on the
   robot) — a robot migrates atomically in one PR.
