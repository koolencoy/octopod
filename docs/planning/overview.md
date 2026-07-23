# Overview — octopod

octopod is the **DX UIM (Open Systems) automation backend of the
Observability Portal**, the IDP built on Backstage + Bitbucket +
Ansible. Its one job: when an approved probe config lands on `main` of
the `dxuim-configs` Bitbucket repo, activate it on the DX UIM probe
config API and tell the requester whether that worked.

## The concrete flow

1. **Request** — an engineer fills the "Raise an Alert" wizard in the
   Observability Portal (Backstage Scaffolder; lives in the separate
   ELK/backstage project — no DX UIM template exists yet, so today the
   config files are hand-authored, see backlog).
2. **Commit** — the config goes to a per-request branch
   `staging/<environment>-<robot>` off `main` in project `SRE`, repo
   `dxuim-configs` on `bitbucket.acbc.internal`. A PR into `main` is
   the approval gate; `main` is production truth. Full model:
   `docs/design/branching-strategy.md`.
3. **Trigger** — on merge, Bitbucket's `repo:refs_changed` webhook
   fires `ansible/playbooks/sync-dxuim-config.yml` with the merge's
   `fromHash`/`toHash`. The playbook also supports two fallback modes:
   single-file (`changed_file_path`) and full-tree poll (no vars).
4. **Activate** — `dxuim_config_sync` reads the changed
   `{environment}/{robot}/{probe}.json` files over Bitbucket's REST
   API (never a clone), resolves the hub from
   `dxuim_hub_by_environment` (currently only `UAT: ulnstapor0a`;
   unknown environments fail loudly), strips the `metadata` block, and
   PUTs the `probeConfigKeys` to
   `{dxuim_api_base}/uimapi/probes/DXUIM/{hub}/{robot}/{probe}/config`.
5. **Notify** — `notify_requester` posts success/failure to the
   Backstage Notifications API, addressed to the `requestedBy` /
   `approvedBy` entity refs carried in each file's `metadata` block
   (files predating that convention sync fine but notify no one).

## What's live today, exactly

- **`ansible/roles/dxuim_config_sync`** — all three trigger modes
  implemented. Verified end-to-end against `dxuim-stub/` under real
  ansible-core on WSL (via `playbooks/test-dxuim-stub.yml`) — the
  payload template and PUT logic are exercised for real, the
  Bitbucket fetch path is not (no local Bitbucket to test against).
- **`ansible/roles/notify_requester`** — built, but the Notifications
  API request shape is unverified against a real Backstage install.
- **One registered robot**: `dxuim-config/UAT/ulaeiapos0a/`. Only
  `processes.json` has real content (3 process watchers);
  `cdm.json` and `logmon.json` are empty placeholders — CMD and Log
  monitoring for this robot do not exist yet.
- **`catalog-info.yaml` per robot** — hand-authored (once, for
  `ulaeiapos0a`) so the robot appears in the Portal's catalog with an
  owner, lifecycle, and Grafana tab. That catalog view *is* the alert
  asset inventory; there is no separate list to maintain.
- **`grafana/`** — entity + overview dashboards exist as JSON models;
  the DX UIM panels in them are `TODO` pending a confirmed
  DX UIM → Grafana data source.

## Key contracts (single source: `ansible/inventory/group_vars/all/main.yml`)

| Contract | Value today |
| --- | --- |
| Bitbucket | `https://bitbucket.acbc.internal`, project `SRE`, repo `dxuim-configs`, branch `main` |
| Config layout | `dxuim-config/{ENV}/{robot}/{probe}.json` |
| Hub lookup | `dxuim_hub_by_environment` — `UAT: ulnstapor0a` only |
| DX UIM API | `https://1.1.1.1:8443` (UAT), user `accountsvcid`, PUT per probe |
| File shape | `probeConfigKeys` (wire format) + `metadata` (stripped before PUT) — see `dxuim-config/guide.md` |
| Notifications | `https://backstage.acbc.internal/api` |

Secrets (DX UIM password, Backstage token) come from Ansible Vault —
`vault.yml.example` documents the two variables.

## Scope boundary — what octopod is not

octopod is one slice of the Observability Portal program. Explicitly
outside this repo:

- **The Backstage app itself** — Scaffolder templates, the wizard, the
  catalog UI. Lives in the ELK/backstage project; backlog items that
  need changes there are tagged `[ELK/backstage]`.
- **ELK Elasticsearch watcher sync** — deliberately removed from this
  repo. Survives only as a stale mirror at `ELK/ansible/` (OneDrive,
  not a git repo); promoting or retiring it is an open decision in the
  backlog.
- **Asset Registry at full scope** — the ServiceNow CMDB → Backstage →
  Tech Insights scoring workstream (~20k hosts) has its own drafted
  spec in the ELK project and is not covered by anything here.

## Where the plan lives

- `milestones.md` — current milestone: **DX UIM base hardening, due
  30 September 2026**, with explicit in/out-of-scope lists.
- `backlog.md` — every open gap, tagged by owning repo.
- `docs/spec/raise-an-alert-domain-model.md` — Draft v0.1 of the
  domain model that will replace raw `probeConfigKeys` as the
  committed format; not yet implemented in Ansible.
