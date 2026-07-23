# Execution plan — to 30 September 2026

Week-by-week plan delivering the **DX UIM base hardening** milestone
(`milestones.md`) and the executive overview's commitments: a
verified, production-credible DX UIM slice and a measured savings
baseline. Started week of 20 July 2026; 11 weeks to Wed 30 Sep 2026,
one buffer week held in reserve.

Living document: tick the Status column weekly (Friday), name
slippage explicitly — slipped work moves into the buffer, nothing
slips silently.

## Plan

| Wk | Dates | Phase | Focus | Key tasks | Exit criterion | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 20–24 Jul | Discovery | DX UIM discovery | Discovery of DX UIM for **process and log monitoring** (probes, config keys, API behavior) | Enough understanding of `processes`/`logmon` to author real configs | ✅ Done |
| 2 | 27–31 Jul | Baseline | Savings baseline + access | Export monitoring-request tickets (HPSM/ServiceNow), run `tools/compute_savings.py`, put measured figures in `overview.md`; start one-week chat/call sample; confirm DX UIM UAT credentials, Bitbucket webhook admin, Backstage & Grafana access + versions | Measured savings sentence in `overview.md`; access confirmed or escalated | ⬜ |
| 3 | 3–7 Aug | Decisions | Open decisions + design review | Decide ELK watcher-sync home (fold in / own repo / retire) — stale OneDrive mirror deleted or superseded; confirm Grafana ⇄ DX UIM data source or formally descope the `TODO` panels; review `architecture/domain-model-transform-design.md` and decide its §10 questions (file layout Option A/B, schema ownership, legacy coexistence); record all in `backlog.md` + `architecture.md` | No `[decision needed]` items in the backlog; transform design status moves Proposed → Decided | ⬜ |
| 4 | 10–14 Aug | Verify | Real Bitbucket fetch path | Push config tree to real `dxuim-configs` repo (project `SRE`); run all three trigger modes (poll / single-file / commit-range) against real Bitbucket with PUT still at the stub; test `limit=1000` pagination behavior on a bulk commit | All three trigger modes proven against real Bitbucket | ⬜ |
| 5 | 17–21 Aug | Verify | Real DX UIM UAT + webhook | Point sync at real UAT DX UIM; re-apply `processes.json` (idempotent), confirm probe reflects it; wire real `repo:refs_changed` webhook, fire end-to-end from a merged PR; fix TLS verify or accept as UAT-only debt with PROD gate | Merged PR → live config on real UAT DX UIM, hands-off | ⬜ |
| 6 | 24–28 Aug | Verify | Backstage & Grafana assumptions | Verify Notifications API request shape on installed Backstage, fix `notify_requester` if needed, send real success + failure; verify Grafana annotation keys and `InfoCard`/`SidebarItem` assumptions; register `catalog-info.yaml`, confirm robot's portal page renders | Every Hardening "unverified assumption" verified or fix in flight | ⬜ |
| 7 | 31 Aug–4 Sep | Build | Real `cdm.json` | Author real CPU/disk/memory thresholds for `ulaeiapos0a` with the app team; commit via real PR flow; activate on UAT; forced-breach test; record the verified CDM key structure — it clears the transform design's §7 gate for the CMD mapping | CDM alerts live and firing via the Portal pipeline; CMD keys documented | ⬜ |
| 8 | 7–11 Sep | Build | Real `logmon.json` | Real log paths + keywords for `ulaeiapos0a` (uses W1 discovery); PR flow, activation, forced-match test; record the verified logmon key structure (transform design §7 gate for the Log mapping); build the two DX UIM Grafana panels if W3 decision was positive, else confirm descope note | First robot fully monitored (process + CMD + log), none hand-done; logmon keys documented | ⬜ |
| 9 | 14–18 Sep | Audit | Provenance | Add `changeRecordId` to metadata convention (`guide.md`, `data/data-model.md`), thread through `notify_requester`; confirm `sourceTaskId` timeline with ELK/backstage — consume or stub + document; update spec with W4–W8 learnings | Merged PR carries durable link to its change record | ⬜ |
| 10 | 21–25 Sep | Buffer | Reserved for slippage | Absorb slip from W4–W9 (likely causes: access, firewall, app-team availability). If unused: full no-args re-sync as drift-repair drill; pre-write milestone report | Buffer consumed intentionally or drill done | ⬜ |
| 11 | 28–30 Sep | Close | Milestone close (3 days) | Final full re-sync, verify git ⇄ reality agreement; update `milestones.md`, `backlog.md`, `architecture.md` §8; stakeholder report: verified scope, measured savings, proposed next milestone (ELK slice + domain-model transform Phase 1 per `architecture/domain-model-transform-design.md` §8 — by then designed, decided, and with its CMD/Log gates cleared in W7–W8) | Milestone reported closed with evidence | ⬜ |

## External dependencies (tracked, not owned)

| Dependency | Owner | Needed by | Fallback |
| --- | --- | --- | --- |
| DX UIM UAT API credentials & network path | Platform team | W5 | Slip to buffer; escalate in W2 |
| Bitbucket webhook to Ansible host (firewall) | Platform/network | W5 | Poll mode is production-viable interim |
| Installed Backstage + Grafana access | Portal team | W6 | Verify against same versions in a sandbox |
| App-team input on CDM thresholds & log keywords | App owners | W7–W8 | Start with platform-recommended defaults, tune later |
| `sourceTaskId` sent by wizard | ELK/backstage | W9 | Stub the consumption point, document |

## Principles

- **Decisions first** — open decisions are scheduled early (W3);
  they're cheap to make and expensive to leave open.
- **Verify before build** — W4–W6 test today's claimed-working pieces
  against the real installed systems before new content (W7–W8) goes
  on top.
- **Out of scope stays out** — `[ELK/backstage]`-owned items and the
  Asset Registry are tracked as dependencies, not planned work
  (`scope.md`).

## Weekly cadence

- Monday: 15-minute plan check against this table; blockers named.
- Friday: set the week's Status (✅ done / ⚠️ partial → buffer /
  ❌ slipped → buffer) and adjust downstream rows if needed.
