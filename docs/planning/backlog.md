# Backlog

Every item here came up as a real, specific gap while building the
thing next to it — none of this is speculative. Each item is tagged
with which repo it belongs to.

## Hardening what's already live

- **[octopod]** Bitbucket `compare/changes` pagination caps at
  `limit=1000` with no follow-up paging. A single push touching more
  than 1000 files across the estate would silently drop the rest.
  Unlikely at current scale (a robot's commit touches at most 3
  files), but worth fixing before assuming it's safe.
- **[octopod]** `cdm.json` and `logmon.json` for `ulaeiapos0a` are
  still empty placeholders — CMD and Log monitoring aren't actually
  configured for the one real robot in the repo, only Process
  monitoring is.
- **[octopod]** Grafana annotation keys (`grafana/dashboard-selector`,
  `grafana/alert-label-selector`) and the Backstage Notifications API
  request shape were both built against my best understanding of
  common plugin conventions, flagged inline as needing verification
  against whatever's actually installed. Same for `InfoCard`'s
  `action` prop and the `SidebarItem` badge-via-children pattern in
  the app-shell code. None of this has been checked against a real
  running Backstage instance.

## Provenance & audit gaps

- **[octopod + ELK/backstage]** `changeRecordId` — the Infinity change
  validation step returns *something*, but nothing captures that
  reference into the committed domain model. Right now there's a real
  production change happening with no durable link back to the change
  record that approved it.
- **[ELK/backstage]** `sourceTaskId` — discussed but not built. Without
  it, a Backstage Notification ("Alert activated: X") has no way to
  link back to the original Scaffolder task page that created it.
- **[ELK/backstage]** Branch-naming collision — `staging/<name>` is
  derived only from asset identity, not the request itself. Two people
  requesting a change to the *same* container/robot concurrently would
  collide on one branch name. Same `sourceTaskId` value fixes both this
  and the notification-linking gap above in one move.

## DX UIM parity with the ELK side

- **[ELK/backstage]** There's no DX UIM Scaffolder template — the ELK
  side auto-generates `catalog-info.yaml` alongside every watcher
  config via `catalog:register`; DX UIM's `catalog-info.yaml` had to
  be hand-authored once, as a one-off. Ansible deliberately never
  writes git (see `mock/branching-strategy.html`), so this can't be
  patched from the octopod side — it needs a real Scaffolder template,
  mirroring `microservice-keyword-alert`.

## Domain model completeness

From the alert-metadata schema review — fields identified as missing,
not yet added anywhere:
- `matchType` (phrase / wildcard / regex) — log watchers hardcode
  phrase-match today.
- `comparisonOperator` (gt/gte/lt/lte) — CMD alerts implicitly assume
  "greater than," which doesn't fit e.g. "disk free space below X%."
  `aggregation` (avg/max/current) has the same gap.
- `lookbackWindow` — hardcoded `now-1m` in the ELK watcher template;
  should be a per-alert choice, not an infra default.
- `indexPattern` — currently derived (`logs-{namespace}-*`), never
  stored explicitly; worth confirming that derivation is never wrong.

## Visibility surfaces (designed, not built)

- **[ELK/backstage]** The Catalog "Configuration" tab — a rendered,
  human-readable view of the domain model, backed by a server-side
  Bitbucket-read proxy (never call Bitbucket directly from the
  browser). Shares its fetch/render logic with the next item.
- **[ELK/backstage]** The wizard's "existing configuration for this
  asset" summary card, and the same context embedded in the PR
  description for the approver. Open design question: should an exact
  keyword+severity duplicate warn, or just inform?
- **[octopod]** The DX UIM side of the Grafana overview dashboard is a
  `TODO` placeholder — real panels need a confirmed DX UIM → Grafana
  data source before they can be built for real.
