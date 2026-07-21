# Milestones

Sequenced by dependency, not by calendar date — add target dates once
these are prioritized against everything else in flight. Each
milestone links back to `backlog.md` items rather than repeating them.

## M1 — Verify what's already claimed to work

Nothing here is new build; it's closing the "unverified" flags before
trusting this in a real environment.
- Confirm Grafana annotation keys against the actual installed plugin
- Confirm the Backstage Notifications API request shape
- Confirm `InfoCard`/`SidebarItem` assumptions in the app-shell code
- Fill in real `cdm.json` / `logmon.json` for `ulaeiapos0a`, so there's
  a second and third real example beyond `processes.json`

**Why first:** everything downstream assumes these primitives behave
as documented. Building more on top of an unverified assumption just
means more places to fix when it turns out wrong.

## M2 — Provenance & audit

- Add `changeRecordId` to the metadata convention (both backends)
- Thread `sourceTaskId` through Scaffolder → commit → notification
- Fix the branch-naming collision using the same `sourceTaskId`

**Why second:** this is a real production system creating real alert
configs with no durable link back to what approved them. That's a
compliance gap, not a nice-to-have, and it's cheap to fix now while
there's still only one real robot's worth of history to reconcile.

## M3 — DX UIM Scaffolder template

Mirror `microservice-keyword-alert` for the DX UIM side — generates
the probe config *and* `catalog-info.yaml` together, same as ELK
already does.

**Why third:** everything in M1/M2 is easier to retrofit once there's
only one path (the template) generating DX UIM configs, instead of
the current hand-authored one-off plus whatever comes next.

## M4 — Domain model completeness

`matchType`, `comparisonOperator`, `aggregation`, `lookbackWindow`,
`indexPattern` — promote each from "hardcoded assumption" to an actual
field.

**Why fourth:** these are additive and backward-compatible (existing
configs keep working with the current hardcoded defaults), so there's
no urgency forcing this ahead of the provenance/template work above.

## M5 — Visibility surfaces

- Backstage Configuration tab + backend Bitbucket-read proxy
- Wizard + PR-description "existing configuration" summary
- Real DX UIM datasource wired into the Grafana overview dashboard

**Why last:** these are UX quality-of-life, not correctness or audit
gaps. Worth doing, but nothing downstream depends on them.
