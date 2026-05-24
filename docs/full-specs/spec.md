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
| Yamory | SaaS (vulnerability management) | https://yamory.io/news | GitHub Actions + Playwright (headless Chromium) |
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

- Weekly execution via GitHub Actions (every Saturday at JST 07:00 / UTC Friday 22:00)
- Or: create an Issue → Copilot creates a PR → review → merge to main

### Publication Endpoint

- Published via GitHub Pages

---

## 3. Data Collection

### Collection Methods

| Target Type | Method |
|---|---|
| GitHub OSS (Trivy, etc.) | GitHub Actions + GitHub Releases API (structured data) |
| SaaS (FutureVuls) | GitHub Actions + HTML scraping |
| SaaS (Yamory) | GitHub Actions + Playwright (headless Chromium) |

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

### Published URL

https://tmyymmt.github.io/sca-tools-feed/

### Output File Structure (public/)

`public/` is not committed to the repository (gitignored). It is generated at runtime by GitHub Actions and deployed to GitHub Pages.

| Path | Content |
|---|---|
| `feeds/all.{rss,atom,json}` | Combined feed for all tools |
| `feeds/{tool_id}.{rss,atom,json}` | Per-tool feeds |
| `{tool_id}.html` / `{tool_id}_ja.html` | Per-tool summary pages (English/Japanese) |
| `comparison.html` / `comparison_ja.html` | All-tools comparison pages (Summary table + Detailed Comparison table) |
| `index.html` | Top page (feed list and links to comparison pages) |
| `.nojekyll` | Disables Jekyll processing on GitHub Pages |

HTML pages automatically apply dark mode by detecting browser/OS settings via the `prefers-color-scheme` media query.

The tool list in `index.html` uses the same sort order as the Summary table: summary feature checkmark count descending, then `centralized_management: true` first, then alphabetically by tool name. Rows in `comparison.html` are sorted independently per table: each table sorts by its own checkmark count descending, then by `centralized_management: true` first, then alphabetically.

### Per-Tool Page Structure

Each per-tool page (`{tool_id}.html` / `{tool_id}_ja.html`) contains:

- Tool overview (title, description, type, license, homepage link)
- Pricing display in the overview table: when `pricing_url` is set and `pricing` text contains `Paid` (case-insensitive), each `Paid` token is rendered as a link to `pricing_url` (e.g., `Free / [Paid](...)`)
- **Features table**: all 12 feature flags with ✅/❌ status:
  - Container Scanning, Language/Library Scanning, SBOM Generation, Policy Evaluation, IaC Scanning, Secret Detection, License Scanning, Build Tool Plugin, API Server, Agentless SSH Scanning, Dashboard, Centralized Management
- Feature reference link to official documentation (`features_url` in tools.yml, fallback to `homepage`)
- Release History (list of releases with version, date, and description)
- Source URL link below the Release History heading, pointing to the upstream release page

### Comparison Page Structure

The comparison pages (`comparison.html` / `comparison_ja.html`) contain two tables:

- **Summary table**: Tool name (with link to per-tool page and feature reference link), latest version, last updated, type, license, pricing, and basic feature flags (Container, Lang/Lib, SBOM, Policy). Pricing uses the same `pricing_url` + `Paid` token link rendering rule as per-tool pages.
- **Detailed Comparison table**: Tool name (with link to per-tool page and feature reference link), all feature flags plus a Unique Features column. Feature flags covered:
  - Container, Lang/Lib, SBOM, Policy, IaC, Secret Detection, License Scan, Build Plugin, API Server, SSH Agentless, Dashboard, Centralized Management

Each table uses its own sort order: checkmark count within that table's feature columns descending, then centralized_management true first, then alphabetical.

---

## 6. Non-Functional Requirements

See [spec-nonfunctional.md](spec-nonfunctional.md) for details.

- Prefer GitHub API over scraping; scraping is a last resort
- Tolerate partial failures; keep updating other tools' feeds on failure
- Use atomic writes to prevent publishing partially written files
