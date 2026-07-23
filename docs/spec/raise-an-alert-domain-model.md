# Raise an Alert — Domain Data Model

Author role: Observability Engineer (domain data modeling)
Status: Draft v0.1 — proposed schema, not yet enforced by Ansible
Applies to: the "Raise an Alert" Scaffolder wizard (`docs/design/mockups/backstage-catalog-v2.html`),
the files committed to Bitbucket as a result of it, and the Ansible roles that
read those files (`ansible/roles/dxuim_config_sync`).

## 1. Purpose

The wizard collects three kinds of monitoring request — **Log**, **CMD
(resource threshold)**, and **Process** — against two kinds of asset —
**Microservice** and **Open System**. Today the only real, committed example
(`dxuim-config/UAT/ulaeiapos0a/processes.json`) is written directly in DX
UIM's native wire format (`probeConfigKeys`), because no domain model layer
exists yet. This spec defines that missing layer: one generalized document
shape, shared across all three categories and both asset types, that gets
committed to Bitbucket instead of either the raw form input or the
fully-transformed target-system payload.

This closes out the "Domain model completeness" section of
`docs/planning/backlog.md` by giving `matchType`, `comparisonOperator`,
`aggregation`, `lookbackWindow`, and `indexPattern` an actual home, and the
"Provenance & audit gaps" section by giving `changeRecordId` and
`sourceTaskId` a place to live in the committed document.

## 2. Design principles (recap)

These were established earlier and this schema follows them, not the other
way around:

- **Neither raw input nor wire payload.** Raw form input is too literal
  (it's shaped by whatever the wizard's UI happened to look like on a given
  day); a fully-transformed `probeConfigKeys` array is opaque to a PR
  reviewer and couples git history to DX UIM's schema. The domain model is
  the human-reviewable middle layer.
- **Ansible never writes git** (`docs/design/branching-strategy.md`). It only
  reads via the Bitbucket REST API and PUTs to the target system. So this
  document is the *only* artifact Ansible has to work with — anything not
  captured here is lost.
- **PUT is idempotent.** The domain model doesn't need to express deltas or
  intent-to-change — each file is a complete, current-state description of
  "what should be configured," safe to re-apply.
- **Additive schema evolution.** New fields get a default that reproduces
  today's implicit behavior, so files committed before a field existed keep
  working. `schemaVersion` exists so Ansible can tell old documents apart
  from new ones if a default ever needs to change.

## 3. Where this lives

Current, real, DX UIM-facing convention (unchanged by this spec):

```
dxuim-config/{environment}/{robot}/{probe}.json
```

`probe` is a DX UIM probe name, not the wizard's category name — the two use
different vocabularies:

| Wizard `category` | DX UIM probe file | DX UIM probe |
|---|---|---|
| `log` | `logmon.json` | Log Monitor |
| `cmd` | `cdm.json` | CDM (CPU/Disk/Memory) |
| `process` | `processes.json` | Processes |

The equivalent microservice/ELK-routed path convention is owned by
`ELK/backstage`'s Scaffolder skeleton, not this repo — out of scope here,
but the document shape below is written to fit either.

**Migration note**: `dxuim-config/UAT/ulaeiapos0a/processes.json` predates
this spec and is DX UIM wire format, not this domain model. Adopting this
schema means adding a transformation step to
`ansible/roles/dxuim_config_sync` (today it reads `probeConfigKeys` almost
as a passthrough — see `tasks/fetch_from_bitbucket.yml` and
`templates/dxuim_config_payload.json.j2`); it does not mean rewriting that
file immediately.

## 4. Common envelope

Every committed document — regardless of category or asset type — starts
with this shape:

| Field | Type | Required | Notes |
|---|---|---|---|
| `schemaVersion` | string | yes | `"1.0"` for this spec. Lets Ansible branch on shape if it ever changes non-additively. |
| `systemType` | enum: `microservice`, `opensystem` | yes | Drives which `asset` shape applies (§5). |
| `category` | enum: `log`, `cmd`, `process` | yes | Drives which extension object is present (§6). |
| `routing` | object | yes | See below. Captured at request time. |
| `asset` | object | yes | See §5. |
| `approver` | string (entity ref) | yes | e.g. `user:default/lead-sre`. **Gap**: the wizard captures this as free text (`wApprover`) today, not a resolved Backstage entity ref — see §9. |
| `metadata` | object | yes | See below. |

`routing`:

| Field | Type | Notes |
|---|---|---|
| `tool` | enum: `ELK`, `DX UIM` | The backend this request targets. |
| `state` | enum: `migrated`, `legacy`, `unknown` | `migrated` = OTel-enabled host routed to ELK; `legacy` = still DX UIM; `unknown` = host not found in the Asset Registry, defaulted to DX UIM. Microservices are always `ELK` with no `state` distinction. |

Routing is resolved once, when the request is raised (`resolveOpenSystemRouting()`
in the wizard, backed by the Asset Registry / `HOST_REGISTRY` demo data).
**Design risk worth flagging**: if a host migrates to OTel between the time
a request is committed and the time Ansible activates it, the committed
`routing` could be stale. This spec commits the value as captured; it does
not resolve the staleness question. Two options for whoever picks this up:
trust the committed value as-is (simplest, matches "PUT is idempotent" —
worst case the config lands on the pre-migration backend and gets
re-submitted after), or have Ansible re-derive routing from the live Asset
Registry at activation time and fail loudly if it disagrees with what's
committed. Not decided.

`metadata`:

| Field | Type | Required | Notes |
|---|---|---|---|
| `requestedBy` | string (entity ref) | yes | Existing convention (`dxuim-config/guide.md`). |
| `approvedBy` | string (entity ref) | yes | Existing convention. |
| `requestedAt` | string (ISO 8601) | yes | New. Not captured anywhere today. |
| `changeRecordId` | string | no | New — closes the backlog gap: "the Infinity change validation step returns *something*, but nothing captures that reference." Optional because not every environment requires a change record (e.g. SIT). |
| `sourceTaskId` | string | no | New — closes two backlog gaps at once: notification deep-linking back to the Scaffolder task, and the `staging/<name>` branch-naming collision (two concurrent requests for the same asset get two different branch names once this is threaded through). |

Files committed before this convention existed won't have `metadata` at
all — same graceful-degradation behavior `notify_requester` already has for
missing `requestedBy`/`approvedBy` should extend to these two new fields
(skip, don't fail).

## 5. Asset identity (`asset`)

Common to both system types — these three exist in the wizard for either
path (`wServiceId`/`wOpenServiceId`, `wSearchCode`/`wOpenSearchCode`,
`wEnv`/`wOpenEnv`):

| Field | Type | Notes |
|---|---|---|
| `environment` | enum: `SIT`, `UAT`, `PROD`, `DR` | |
| `serviceId` | string | HPSM service ID. |
| `searchCode` | string | HPSM search code. |

Plus a system-type-specific `identity` sub-object:

**`systemType: "microservice"`**

| Field | Type | Notes |
|---|---|---|
| `entity` | enum: `CBS`, `MIDDLEWARE`, `PAYMENTS`, `CHANNELS` | |
| `namespace` | string | K8s namespace, e.g. `deposit-adapter-sg`. |
| `container` | string | K8s container name, e.g. `ms-cbs-account-movement-adapter`. |

**`systemType: "opensystem"`**

| Field | Type | Notes |
|---|---|---|
| `hostname` | string | Also the Asset Registry / `HOST_REGISTRY` lookup key. |
| `osType` | enum: `Linux`, `Windows`, `AIX` | |
| `appName` | string | |

## 6. Category extensions

### 6.1 Log Monitoring (`category: "log"`)

| Field | Type | Required | Notes |
|---|---|---|---|
| `filepath` | string | conditional | Only when `routing.tool === "DX UIM"`. ELK/OTel resolves log location via resource attributes, so this is meaningless there — mirrors `needsFilepath` in the wizard today. |
| `matchType` | enum: `phrase`, `wildcard`, `regex` | no, default `phrase` | New — closes backlog gap "log watchers hardcode phrase-match today." Default reproduces current behavior exactly. |
| `lookbackWindow` | string | no, default `"1m"` | New — closes backlog gap "hardcoded `now-1m` in the ELK watcher template." Default matches that hardcode. |
| `keywords` | array of `{ keyword: string, severity: enum }` | yes, min 1 | `severity` ∈ `Critical`, `Major`, `Minor`, `Warning`. One document can carry several keywords sharing one `filepath` — matches how the wizard's keyword table works (one filepath field, many keyword rows) and how `docs/design/mockups/backstage-catalog-v2.html`'s demo data groups `EXISTING_CONFIG` entries by filepath. |

A single asset accumulates multiple log documents over time (one per
filepath, since each wizard submission targets one filepath) — see §7.1.

### 6.2 CMD Monitoring (`category: "cmd"`)

| Field | Type | Required | Notes |
|---|---|---|---|
| `metric` | enum: `CPU`, `Memory`, `Disk` | yes | |
| `comparisonOperator` | enum: `gt`, `gte`, `lt`, `lte` | no, default `gt` | New — closes backlog gap "CMD alerts implicitly assume 'greater than, instantaneous.'" Default matches current implicit behavior. |
| `aggregation` | enum: `avg`, `max`, `current` | no, default `avg` | New. Default chosen to match the existing "sustained for N minutes" wording in the UI — that phrasing already implies an averaged/sustained-breach check, not an instantaneous read. |
| `threshold` | number | yes | Percentage. |
| `duration` | number | yes | Minutes the breach must sustain before firing. |
| `severity` | enum | yes | `Critical`, `Major`, `Minor`, `Warning`. |

Only available for Open Systems today (`ALERT_MATRIX.microservice.cmd.available === false`,
noted "coming soon — pod resource watchers via metrics-server"). One
document per metric — matches the wizard (one metric chip selected per
submission).

### 6.3 Process Monitoring (`category: "process"`)

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | Process name or cmdline pattern, e.g. `*java*`. |
| `expectedState` | enum: `Running`, `Stopped` | yes | Alert fires when the process deviates from this. |
| `interval` | number | yes | Check interval, minutes. |
| `severity` | enum | yes | `Critical`, `Major`, `Minor`, `Warning`. |

Also Open-Systems-only today (`ALERT_MATRIX.microservice.process.available === false`,
"not applicable — Kubernetes liveness probes cover this"). One document per
process — matches the wizard. No backlog gap flagged here; already
structurally complete relative to what the wizard captures. (`matchType`
could symmetrically apply to `name` the way it does to log keywords — noted
as a future consideration, not a current gap, since nothing today needs it.)

## 7. Worked examples

### 7.1 Open System, Process, routed to DX UIM

Two separate documents (one process each), both under
`dxuim-config/UAT/ulaeiapos0a/` per the real robot already in this repo —
this is the domain-model equivalent of two of the entries already in
`processes.json`:

```json
{
  "schemaVersion": "1.0",
  "systemType": "opensystem",
  "category": "process",
  "routing": { "tool": "DX UIM", "state": "legacy" },
  "asset": {
    "environment": "UAT",
    "serviceId": "572",
    "searchCode": "MIDDLEWARE",
    "identity": { "hostname": "ulaeiapos0a", "osType": "Linux", "appName": "MIDDLEWARE" }
  },
  "process": {
    "name": "*java*",
    "expectedState": "Running",
    "interval": 5,
    "severity": "Critical"
  },
  "approver": "user:default/lead-sre",
  "metadata": {
    "requestedBy": "user:default/jdoe",
    "approvedBy": "user:default/lead-sre",
    "requestedAt": "2026-06-18T09:12:00Z",
    "changeRecordId": "INF-0042931",
    "sourceTaskId": "task-8f21c3"
  }
}
```

### 7.2 Microservice, Log, routed to ELK

```json
{
  "schemaVersion": "1.0",
  "systemType": "microservice",
  "category": "log",
  "routing": { "tool": "ELK" },
  "asset": {
    "environment": "PROD",
    "serviceId": "572",
    "searchCode": "MIDDLEWARE",
    "identity": {
      "entity": "CBS",
      "namespace": "deposit-adapter-sg",
      "container": "ms-cbs-account-movement-adapter"
    }
  },
  "log": {
    "matchType": "phrase",
    "lookbackWindow": "1m",
    "keywords": [
      { "keyword": "400", "severity": "Major" },
      { "keyword": "500", "severity": "Major" }
    ]
  },
  "approver": "user:default/lead-sre",
  "metadata": {
    "requestedBy": "user:default/jdoe",
    "approvedBy": "user:default/lead-sre",
    "requestedAt": "2026-05-02T14:03:00Z"
  }
}
```

### 7.3 Open System, CMD, routed to ELK (post-migration) — flags a real gap

```json
{
  "schemaVersion": "1.0",
  "systemType": "opensystem",
  "category": "cmd",
  "routing": { "tool": "ELK", "state": "migrated" },
  "asset": {
    "environment": "PROD",
    "serviceId": "231",
    "searchCode": "MIDDLEWARE",
    "identity": { "hostname": "sgapp0231", "osType": "Linux", "appName": "MIDDLEWARE" }
  },
  "cmd": {
    "metric": "CPU",
    "comparisonOperator": "gt",
    "aggregation": "avg",
    "threshold": 90,
    "duration": 5,
    "severity": "Critical"
  },
  "approver": "user:default/lead-sre",
  "metadata": {
    "requestedBy": "user:default/jdoe",
    "approvedBy": "user:default/lead-sre",
    "requestedAt": "2026-07-10T08:44:00Z"
  }
}
```

This document is fully valid against the schema, and the wizard would
happily produce it (`sgapp0231` is `otel: true` in `HOST_REGISTRY`, so all
three categories route to ELK together per the comment in `ALERT_MATRIX`).
But §8.2 below has no defined ELK-side shape for `cmd` or `process` — only
`log` maps to an established Elasticsearch Watcher pattern. This is a real,
current gap, not a hypothetical one: it will be hit the first time someone
raises a CMD or Process alert against an OTel-migrated host.

## 8. Target-system mapping

### 8.1 DX UIM

**Process — real, verified** (matches the actual shape in
`dxuim-config/UAT/ulaeiapos0a/processes.json`). Watcher name follows the
existing `generateWatcherNames()` convention (`{prefix}_{sanitized-name}_process`):

| Domain model | `probeConfigKeys` |
|---|---|
| — | `/watchers/{name}/active` = `"yes"` |
| — | `/watchers/{name}/scan_proc_cmd_line` = `"yes"` |
| `expectedState: "Running"` → | `/watchers/{name}/report` = `"down"` (alert when it goes down) |
| `expectedState: "Stopped"` → | `/watchers/{name}/report` = `"up"` (alert when it comes up) |
| `name` → | `/watchers/{name}/proc_cmd_line` = `name` |
| — | `/watchers/{name}/process` = `""` |

**CMD and Log — proposed, unverified.** `cdm.json` and `logmon.json` are
still empty placeholders for the one real robot in this repo (see
`docs/planning/overview.md`), so there's no real example to reverse-engineer
a key structure from, the way there was for `processes.json`. Anyone
implementing the transform for these two needs to confirm the actual CDM
and Log Monitor probe key conventions against Broadcom's probe
documentation (or a populated real example) before shipping — don't assume
the sketch below is correct:

```
/monitor/{metric}/threshold
/monitor/{metric}/duration
/monitor/{metric}/severity
```

### 8.2 ELK

**Log — established pattern** (the Elasticsearch Watcher template referenced
in `docs/planning/backlog.md`): keyword match query against an index
pattern, condition on hit count within `lookbackWindow`, action fires a
notification. `indexPattern` is currently *derived* at generation time
(from namespace/container naming) rather than stored — the backlog already
flags this as incomplete. This spec's position: `indexPattern` belongs as
an optional field on the `log` extension object (only relevant when
`routing.tool === "ELK"`), defaulting to the derived value when absent, so a
user can override it for the cases where derivation guesses wrong. Left out
of §6.1's table above because it's ELK-only, not category-universal — add it
there when the ELK-side generator actually starts accepting overrides.

**CMD and Process — undefined.** No Elasticsearch Watcher (or any other
mechanism) has been designed for these two categories against an
OTel-migrated Open System host. This isn't a "probably fine, just needs
Ansible plumbing" gap like DX UIM's CDM/Log probes above — it's a genuine
open design question (Prometheus-style alerting rules over OTel metrics?
Grafana-managed alerts? something else?) that belongs to whoever owns the
ELK-side automation, tracked via the `ELK/ansible/` scope decision in
`docs/planning/backlog.md`.

## 9. Open questions

Carried over from — and should stay in sync with — `docs/planning/backlog.md`:

- **`approver` as free text.** The wizard captures `wApprover` as a plain
  string today ("resolved via Active Directory," per the UI's own
  placeholder copy), not a validated Backstage entity ref. This schema
  documents the target shape (`user:default/...`); resolving that gap is a
  wizard-side fix, not a schema-side one.
- **Routing staleness** — see §4. Not decided.
- **CMD/Process on ELK** — see §8.2. Not designed anywhere yet.
- **`indexPattern` override** — see §8.2. Depends on the ELK-side generator
  accepting it, which is outside this repo.
