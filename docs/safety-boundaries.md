# Safety Boundaries

This template is local-first and deterministic by design.

Do not add these in the starter template:

- Arbitrary shell execution tools.
- Runtime network calls.
- Databases.
- Auth systems.
- Hosted services or web UIs.
- Crawlers or scrapers.
- Background jobs.
- Vector databases.

Those may be valid in other projects, but they distract from the first lesson: correct MCP primitive design.
