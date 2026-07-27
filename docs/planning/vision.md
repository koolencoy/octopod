# Vision — A Fresh New Page for Observability

*For senior executives. Companion: `overview.md` (the executive
overview: problem, resolution, benefits, savings).*

## The moment we are in

For more than a decade, observability has run the same way: when
someone needs an alert, a dashboard, or an answer to "is this system
monitored?", they find an engineer and ask. The engineer does the
work by hand, in one of several tools, and moves to the next request.
The knowledge of what is monitored — and how, and why — lives in a
few people's heads and in documents that go stale the week they are
written.

This worked when the estate was small. It does not scale to thousands
of hosts, hundreds of applications, and four monitoring tools — and
it quietly costs us every day: senior engineers doing repetitive
configuration instead of engineering, teams waiting days for
minutes of work, and an audit story that depends on memory rather
than records.

## The vision

**One portal — the front door and the yellow pages of observability.**

Any engineer, in any team, opens the Observability Portal and can:

- **See** every monitored asset, who owns it, and exactly what
  monitoring it has — live, trusted, never stale.
- **Ask** for what they need through a guided wizard — a new alert, a
  threshold change — in minutes, without knowing which tool serves it
  or who to call.
- **Trust** that every change was approved, is on record forever, and
  was activated automatically the moment it was approved.

The platform team stops being a queue and becomes what its name says:
a team that builds and runs a platform. The tools we already own —
DX UIM, ELK, Grafana, SolarWinds, all on-premises — stay; what
changes is that they are driven by one governed, automated pipeline
instead of by hand.

## What turns the page

| For the past decade | From now on |
| --- | --- |
| Ping or call an engineer and wait | Self-service wizard; done in minutes after approval |
| Inventories and runbooks that drift | A living catalog generated from the same config that drives the tools |
| Hand-made changes, informal approvals | Every change is a reviewed, recorded, automatically-activated request |
| Four tools, four tribal processes | One portal, one request pattern, whatever the tool behind it |
| Knowledge in a few heads | Process and inventory in the platform, owned by everyone |

## Why this succeeds now

- **It is already working.** The first slice — infrastructure
  monitoring on DX UIM — runs end to end today: request, approval,
  automatic activation, confirmation back to the requester. This is
  not a concept; it is a working pipeline being hardened for
  production this quarter.
- **Nothing new to buy.** The Portal is built from what we already
  run — our monitoring tools, our git server, our automation — plus
  open-source Backstage. The investment is engineering focus, not
  licenses.
- **Each step pays for itself.** Every tool slice that onboards
  removes its share of manual requests immediately. A measured
  savings baseline (in progress) will report that in engineer-hours,
  not adjectives.

## What we are asking for

1. **Endorse the direction** — the Portal as the single front door
   for observability, and self-service as the default way of working.
2. **Hold teams to it** — new monitoring requests go through the
   Portal as slices come live, not around it.
3. **Protect the focus** — the platform team's capacity to finish the
   current milestone (30 September 2026) and onboard the next tool,
   rather than absorbing that capacity back into the queue the Portal
   is retiring.

A decade of operating one way is exactly why this matters: the
cost is so familiar it has become invisible. The Portal makes it
visible — and then removes it. That is the fresh page.
