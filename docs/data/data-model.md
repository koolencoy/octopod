# Data model — key contracts

The concrete values and file shapes the DX UIM automation runs on.
Non-secret runtime values have a single source of truth:
`ansible/inventory/group_vars/all/main.yml` — this page describes
them; that file defines them.

## Key contracts

| Contract | Value today |
| --- | --- |
| Bitbucket | `https://bitbucket.acbc.internal`, project `SRE`, repo `dxuim-configs`, branch `main` |
| Config layout | `dxuim-config/{ENV}/{robot}/{probe}.json` |
| Hub lookup | `dxuim_hub_by_environment` — `UAT: ulnstapor0a` only |
| DX UIM API | `https://1.1.1.1:8443` (UAT), user `accountsvcid`, PUT per probe |
| File shape | `probeConfigKeys` (wire format) + `metadata` (stripped before PUT) — see `dxuim-config/guide.md` |
| Notifications | `https://backstage.acbc.internal/api` |

Secrets (DX UIM password, Backstage token) come from Ansible Vault —
`ansible/inventory/group_vars/all/vault.yml.example` documents the
two variables.

## The committed file, today and tomorrow

- **Today** the committed probe config is DX UIM's native wire format:
  a `probeConfigKeys` array, plus a `metadata` sibling
  (`requestedBy` / `approvedBy`) that Ansible strips before the PUT
  and uses to address notifications. Conventions:
  `dxuim-config/guide.md`.
- **Tomorrow** the committed format becomes the tool-neutral domain
  model drafted in `docs/spec/raise-an-alert-domain-model.md`
  (Draft v0.1) — one document shape across Log/CMD/Process and both
  asset types, translated per target tool at activation time. The
  transform is specified but not yet implemented in Ansible.
