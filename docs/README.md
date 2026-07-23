# Documentation index

Suggested reading order for anyone new to octopod — the Observability
Portal, the self-service window between engineers and the
Observability Platform team. DX UIM automation is the first delivered
backend slice; ELK, Grafana, and SolarWinds follow the same pattern —
`planning/overview.md` explains the vision and what lives where.

## 1. Orientation

- `planning/overview.md` — the executive overview: the problem
  (20 years of ping-the-engineer operations, documentation drift),
  how the Portal resolves it, and the benefits and savings case.
  **Read first.**
- `../README.md` — repo map and the end-to-end flow in brief.

## 2. Architecture

- `architecture/architecture.md` — how the platform works end to end:
  the Backstage → Bitbucket → Ansible flow, the one-way GitOps rules,
  the git/branching model the whole pipeline assumes (§4.1: `main` =
  truth, `staging/<name>` = per-request branch, PR = approval gate,
  Ansible never writes git), per-target status (DX UIM built, ELK
  pending a home, SolarWinds not started), and the build-stage status
  matrix. Includes a terminology table for the DX UIM/Backstage jargon.

## 3. Design

- `ui-ux-design/mockups/backstage-catalog-v2.html` — current "Raise an
  Alert" wizard + catalog mockup (v2 is the live iteration;
  `backstage-catalog.html` / `-dark.html` are earlier versions kept
  for reference).
- `ui-ux-design/assets/` — logo/branding assets.

## 4. Specification

- `spec/raise-an-alert-domain-model.md` — Draft v0.1 domain data model
  for alert requests: the human-reviewable middle layer between the
  wizard's form input and DX UIM's native `probeConfigKeys` wire
  format. Spec'd but not yet enforced by Ansible.

## 5. Data

- `data/data-model.md` — the key contracts the automation runs on
  (Bitbucket coordinates, config layout, hub lookup, DX UIM API,
  file shape, notifications endpoint) and the committed file format,
  today (`probeConfigKeys` wire format) and tomorrow (the
  tool-neutral domain model).

## 6. Operations

- `../dxuim-config/guide.md` — the DX UIM API call the sync is built
  on, plus the `metadata` and `catalog-info.yaml` file conventions.
  Kept next to the config tree it describes.

## 7. Project management

- `planning/scope.md` — what is in scope now, in scope later, and
  out of scope (with where out-of-scope work actually lives). Scope
  changes by PR to that file.
- `planning/milestones.md` — current milestone: **DX UIM base
  hardening, due 30 September 2026**, with the current-state baseline
  and explicit in/out-of-scope lists.
- `planning/execution-plan.md` — the week-by-week plan delivering
  that milestone (27 Jul → 30 Sep 2026): decisions first, verify
  against real systems, complete the first robot, provenance, buffer,
  close. Living document — exit criteria ticked weekly.
- `planning/backlog.md` — every open gap, each tagged with the repo it
  belongs to (`[octopod]` vs `[ELK/backstage]`).
