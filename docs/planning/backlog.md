# Backlog

Every item here came up as a real, specific gap while building the
thing next to it — none of this is speculative. Each item is tagged
with which repo it belongs to.

## Scope decision needed

- **[decision needed]** `ELK/ansible/` (OneDrive, not a git repo) is a
  **stale, pre-cleanup mirror** of what octopod's `ansible/` used to
  contain before the ELK-watcher role was removed from this repo. It
  still references `bitbucket_repo_slug: elk-watchers`,
  `bitbucket_branch: staging` (should be `main`), the old `ocbc`
  naming, and none of the hardening fixes from M1 (`roles_path`,
  `stdout_callback`, the `group_vars` relocation). It needs one of:
  fold it back into this repo (now that octopod is the overall
  Observability Portal, an ELK watcher-sync role next to
  `dxuim_config_sync` is a natural shape), promote it into its own
  git repo (one-repo-per-backend, matching
  `docs/ui-ux-design/branching-strategy.md`), or explicitly retire it if
  ELK watcher sync isn't being pursued right now. Leaving it as a
  silently-rotting copy is the one option that's actually wrong.
- **[decision needed]** The Asset Catalog & Scoring spec
  (`ELK/ELK-Asset-Catalog-Entity-Model-and-Scoring-Spec.md`, drafted
  2026-06-20) is a full separate workstream — ServiceNow CMDB entity
  provider, ~20,000 hosts, Tech Insights fact retriever + checks +
  scorecard. This is what "Asset Registry" actually means at full
  scope, and it is **not** something octopod's DX UIM automation
  overlaps with or covers. Track it as its own milestone stream, not
  folded into this repo's backlog.

## Hardening what's already live (DX UIM)

- **[octopod]** Bitbucket `compare/changes` pagination caps at
  `limit=1000` with no follow-up paging. Unlikely to matter at current
  scale (a robot's commit touches at most 3 files), but unverified
  past that ceiling.
- **[octopod]** `cdm.json` and `logmon.json` for `ulaeiapos0a` are
  still empty placeholders — CMD and Log monitoring aren't configured
  for the one real robot in the repo, only Process monitoring is.
- **[octopod]** Grafana annotation keys, the Backstage Notifications
  API request shape, `InfoCard`'s `action` prop, and the `SidebarItem`
  badge-via-children pattern were all built against best
  understanding, flagged inline as unverified against whatever's
  actually installed.

## Provenance & audit gaps

- **[octopod + ELK/backstage]** `changeRecordId` — the Infinity change
  validation step returns *something*, but nothing captures that
  reference into the committed domain model. A real production change
  is happening with no durable link back to what approved it.
- **[ELK/backstage]** `sourceTaskId` — not built. Without it, a
  Backstage Notification has no way to link back to the originating
  Scaffolder task page.
- **[ELK/backstage]** Branch-naming collision — `staging/<name>` is
  derived only from asset identity, not the request itself; two
  concurrent requests for the same container/robot would collide on
  one branch name. The same `sourceTaskId` fixes this and the
  notification-linking gap in one move.

## DX UIM parity with the ELK side

- **[ELK/backstage]** No DX UIM Scaffolder template exists — the ELK
  side auto-generates `catalog-info.yaml` alongside every watcher
  config; DX UIM's was hand-authored once as a one-off. Since Ansible
  deliberately never writes git, this can only be fixed with a real
  Scaffolder template mirroring `microservice-keyword-alert`.

## Domain model completeness

Schema now drafted — `docs/spec/raise-an-alert-domain-model.md`. The items
below are the fields that spec adds; what's still open is *implementing*
the transform (Ansible currently reads/passes through DX UIM's native
`probeConfigKeys` almost as-is, not this domain model) and, for the ELK
side, that CMD/Process have no defined target-system mapping at all yet
(spec §8.2).

- `matchType` (phrase / wildcard / regex) — log watchers hardcode
  phrase-match today.
- `comparisonOperator` (gt/gte/lt/lte) and `aggregation`
  (avg/max/current) — CMD alerts implicitly assume "greater than,
  instantaneous," which doesn't fit e.g. disk-free-space checks.
- `lookbackWindow` — hardcoded `now-1m` in the ELK watcher template;
  should be a per-alert choice.
- `indexPattern` — currently derived, never stored explicitly.

## Visibility surfaces (designed, not built)

- **[ELK/backstage]** Catalog "Configuration" tab, backed by a
  server-side Bitbucket-read proxy (never call Bitbucket directly from
  the browser).
- **[ELK/backstage]** Wizard + PR-description "existing configuration"
  summary. Open question: should an exact keyword+severity duplicate
  warn, or just inform?
- **[octopod]** DX UIM side of the Grafana overview dashboard is a
  `TODO` — needs a confirmed DX UIM → Grafana data source first.
