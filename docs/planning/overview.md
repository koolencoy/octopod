# Planning — octopod

This folder tracks open work for the Observability Portal automation
backend: what's live, what's a known gap, and the order to close them
in. See `backlog.md` for the itemized list and `milestones.md` for how
it's sequenced.

## What's actually live today

- `ansible/roles/dxuim_config_sync` — reads DX UIM probe config from
  Bitbucket (poll, single-file, or commit-range mode) and PUTs it to
  the real `uimapi/probes/{domain}/{hub}/{robot}/{probe}/config`
  endpoint. Verified end-to-end against `dxuim-stub/` with real
  Ansible (WSL), not just simulated.
- `ansible/roles/notify_requester` — success/failure notification via
  Backstage Notifications, wired into the sync role's block/rescue.
- One real robot registered: `dxuim-config/UAT/ulaeiapos0a/` — only
  `processes.json` has real content; `cdm.json` and `logmon.json` are
  still empty placeholders.
- `grafana/` — two dashboards (entity detail, overview), Elasticsearch
  side is real, DX UIM side is an explicit `TODO` placeholder.
- `mock/branching-strategy.html` — the branching model this whole
  pipeline assumes (`main` = truth, `staging/<name>` = per-request,
  PR = approval gate).

## What's NOT in this repo

The Backstage app itself (Scaffolder templates, the app-shell
TypeScript, the "Raise an Alert" wizard mock) lives in the separate
`ELK/backstage/` project. Several backlog items below require changes
there, not here — each item says which repo it belongs to.
