# The Second Brain — AI Use Cases and the Observability Score

**Status:** Proposed direction for the AI-DLC chapter (see
`vision.md`, "The next chapter"). Nothing here is being built yet —
this document exists so the use cases, the guardrails, and the
dependencies are agreed *before* the first AI feature starts, and so
the current build makes the right preparations.

**One line:** the Portal's config, docs, and history in Bitbucket form
a versioned, plain-text knowledge base — the *second brain*. This
document lists what AI tools can do with it, and how the Observability
Score becomes a natural-language guidance loop that pulls users into
self-service.

---

## 1. The two rules everything below follows

1. **AI proposes, humans approve, git records.** AI never writes to
   `main` and never touches a platform service directly. Its only
   write path is the same one humans use: a `staging/` branch and a
   PR through the existing approval gate. This rule is inherited from
   the architecture, not invented for AI — which is why AI adoption
   is safe by construction.
2. **Scores are math, guidance is language.** Anything presented as a
   *score* or *fact* is computed deterministically (rules over
   config-as-code and the CMDB — reproducible, comparable,
   auditable). AI's job is to *narrate*: explain what the number
   means, what's missing, and what to do next — always citing the
   facts, files, and PRs it drew from. An LLM never computes a score.

## 2. Use cases, in three tiers

Tiers are ordered by governance risk. Each tier stands alone; later
tiers build on earlier ones.

### Tier 1 — AI reads, humans ask (no write path; first to ship)

| Use case | What it looks like | Why the second brain enables it |
|---|---|---|
| Estate Q&A | "What monitoring does this system have, and why?" — answered with citations to config files and PRs | The config *is* the documentation; answers can't drift from reality |
| Provenance & audit answers | "Who approved this threshold, when, and what did it replace?" | Git history already records requester, approver, diff, date |
| Coverage & gap analysis | "Which PROD hosts have no process monitoring? Which have placeholder configs?" | Config repos + CMDB cross-reference; today this requires manually walking folders |
| Approver assistance | Plain-English PR summaries: "Adds CPU alert 90%/5min on host X; similar alert exists at 85% — possible duplicate" | Makes the approval gate stronger, not just faster; answers the wizard's open duplicate-handling question |

### Tier 2 — AI proposes, humans approve (write path via PRs; the AI-DLC core)

| Use case | What it looks like | Depends on |
|---|---|---|
| Intent-to-config drafting | Engineer describes the need in natural language; AI drafts the domain-model document and opens the staging PR — a second front door beside the wizard | Domain-model transform live (the committed format must be human-reviewable for approval to be meaningful) |
| Legacy migration PRs | AI converts wire-format files to domain-model format, one reviewable PR at a time (transform design, Phase 4) | Domain-model transform live |
| Self-maintaining documentation | On merge, AI proposes the matching runbook/guide update as a follow-up PR | Authoring conventions (§5) |
| Drift remediation proposals | Activation failure or reconciliation mismatch → AI drafts the fixing PR with evidence attached | Reconciliation facts (§3) |

### Tier 3 — AI watches and nudges (proactive)

| Use case | What it looks like |
|---|---|
| Team digests | Scheduled notification per team: coverage gaps, aging placeholders, noisy alerts, suggested next steps — through the Backstage Notifications channel already built |
| Score-driven guidance | The Observability Score loop — section 3, the centerpiece |

## 3. The Observability Score as a guidance loop

The score is the mechanism that turns passive inventory into active
guidance: it tells every team where they stand, and the narrative
layer tells them — in natural language — what to do about it, with a
link that starts the fix.

### The pipeline

```
Second brain          Facts                Checks / Score        Narrative (AI)         Delivery
─────────────         ─────                ──────────────        ──────────────         ────────
config repos,    ──►  "has processes  ──►  Tech Insights    ──►  what's missing,   ──►  entity page card
CMDB, catalog,        .json with           rules; per-entity     why it matters,        notifications digest
TechDocs, git         content?" etc.       scorecard             next step + link       chat assistant
                                           (deterministic)       (cites its facts)
```

The "next step + link" is the loop-closer: every recommendation links
to a **governed action** — the Raise-an-Alert wizard pre-filled for
that host, or a draft PR — never a direct write. *"Score 62: log
monitoring isn't configured for this host → Enable it here"* → wizard
→ PR → approval → activation → score updates. The score pulls users
into the same self-service pattern the Portal already runs on.

### Three kinds of drift the score measures

| Drift | Meaning | Measured from |
|---|---|---|
| Coverage drift | Asset exists but expected monitoring is absent or placeholder | CMDB vs config repos (today's empty `cdm.json` / `logmon.json` would be caught) |
| Reality drift | Git says X, the platform service says Y | Activation failures now; periodic read-back reconciliation later |
| Convention drift | Legacy wire format, missing `metadata` provenance, stale hand-authored catalog file | The config files themselves |

### Crawl / walk / run

1. **Crawl — no AI at all.** Tech Insights checks with *templated*
   guidance strings per failed check ("Log monitoring not configured
   — raise it here"). The entire loop — score, guidance, pre-filled
   wizard link, notification — ships deterministically. This proves
   the mechanism before any language model is involved.
2. **Walk — AI narrates.** Templates are replaced by contextual
   natural-language guidance; Tier 1 conversational Q&A arrives.
3. **Run — AI proposes.** Tier 2: remediation and drafting PRs,
   duplicate detection at request time.

## 4. Dependencies — what must be true first

| Dependency | Status | Owner |
|---|---|---|
| Domain-model transform (machine-readable, human-reviewable committed format) | Designed (`docs/architecture/domain-model-transform-design.md`), not built | octopod |
| Asset Catalog & Scoring workstream (CMDB → catalog entities → Tech Insights facts/checks) | Drafted spec exists in the wider program; explicitly out of octopod's current scope — **activating it is a program decision this direction now makes more urgent** | Program |
| AI bot credential design (scoped Bitbucket account: may create `staging/*`, may never push `main`; AI-authored commits attributable in the audit trail) | Not designed — needed before any Tier 2 use case | octopod + program |
| AI read surface over Bitbucket (index/API the AI tools query) | Not designed — needed for Tier 1 at scale | Program |
| Authoring conventions (§5) | Practiced informally, not written down | octopod |

## 5. Doc structure is architecture now

If Bitbucket is the second brain, the way documents are written stops
being a style preference and becomes the ingestion format for every
use case above. The conventions already in use in this repo — plain
language first, one concern per document, explicit status labels
(Decided / Proposed / Open), machine-parseable contract tables
(`docs/data/data-model.md`) — should be captured as a one-page
authoring convention so the second brain stays structured as more
authors (human and AI) contribute. Backlog item.

## 6. Read more

| Document | What it covers |
|---|---|
| `vision.md` | The executive framing: AI-DLC and the second brain |
| `docs/architecture/architecture.md` | The portal pattern all of this plugs into |
| `docs/architecture/domain-model-transform-design.md` | The keystone dependency for Tier 2 |
| `docs/data/data-model.md` | Example of a machine-parseable contract page |
