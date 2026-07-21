# Milestones

## Next milestone: DX UIM base hardening — by 30 September 2026

This is scoped tightly to what **octopod itself** can actually deliver
by end of September. It deliberately excludes work that belongs to
other repos/workstreams — see "Explicitly not in this milestone"
below. Confusing those with octopod's own scope is the single easiest
way for this date to slip on work this repo was never going to
finish anyway.

### In scope

1. **Verify what's already claimed to work** (`backlog.md` → Hardening)
   - Confirm Grafana annotation keys against the actual installed plugin
   - Confirm the Backstage Notifications API request shape
   - Confirm the `InfoCard`/`SidebarItem` assumptions in the app-shell code
   - Fill in real `cdm.json` / `logmon.json` for `ulaeiapos0a`
2. **Provenance & audit** (octopod's half)
   - Add `changeRecordId` to the DX UIM metadata convention
   - Consume `sourceTaskId` once the Scaffolder side starts sending it
     (blocked on the ELK/backstage item below — track, don't own)
3. **Resolve the `ELK/ansible/` mirror decision** — promote to a real
   repo or explicitly retire it. Either answer is fine; leaving it
   silently stale is not.
4. **Grafana DX UIM data source** — get a confirmed answer on what
   actually bridges DX UIM into Grafana, so the two `TODO` panels can
   become real.

### Explicitly not in this milestone

- **Asset Registry at full scope** (ServiceNow CMDB entity provider,
  Tech Insights scoring across ~20k hosts) — a separate, larger
  workstream with its own drafted spec. Don't report this milestone's
  completion as if it includes Asset Registry progress.
- **ELK Elasticsearch watcher sync** — no longer part of octopod.
  Depends on the scope decision above; if promoted to its own repo,
  it gets its own milestone tracking there, not here.
- **The DX UIM Scaffolder template, the Configuration tab, the wizard
  "existing config" summary** — all `[ELK/backstage]`-tagged items.
  octopod depends on some of these eventually but doesn't own them.

## After this milestone

- **DX UIM Scaffolder template** (ELK/backstage) — once built, retire
  the hand-authored `catalog-info.yaml` convention in favor of
  generating it alongside every probe config, same as ELK does today.
- **Domain model completeness** — `matchType`, `comparisonOperator`,
  `aggregation`, `lookbackWindow`, `indexPattern`. Additive and
  backward-compatible, no urgency forcing this earlier.
- **Visibility surfaces** — Configuration tab, wizard/PR existing-config
  summary. UX quality-of-life; nothing else depends on these.
