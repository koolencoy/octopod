# Execution plan — to 30 September 2026

Week-by-week plan delivering the **DX UIM base hardening** milestone
(`milestones.md`) and the executive overview's commitments
(`overview.md`): a verified, production-credible DX UIM slice and a
measured savings baseline. 10 working weeks, Mon 27 Jul → Wed 30 Sep
2026, with one buffer week held in reserve.

Principles:

- **Decisions first.** Open decisions (ELK mirror home, Grafana data
  source) are scheduled in the first two weeks — they're cheap to make
  and expensive to leave open.
- **Verify before build.** Weeks 3–5 test today's claimed-working
  pieces against the *real* installed systems before new content is
  added on top.
- **Out of scope stays out.** `[ELK/backstage]`-owned items (DX UIM
  Scaffolder template, Configuration tab, `sourceTaskId` sending) and
  the Asset Registry are tracked as external dependencies, not planned
  work — per `milestones.md`.

## Phase 1 — Baseline & decisions (W1–W2)

### Week 1 · 27–31 Jul — Savings baseline + access checklist

- Export 3–12 months of monitoring-request tickets (HPSM/ServiceNow,
  platform team's queue) per `savings-baseline.md`; run
  `tools/compute_savings.py`; replace the illustrative figures in
  `overview.md` with measured ones.
- Confirm access needed by the verification sprint: DX UIM UAT API
  credentials work (`accountsvcid`), Bitbucket project `SRE` webhook
  admin rights, access to the installed Backstage and Grafana
  instances and their versions.
- Start a one-week chat/call sample count (requests that never became
  tickets) to complete the baseline.

**Exit:** measured savings sentence in `overview.md`; access confirmed
or escalated; installed versions of Backstage/Grafana recorded.

### Week 2 · 3–7 Aug — The two open decisions

- **ELK watcher-sync home** (backlog "scope decision needed"): decide
  fold-into-octopod / own repo / retire. Whichever way, the stale
  OneDrive `ELK/ansible/` mirror is deleted or superseded this week.
- **Grafana ⇄ DX UIM data source**: confirm with the platform team
  what actually bridges DX UIM metrics into Grafana (plugin, export,
  or none). If none exists, the two `TODO` panels are formally
  descoped to post-milestone and the dashboards note it.
- Record both decisions in `backlog.md` (close the items) and
  `architecture.md` §8/§9.

**Exit:** no `[decision needed]` items left in the backlog.

## Phase 2 — Verify against real systems (W3–W5)

### Week 3 · 10–14 Aug — Real Bitbucket fetch path

- Stand up (or get access to) the real `dxuim-configs` repo in
  project `SRE`; push the current `dxuim-config/` tree.
- Run `sync-dxuim-config.yml` in all three modes against real
  Bitbucket (poll, single-file, commit-range) with the PUT target
  still pointed at the stub — this exercises the one path the stub
  test never covered (`fetch_from_bitbucket.yml`).
- Verify the `limit=1000` compare/changes behavior on a bulk commit;
  either accept with a logged warning (current design) or implement
  paging now if the test shows silent truncation.

**Exit:** all three trigger modes proven against real Bitbucket.

### Week 4 · 17–21 Aug — Real DX UIM UAT + webhook wiring

- Point the sync at the real UAT DX UIM API; re-apply
  `processes.json` for `ulaeiapos0a` (idempotent PUT — safe) and
  confirm the probe actually reflects the config.
- Wire the real `repo:refs_changed` webhook from Bitbucket to the
  Ansible trigger; fire an end-to-end run from a merged PR.
- Fix TLS verification on the DX UIM call or formally accept it as
  UAT-only debt with a PROD gate noted (backlog/architecture §7).

**Exit:** merged PR → live config on real UAT DX UIM, hands-off.

### Week 5 · 24–28 Aug — Backstage & Grafana assumptions

- Verify the Backstage Notifications API request shape against the
  installed version; fix `notify_requester` if it differs; send real
  success and failure notifications.
- Verify the Grafana annotation keys and the `InfoCard`/`SidebarItem`
  assumptions flagged inline in the app-shell code; log fixes needed
  on the Backstage side as `[ELK/backstage]` items.
- Register `ulaeiapos0a`'s `catalog-info.yaml` in the installed
  Backstage catalog; confirm the robot's portal page renders.

**Exit:** every "unverified assumption" item in the backlog's
Hardening section is verified or has a concrete fix in flight.

## Phase 3 — Complete the first robot (W6–W7)

### Week 6 · 31 Aug–4 Sep — Real cdm.json (CPU/disk/memory)

- Author real CDM monitoring config for `ulaeiapos0a` with the app
  team (thresholds for CPU, disk, memory), commit via the real
  PR flow, activate on UAT, confirm alerts fire on a forced breach.

### Week 7 · 7–11 Sep — Real logmon.json (log monitoring)

- Same for log monitoring: real log paths + keywords for
  `ulaeiapos0a`, PR flow, activation, forced-match test.
- If the Grafana data source decision (W2) was positive, build the
  two DX UIM `TODO` panels now; otherwise confirm the descope note.

**Exit (phase):** the first robot is fully monitored — process, CMD,
and log — entirely through the Portal pipeline, none of it hand-done.

## Phase 4 — Provenance & audit (W8)

### Week 8 · 14–18 Sep

- Add `changeRecordId` to the DX UIM `metadata` convention
  (`guide.md`, `data/data-model.md`) and thread it through
  `notify_requester` output.
- Confirm with the ELK/backstage side when the wizard will send
  `sourceTaskId`; octopod consumes it if available, otherwise the
  consumption point is stubbed and documented (track, don't own).
- Update `docs/spec/raise-an-alert-domain-model.md` status notes with
  everything learned in W3–W7.

**Exit:** a merged PR carries a durable link to its change record;
audit chain documented end to end.

## Phase 5 — Buffer & close (W9–W10)

### Week 9 · 21–25 Sep — Buffer

Reserved for slippage from W3–W8 (external dependencies — access,
webhook firewall rules, app-team availability for thresholds — are
the likely causes). If unused: dry-run a full no-args re-sync as the
drift-repair drill, and pre-write the milestone report.

### Week 10 · 28–30 Sep — Milestone close (3 days)

- Final full re-sync; verify git ⇄ reality agreement.
- Update `milestones.md` (close), `backlog.md` (re-tag survivors),
  `architecture.md` §8 status matrix.
- Milestone report to stakeholders: verified scope, measured savings
  baseline (from W1), and the proposed next milestone — ELK slice
  onboarding per the W2 home decision, and the domain-model
  transform.

## External dependencies (tracked, not owned)

| Dependency | Owner | Needed by | Fallback |
| --- | --- | --- | --- |
| DX UIM UAT API credentials & network path | Platform team | W4 | Slip to buffer; escalate W1 |
| Bitbucket webhook to Ansible host (firewall) | Platform/network | W4 | Poll mode is production-viable interim |
| Installed Backstage + Grafana access | Portal team | W5 | Verify against versions in a sandbox |
| App-team input on CDM thresholds & log keywords | App owners | W6–W7 | Start with platform-recommended defaults, tune later |
| `sourceTaskId` sent by wizard | ELK/backstage | W8 | Stub the consumption point, document |

## Weekly cadence

- Monday: 15-minute plan check against this file; blockers named.
- Friday: tick the week's exit criterion here (edit this file — it is
  the living plan) and note slippage into the buffer explicitly.
