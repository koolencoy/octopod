# Documentation index

Suggested reading order for anyone new to octopod. Remember the scope
boundary: octopod is only the DX UIM automation slice of the wider
Observability Portal program — `planning/overview.md` explains what
lives where.

## 1. Orientation

- `planning/overview.md` — what octopod is, what's live today, and
  where it sits inside the wider observability program. **Read first.**
- `../README.md` — repo map and the end-to-end flow in brief.

## 2. Design

- `design/branching-strategy.md` — the git/branching model the whole
  pipeline assumes (`main` = truth, `staging/<name>` = per-request
  branch, PR = approval gate, Ansible never writes git). Load-bearing:
  code comments and specs reference it.
- `design/mockups/backstage-catalog-v2.html` — current "Raise an
  Alert" wizard + catalog mockup (v2 is the live iteration;
  `backstage-catalog.html` / `-dark.html` are earlier versions kept
  for reference).
- `design/assets/` — logo/branding assets.

## 3. Specification

- `spec/raise-an-alert-domain-model.md` — Draft v0.1 domain data model
  for alert requests: the human-reviewable middle layer between the
  wizard's form input and DX UIM's native `probeConfigKeys` wire
  format. Spec'd but not yet enforced by Ansible.

## 4. Operations

- `../dxuim-config/guide.md` — the DX UIM API call the sync is built
  on, plus the `metadata` and `catalog-info.yaml` file conventions.
  Kept next to the config tree it describes.

## 5. Project management

- `planning/milestones.md` — current milestone: **DX UIM base
  hardening, due 30 September 2026**, with explicit in/out-of-scope
  lists.
- `planning/backlog.md` — every open gap, each tagged with the repo it
  belongs to (`[octopod]` vs `[ELK/backstage]`).
