# Scope — octopod, the Observability Portal

What this program does and does not cover. Three buckets: **in scope
now** (being delivered), **in scope, later** (committed direction,
not current work), and **out of scope** (belongs elsewhere — with
where it actually lives). Scope changes happen by PR to this file,
so the record of what changed and who agreed is the git history.

## In scope — now

- **Self-service alert lifecycle for DX UIM (Open Systems)**: raise
  via wizard → PR approval in Bitbucket → automated activation by
  Ansible → requester notified. The first delivered slice, being
  hardened to 30 Sep 2026 (`milestones.md`, `execution-plan.md`).
- **The config-as-code pattern itself**: one config repo per
  monitoring tool, `main` = production truth, `staging/<name>` per
  request, PR = approval gate, Ansible reads-only
  (`architecture.md` §4.1).
- **The living catalog for monitored assets**: every robot/asset
  registered via `catalog-info.yaml` with owner and lifecycle — the
  Portal "yellow pages." Hand-authored today, generated later.
- **Requester notifications** (success and failure) via Backstage
  Notifications — shared by every current and future tool slice.
- **Provenance & audit**: `requestedBy` / `approvedBy` today;
  `changeRecordId` and `sourceTaskId` consumption this milestone.
- **Grafana alerting dashboards** (entity + overview) for assets
  managed through the Portal.
- **The savings baseline**: measuring the manual-request volume the
  Portal replaces (`savings-baseline.md`).

## In scope — later (committed direction, not current work)

- **ELK Stack slice**: watcher-sync automation exists but needs a
  home (decision scheduled W2 of the execution plan); ELK
  CPU/memory/process alerting has no designed mechanism yet.
- **SolarWinds slice**: not started; follows the established pattern
  (own config repo, own role, shared notifications). Four pre-build
  decisions listed in `architecture.md` §6.3.
- **Tool-neutral domain model**: committed format becomes the
  drafted schema (`docs/spec/raise-an-alert-domain-model.md`);
  Ansible grows one translator per tool.
- **DX UIM Scaffolder template**: wizard-generated configs and
  `catalog-info.yaml` for Open Systems, retiring hand-authoring —
  blocked on the Backstage app side.

## Out of scope

- **The monitoring tools themselves** — operating, upgrading, or
  replacing DX UIM, ELK, SolarWinds, Grafana. The Portal automates
  their configuration; it does not run them.
- **Log ingestion pipelines** — the Logstash estate (~168 pipeline
  bundles), index templates, ILM policies. Owned by the ELK platform
  work, currently in the ELK project folder.
- **Asset Registry at full scope** — ServiceNow CMDB → Backstage
  entities → Tech Insights scoring across ~20k hosts. Its own
  workstream with its own drafted spec (in the ELK project); the
  Portal's catalog integrates with it but does not build it.
- **The Backstage app code** — Scaffolder templates, wizard UI,
  catalog UI, app theme. Currently owned in the ELK project;
  octopod items needing changes there are tagged `[ELK/backstage]`
  in the backlog.
- **Incident management** — paging, on-call rotas, ticket routing
  (PagerDuty/ITSM). The Portal creates alert configuration; what
  happens after an alert fires is unchanged.
- **Migration of pre-existing alerts** — the legacy alert estate
  configured by hand over the years is not being bulk-imported.
  Assets enter the Portal as new requests touch them. (Revisit once
  the DX UIM slice is hardened.)

## Why the boundary is drawn here

The milestone history (`milestones.md`) shows the failure mode this
file guards against: work belonging to other repos/workstreams being
silently counted into octopod's dates. If a task isn't in "in scope —
now," it doesn't go into the current milestone — it goes into this
file's later bucket, the backlog with an owner tag, or out.
