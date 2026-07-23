# Overview — octopod, the Observability Portal

octopod is the **Observability Portal**: the self-service window
between developers/engineers and the Observability Platform team — the
"yellow pages" for everyone who needs monitoring, alerting, or
dashboards. Built on Backstage (catalog + wizards), Bitbucket
(config-as-code, PR = approval), and Ansible (execution).

## The problem being solved

Two decades of interrupt-driven operations:

- **People ping and call the engineer.** Every alert request, every
  onboarding, every "is this monitored?" question routes through a
  human on the platform team. The team's capacity is spent on toil,
  not on the platform.
- **Documentation drift.** Inventories and runbooks live apart from
  the systems they describe, so they rot the moment they're written.
  Nobody trusts them; people go back to pinging the engineer.

The Portal's answer, respectively: **self-service** (wizard → PR
approval → automated activation → notification — no human in the loop
except the approver) and **a living catalog** (every monitored asset
is a Backstage catalog entity with an owner, lifecycle, and its
current config; the catalog *is* the inventory).

## The tool estate (all on-premises)

The Observability Platform is not one tool. The Portal fronts all of
them behind one experience:

| Tool | Role | Portal automation status |
| --- | --- | --- |
| DX UIM (Broadcom) | Open Systems infra monitoring (process/CMD/log probes) | **Live — this repo.** Sync verified end-to-end against `dxuim-stub/` |
| ELK Stack | Log ingestion, keyword watchers/alerts | Drafted in the ELK project: watcher-sync Ansible role + `microservice-keyword-alert` Scaffolder template. Consolidation into octopod is an open decision (see backlog) |
| Grafana | Dashboards & visualization | `grafana/` dashboard models here; DX UIM data source unconfirmed (`TODO` panels) |
| SolarWinds | Network monitoring | Not started — future backend slice, same wizard → PR → Ansible pattern |

Every backend follows one pattern: **wizard → per-request branch → PR
gate → webhook → Ansible reads Bitbucket → PUT to the tool's API →
notify the requester.** DX UIM is the first slice delivered end to
end; the rest of this document describes it concretely.

## The DX UIM slice, concretely

1. **Request** — an engineer fills the "Raise an Alert" wizard
   (Backstage Scaffolder; app code currently lives in the ELK
   project — no DX UIM template exists yet, so today the config files
   are hand-authored, see backlog).
2. **Commit** — the config goes to a per-request branch
   `staging/<environment>-<robot>` off `main` in project `SRE`, repo
   `dxuim-configs` on `bitbucket.acbc.internal`. A PR into `main` is
   the approval gate; `main` is production truth. Full model:
   `docs/ui-ux-design/branching-strategy.md`.
3. **Trigger** — on merge, Bitbucket's `repo:refs_changed` webhook
   fires `ansible/playbooks/sync-dxuim-config.yml` with the merge's
   `fromHash`/`toHash`. Two fallback modes exist: single-file
   (`changed_file_path`) and full-tree poll (no vars).
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
  owner, lifecycle, and Grafana tab — the "yellow pages" entry.
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

## Where the plan lives

- `milestones.md` — current milestone: **DX UIM base hardening, due
  30 September 2026**, with explicit in/out-of-scope lists.
- `backlog.md` — every open gap, tagged by owning repo/workstream.
- `docs/spec/raise-an-alert-domain-model.md` — Draft v0.1 of the
  domain model that will replace raw `probeConfigKeys` as the
  committed format; not yet implemented in Ansible.
