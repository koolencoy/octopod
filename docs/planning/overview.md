# Executive Overview — octopod, the Observability Portal

**One line:** a self-service portal that lets any engineer request,
approve, and activate monitoring across our observability tools —
without calling the platform team, and without documentation that
rots.

## The problem

For roughly twenty years, observability has run on interrupt-driven
operations. The pattern is always the same:

- **Every request is a conversation.** Anyone who needs an alert, a
  dashboard, or an answer to "is this monitored?" pings or calls a
  platform engineer. The engineer stops what they're doing, does the
  work by hand in the relevant tool, and moves to the next
  interruption. Requesters wait on a queue that is really a person.
- **Documentation drifts.** Inventories, runbooks, and "who owns
  this" lists are written apart from the systems they describe, so
  they are stale almost immediately. Nobody trusts them — so people
  go back to pinging the engineer, which is how the cycle sustains
  itself.
- **Approvals and audit are informal.** Changes made by hand on a
  monitoring tool leave no reviewable record of who asked, who
  approved, and what exactly changed.

The cost is paid three ways: platform engineers spend their capacity
on repetitive toil instead of platform work; requesters wait days for
what is minutes of actual change; and the organization carries audit
and knowledge-concentration risk (the inventory lives in a few
people's heads).

## The resolution

octopod turns the manual conversation into a governed, automated
pipeline, using tools we already run — nothing new is licensed:

1. **Self-service request** — the engineer describes the alert they
   need in a wizard (Backstage), instead of describing it to a human.
2. **Approval as a pull request** — the request becomes a reviewable
   change in Bitbucket; the approver merges it. The merge *is* the
   approval, and git *is* the audit trail: who asked, who approved,
   what changed, when.
3. **Automated activation** — Ansible picks up the approved change
   and configures the monitoring tool (DX UIM today; ELK next;
   SolarWinds planned — all on-premises). The requester is notified
   of success or failure automatically.
4. **A living catalog** — every monitored asset is registered in the
   Portal with its owner and current configuration. The catalog *is*
   the inventory — the "yellow pages" — generated from the same files
   that drive the tools, so it cannot drift from reality.

The only human step left is the one that must stay human: approval.

## Benefits

| Benefit | Mechanism |
| --- | --- |
| Platform capacity reclaimed | Repetitive configuration work is removed from engineers entirely; they handle approvals and exceptions only |
| Faster turnaround | Requests complete in minutes after approval, not days on a queue — no waiting on an engineer's availability |
| Audit & compliance by construction | Every change is a reviewed, merged PR with requester, approver, and diff permanently recorded |
| Documentation that cannot drift | The catalog is generated from the same config that drives the tools — always current, zero upkeep |
| Consistency across tools | One request pattern for DX UIM, ELK, Grafana, and SolarWinds — no per-tool tribal knowledge needed |
| Reduced key-person risk | The process, inventory, and conventions live in git and the Portal, not in individuals' heads |
| No new license spend | Built on Backstage (open source) plus the Bitbucket, Ansible, and monitoring tools already in place |

## Savings

The savings model is simple to state and easy to baseline from our
own ticket/chat volume — the formula, with our numbers to be filled
in:

```
monthly savings = requests/month × engineer-minutes per request × loaded rate
                + requester wait-time cost avoided
                + audit-preparation effort avoided
```

Illustrative only (replace with measured figures): at 100 alert
requests a month averaging 45 engineer-minutes of hands-on work each,
self-service returns ~75 engineer-hours a month — roughly half an FTE
— before counting the requesters' waiting time or audit preparation.

Two further savings are real but harder to price:

- **Avoided incidents.** Stale inventories mean assets people assume
  are monitored sometimes aren't. A trustworthy catalog closes the
  gap between "believed monitored" and "actually monitored."
- **Onboarding.** New team members learn one portal, not four tools'
  worth of tribal process.

**Recommended before scaling out:** measure the baseline (requests
per month and average handling time from tickets/chat) for one
quarter, so savings are reported as measured fact rather than
estimate.

## Where we are

The DX UIM (Open Systems) slice is built end-to-end and verified
against a test stub: wizard-authored config → PR approval → automated
activation → requester notification. Current milestone: **DX UIM base
hardening, due 30 September 2026** — verifying remaining assumptions
against the installed systems and filling the first server's
remaining configs. ELK follows the same pattern next; SolarWinds is
planned.

## Read more

- `docs/architecture/architecture.md` — the full technical design,
  component status, and open risks.
- `milestones.md` / `backlog.md` — delivery plan and itemized gaps.
