# Savings baseline — measurement method

The Savings section of `overview.md` currently uses an illustrative
figure. This page is the method for replacing it with a measured one,
so the business case is reported as fact.

## 1. What to export

Pull every **alert/monitoring request handled manually** by the
platform team for the last 3–12 months. Sources, best first:

- **ITSM tickets** (HPSM / ServiceNow): filter on the platform team's
  assignment group and the request categories that map to monitoring
  setup (new alert, threshold change, onboarding, "is this
  monitored?"). Export: ticket ID, created date, resolved date.
- **Chat/call requests that never became tickets**: these are real
  demand too. If they can't be exported, count a sample week and
  extrapolate — note it as such.

One row per request into a CSV with this header (see
`tools/savings-baseline-template.csv`):

```
request_id,created_at,resolved_at,handling_minutes
```

`resolved_at` and `handling_minutes` are optional per row.
`handling_minutes` is hands-on engineer time, not elapsed time — if
unknown, leave blank and the calculator assumes a default you choose.

## 2. Run the calculator

```sh
python3 tools/compute_savings.py requests.csv --default-minutes 45
```

It prints requests/month, average handling minutes, engineer-hours
per month (and the FTE fraction), median requester wait, and a
paste-ready sentence for `overview.md`'s Savings section.

## 3. Honesty rules

- If handling minutes were assumed rather than measured, say so
  wherever the number is quoted (the calculator reports how many rows
  were assumed).
- Chat-sample extrapolations are estimates — label them.
- Report the measurement window alongside every figure.

## 4. Supporting anchor

The core-banking-payments alert inventory
(`ELK/alert-inventory-techdocs/alerts.csv`) lists **73 configured
alerts for that one domain** — each of which was once a manual
request. Useful as a stock ("how much manual work is already embedded
in the estate") alongside the flow (requests/month) measured above.
Confirm the inventory reflects production before quoting it.
