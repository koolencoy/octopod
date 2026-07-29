# Architecture diagrams

The `.svg` files here are what `architecture.md` displays — plain
images, so they render in any browser with no mermaid plugin or
JavaScript. The `.mmd` files are their editable mermaid sources.

**Never edit an `.svg` by hand.** Edit the `.mmd`, then regenerate:

```
npx -y @mermaid-js/mermaid-cli -i <name>.mmd -o <name>.svg -b white
```

(Requires Node.js. `-b white` gives the SVG a solid white background
so it stays readable in dark-themed viewers.)

Commit the `.mmd` and `.svg` together in the same change — a source
edit without its re-render leaves the document showing a stale
diagram.

| Diagram | Shown in |
|---|---|
| `portal-shape` | architecture.md §2.1 — portal + pluggable service slices |
| `request-loop` | architecture.md §2.2 — the six-step request loop |
| `request-sequence` | architecture.md §4 — request flow sequence |
| `branch-topology` | architecture.md §4.1 — staging branch git graph |
| `git-operations` | architecture.md §4.1 — every git op and API call in order |
