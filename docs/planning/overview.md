# Planning — octopod

This folder tracks open work for octopod specifically. Read this
first — the scope boundary matters, because octopod sits inside a
much larger program and it's easy to conflate the two.

## Where octopod fits in the bigger picture

`C:\Users\Admin\OneDrive\Documents\Claude\Projects\ELK` is the wider
observability program this repo is one piece of — real production
Logstash/Elasticsearch config (ILM policies, index templates, per-app
security roles), a drafted Asset Catalog & Scoring spec (ServiceNow
CMDB → Backstage `Resource` entities → Tech Insights scoring across
~20,000 hosts), an alert-inventory TechDocs prototype, and a long
history of architecture/exec decks. Most of that is **out of scope
for octopod** and shouldn't be assumed covered by anything in this
folder.

**octopod's actual scope, as of the most recent instruction**: the DX
UIM (Open Systems) automation backend only. The ELK/Elasticsearch
watcher-sync role that used to live in this repo's `ansible/` was
deliberately removed — that automation still exists, but currently
only as a stale mirror at `ELK/ansible/` (not this repo, not a git
repo at all yet, and out of date — see backlog).

## What's actually live in octopod today

- `ansible/roles/dxuim_config_sync` — reads DX UIM probe config from
  Bitbucket (poll, single-file, or commit-range mode) and PUTs it to
  the real `uimapi/probes/{domain}/{hub}/{robot}/{probe}/config`
  endpoint. Verified end-to-end against `dxuim-stub/` with real
  Ansible (WSL), not simulated.
- `ansible/roles/notify_requester` — success/failure notification via
  Backstage Notifications, generic enough to be reused by a future
  sync role.
- One real robot registered: `dxuim-config/UAT/ulaeiapos0a/` — only
  `processes.json` has real content; `cdm.json` and `logmon.json` are
  still empty placeholders.
- `grafana/` — entity + overview dashboards; DX UIM panels are
  explicit `TODO` placeholders pending a confirmed data source.
- `mock/branching-strategy.html` — the branching model this pipeline
  assumes (`main` = truth, `staging/<name>` = per-request, PR =
  approval gate).

## What depends on the separate `ELK/backstage` project

The Backstage app itself (Scaffolder templates, the "Raise an Alert"
wizard, the app-shell TypeScript) lives outside this repo. Several
backlog items below need changes there, not here — each is tagged
with which repo it belongs to.
