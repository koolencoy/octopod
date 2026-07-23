# octopod — the Observability Portal

octopod is the **Observability Portal**: the self-service window
between developers/engineers and the Observability Platform team — the
"yellow pages" for everything observability. It is built on
**Backstage** (catalog + self-service wizards), **Bitbucket**
(config-as-code, PR = approval gate), and **Ansible** (execution
engine).

## Why it exists

For the past ~20 years, observability has run on heavy, interrupt-
driven operations: anyone needing an alert, a dashboard, or an answer
pings or calls a platform engineer, and documentation drifts because
it lives apart from the systems it describes. The Portal replaces both
habits:

- **Self-service instead of calls** — requests go through wizards,
  approvals through PRs, activation through automation. No human in
  the loop except the approver.
- **A living catalog instead of drifting docs** — every monitored
  asset appears in the Backstage catalog with its owner, lifecycle,
  and current config. The catalog *is* the inventory; there is no
  separate document to keep in sync.

## The tool estate (all on-premises)

| Tool | Role | Portal automation today |
| --- | --- | --- |
| DX UIM (Broadcom) | Open Systems infrastructure monitoring | **Live in this repo** — config sync verified end-to-end against a local stub |
| ELK Stack | Log ingestion, keyword watchers/alerts | Drafted in the ELK project (watcher sync + Scaffolder template); consolidation pending |
| Grafana | Dashboards & visualization | Dashboard models in `grafana/`; DX UIM data source still TODO |
| SolarWinds | Network monitoring | Not started — future backend slice |

## How a request flows (DX UIM, the first delivered slice)

1. An engineer raises an alert through the Portal's "Raise an Alert"
   wizard (Backstage Scaffolder).
2. The config is committed to a per-request `staging/<env>-<robot>`
   branch; a PR into `main` is the approval gate. `main` is production
   truth. (Full model: `docs/architecture/architecture.md` §4.1.)
3. On merge, a Bitbucket webhook triggers Ansible
   (`ansible/playbooks/sync-dxuim-config.yml`), which reads the changed
   config and PUTs it to
   `uimapi/probes/{domain}/{hub}/{robot}/{probe}/config`.
4. Success or failure is reported back to the requester via Backstage
   Notifications (`ansible/roles/notify_requester`).

Ansible only ever **reads** from Bitbucket — it never commits back.
The same pattern (wizard → PR → webhook → Ansible → tool API →
notification) is the template for every other backend in the estate.

## Repository map

| Path | What it is |
| --- | --- |
| `ansible/` | The automation: playbooks, `dxuim_config_sync` and `notify_requester` roles, inventory |
| `dxuim-config/` | Probe config data tree, `{ENV}/{robot}/{probe}.json` — see `dxuim-config/guide.md` for conventions |
| `dxuim-stub/` | Local Python stub of the DX UIM API for end-to-end testing |
| `grafana/` | Entity + overview alerting dashboards (JSON models) |
| `docs/planning/` | Vision, scope, milestones, backlog — start at `overview.md` |
| `docs/spec/` | "Raise an Alert" domain data model (Draft v0.1) |
| `docs/ui-ux-design/` | Branching-strategy design doc, Backstage UI mockups, logo assets |

## Local dev loop

Runs the real payload-template + PUT logic against the stub, no
Bitbucket involved (from `ansible/`, under WSL or any host with
ansible-core):

```sh
python3 ../dxuim-stub/dxuim_stub_server.py &
ansible-playbook playbooks/test-dxuim-stub.yml \
  -e dxuim_api_base=http://127.0.0.1:8443 \
  -e vault_dxuim_password=devpass \
  -e vault_backstage_token=dummy \
  -e backstage_notifications_api=http://127.0.0.1:9/api
```

Real runs need vaulted secrets — copy
`ansible/inventory/group_vars/all/vault.yml.example` and supply the
vault password at runtime (`--vault-password-file` / `--ask-vault-pass`).

## Where to read next

`docs/README.md` is the documentation index with a suggested reading
order.
