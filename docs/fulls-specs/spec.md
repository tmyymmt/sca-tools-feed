# Full Specification

This directory contains the full specification of this project.

## Writing Guidelines

- The specification should be navigable starting from this file
- Manage specifications hierarchically to prevent individual files from becoming too large and hard to read
- When there is a large amount of specification content, start with a high-level, concise description and create child files for the details
- When creating child files
  - Include links to prerequisite information files

---

## 1. Target Tools

### In Scope

| Tool | Type | Source | Collection Method |
|---|---|---|---|
| FutureVuls | SaaS (vulnerability management) | https://help.vuls.biz/releasenotes/ | GitHub Actions + Copilot web search or HTML scraping |
| Vuls (OSS) | OSS | https://github.com/future-architect/vuls | GitHub Releases API |
| Yamory | SaaS (vulnerability management) | https://yamory.io/news | GitHub Actions + Copilot web search or HTML scraping |
| Trivy | OSS | https://github.com/aquasecurity/trivy | GitHub Releases API + CHANGELOG.md |
| Grype | OSS | https://github.com/anchore/grype | GitHub Releases API |
| Syft | OSS | https://github.com/anchore/syft | GitHub Releases API |
| OSV-Scanner | OSS | https://github.com/google/osv-scanner | GitHub Releases API |
| Dependency-Check | OSS | https://github.com/jeremylong/DependencyCheck | GitHub Releases API |
| Clair | OSS | https://github.com/quay/clair | GitHub Releases API |

### Out of Scope (reference only)

Tools that only generate or manage SBOMs are out of scope. They are listed here as references only.

- [microsoft/sbom-tool](https://github.com/microsoft/sbom-tool)

---

## 2. Feed Specification

### Formats

All three formats are supported:

- RSS 2.0
- Atom 1.0
- JSON Feed 1.1

### Feed Fields

- Version (tag name)
- Date/time (published date)
- URL (link to release page)
- Summary (title and overview)
- Change details (CHANGELOG / release notes body)
- Release type category (see below)

### Release Type Categories

Feeds are categorized by release type, also used for filtering:

- `feature`: Feature additions and changes (highest priority)
- `pricing`: Pricing changes
- `security`: Security fixes and hotfixes
- `bugfix`: Bug fixes
- `announcement`: Announcements, conference appearances, awards, etc. (for SaaS tools like Yamory)
- `other`: Other

### Update Frequency

- Daily execution via GitHub Actions
- Or: create an Issue → Copilot creates a PR → review → merge to main

### Publication Endpoint

- Published via GitHub Pages

---

## 3. Data Collection

### Collection Methods

| Target Type | Method |
|---|---|
| GitHub OSS (Trivy, etc.) | GitHub Actions + GitHub Releases API (structured data) |
| SaaS (FutureVuls, Yamory) | GitHub Actions + Copilot web search or HTML scraping |

### GitHub Releases API

- Endpoint: `https://api.github.com/repos/{owner}/{repo}/releases`
- Available fields: `tag_name` (version), `published_at` (date), `body` (CHANGELOG), `html_url`
- Rate limits: 60 req/hour unauthenticated, 5000 req/hour with token
- **Prefer API over scraping** (scraping breaks when HTML structure changes)

### Execution Model

- Polling (daily scheduled execution) is the primary model
- Event-driven (GitHub webhooks, etc.) is not adopted as target SaaS services do not support it

---

## 4. Data Storage

- Collected data is stored as files within the repository (JSON intermediate format)
- All sources are normalized to a unified JSON intermediate format, from which RSS/Atom/JSON Feed files are generated
  - Minimizes impact when upstream sources change
- History is retained permanently and accumulates indefinitely (never deleted)
- Target tools are managed in a configuration file (YAML, etc.) so new tools can be added without code changes

---

## 5. Publication and Distribution

- Target users: general public
- Subscription methods: RSS readers, or direct access to repository files
- Filtering: available by release type category

---

## 6. Non-Functional Requirements

### Reducing Maintenance Burden

- Prefer GitHub API over scraping
- OSS tools on GitHub can be added with low cost; add SaaS tools that require scraping with caution
- Unify internal data format as JSON to limit the impact of upstream changes
- Manage tool list in a configuration file (YAML, etc.) so new tools can be added without code changes
- When scraped HTML changes unexpectedly, emit a warning but do not break the feed

### Behavior on Failure

| Scenario | Behavior |
|---|---|
| Partial failure | If one tool's collection fails, still update feeds for other tools |
| Atomic writes | Write to a temp file then rename; never publish a partially written file |
| Rate limiting | On GitHub API 429, skip that run and retry on the next scheduled execution |
| 404 / page gone | Log the error and preserve existing data as-is |
| GitHub Actions alerts | Auto-create an Issue after N consecutive failures |
| Feed validation | Validate generated RSS/Atom/JSON Feed by parsing and schema-checking before publishing |
| Rollback | Data is stored in Git, so broken state can be reverted with `git revert` |

### License

MIT License

