# octopod

The **DX UIM (Open Systems) automation backend** of the Observability
Portal — the internal developer platform built on **Backstage**
(self-service front end), **Bitbucket** (config-as-code source of
truth, PR = approval gate), and **Ansible** (execution engine).

octopod owns one slice of that platform: taking approved DX UIM probe
configurations out of Bitbucket and activating them on the Broadcom DX
UIM probe config API, then telling the requester what happened. The
Backstage app itself and the ELK/Elasticsearch side live in separate
projects — see `docs/planning/overview.md` for the scope boundary.

## How it works

1. An engineer raises an alert through the Observability Portal's
   "Raise an Alert" wizard (Backstage Scaffolder).
2. The config is committed to a per-request `staging/<env>-<robot>`
   branch; a PR into `main` is the approval gate. `main` is production
   truth. (Full model: `docs/design/branching-strategy.md`.)
3. On merge, a Bitbucket webhook triggers Ansible
   (`ansible/playbooks/sync-dxuim-config.yml`), which reads the changed
   config and PUTs it to
   `uimapi/probes/{domain}/{hub}/{robot}/{probe}/config`.
4. Success or failure is reported back to the requester via Backstage
   Notifications (`ansible/roles/notify_requester`).

Ansible only ever **reads** from Bitbucket — it never commits back.

## Repository map

| Path | What it is |
| --- | --- |
| `ansible/` | The automation: playbooks, `dxuim_config_sync` and `notify_requester` roles, inventory |
| `dxuim-config/` | Probe config data tree, `{ENV}/{robot}/{probe}.json` — see `dxuim-config/guide.md` for conventions |
| `dxuim-stub/` | Local Python stub of the DX UIM API for end-to-end testing |
| `grafana/` | Entity + overview alerting dashboards (JSON models) |
| `docs/planning/` | Scope, milestones, backlog — start at `overview.md` |
| `docs/spec/` | "Raise an Alert" domain data model (Draft v0.1) |
| `docs/design/` | Branching-strategy design doc, Backstage UI mockups, logo assets |

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
