# SCA Tools Feed
A repository that aggregates release information from security and vulnerability-scanning tools, generates per-tool summary pages and comparison pages as HTML, and publishes them as feeds.

Updated weekly via GitHub Actions. Subscribe to the generated feeds with any RSS reader.

🌐 **Live site**: https://tmyymmt.github.io/sca-tools-feed/

## Tool Category

This repository covers **SCA (Software Composition Analysis) tools** — also known as SBOM-based vulnerability management tools.

These tools scan the components that make up a system (OS packages, libraries, container images, etc.) to generate an SBOM (Software Bill of Materials), then match that SBOM against continuously updated CVE and other vulnerability databases to detect known vulnerabilities.

The following categories are **out of scope**:

- **SAST (Static Application Security Testing)**: Tools that detect vulnerabilities by analyzing source code patterns (e.g., SonarQube, Semgrep). See also: https://github.com/tmyymmt/sast-tools-feed/
- **DAST (Dynamic Application Security Testing)**: Tools that detect vulnerabilities by sending requests to a running system (e.g., OWASP ZAP). See also: https://github.com/tmyymmt/dast-tools-feed/
- **SBOM generation/management only**: Tools that do not perform CVE matching (e.g., microsoft/sbom-tool)

## How It Works

- Update feed files and render HTML pages (from Markdown sources) using one of the following methods:
  - Run weekly via GitHub Actions (every Friday at UTC 22:00)
  - Create an Issue, have Copilot create a PR, complete review, and merge to main

## Covered Tools

| Tool | Type | License |
|------|------|---------|
| [Trivy](https://trivy.dev) | OSS | Apache-2.0 |
| [Grype](https://github.com/anchore/grype) | OSS | Apache-2.0 |
| [Syft](https://github.com/anchore/syft) | OSS | Apache-2.0 |
| [OSV-Scanner](https://google.github.io/osv-scanner/) | OSS | Apache-2.0 |
| [Dependency-Check](https://jeremylong.github.io/DependencyCheck/) | OSS | Apache-2.0 |
| [Clair](https://github.com/quay/clair) | OSS | Apache-2.0 |
| [Vuls](https://vuls.io) | OSS | GPL-3.0 |
| [FutureVuls](https://vuls.biz) | Commercial | Proprietary |
| [Yamory](https://yamory.io) | Commercial | Proprietary |

## Feed URLs

### All Tools (Combined)

| Format | URL |
|--------|-----|
| RSS 2.0 | `https://tmyymmt.github.io/sca-tools-feed/feeds/all.rss` |
| Atom 1.0 | `https://tmyymmt.github.io/sca-tools-feed/feeds/all.atom` |
| JSON Feed 1.1 | `https://tmyymmt.github.io/sca-tools-feed/feeds/all.json` |

### Per-Tool Feeds

Replace `{tool_id}` with: `trivy`, `grype`, `syft`, `osv-scanner`, `dependency-check`, `clair`, `vuls`, `futurevuls`, `yamory`

| Format | URL |
|--------|-----|
| RSS 2.0 | `https://tmyymmt.github.io/sca-tools-feed/feeds/{tool_id}.rss` |
| Atom 1.0 | `https://tmyymmt.github.io/sca-tools-feed/feeds/{tool_id}.atom` |
| JSON Feed 1.1 | `https://tmyymmt.github.io/sca-tools-feed/feeds/{tool_id}.json` |

## Pages

- **Comparison**: [English](https://tmyymmt.github.io/sca-tools-feed/comparison.html) / [Japanese](https://tmyymmt.github.io/sca-tools-feed/comparison_ja.html)
- **Per-tool summaries**: `https://tmyymmt.github.io/sca-tools-feed/{tool_id}.html`

## Release Categories

Releases are categorized for easy filtering:

| Category | Description |
|----------|-------------|
| `feature` | Feature additions and changes |
| `bugfix` | Bug fixes |
| `security` | Security fixes and hotfixes |
| `pricing` | Pricing changes |
| `announcement` | Announcements, events, awards |
| `other` | Other |

## Repository Structure

```text
.
├── scripts/                # Python scripts
│   ├── main.py             # Entry point
│   ├── models.py           # Data models
│   ├── categorize.py       # Release categorization
│   ├── storage.py          # JSON storage
│   ├── feed_generator.py   # RSS/Atom/JSON Feed generation
│   ├── markdown_generator.py  # HTML page generation
│   └── collectors/         # Data collectors per source
│       ├── github.py       # GitHub Releases/API collector
│       ├── futurevuls.py   # FutureVuls collector
│       └── yamory.py       # Yamory collector
├── tools/
│   └── tools.yml           # Tool configuration
├── data/                   # Persisted release data (JSON)
├── public/                 # Generated output (gitignored, deployed to GitHub Pages)
├── tests/                  # Test suite
└── docs/                   # Specifications
    └── full-specs/         # Full specifications
        ├── spec.md         # Full specification (English)
        └── spec_ja.md      # Full specification (Japanese)
```

## Rules

- Create documentation in both Japanese and English
  - English: `*.md`, Japanese: `*_ja.md`
- Update the full specification when making functional changes
- AI-specific rules are defined in `.github/copilot-instructions.md`

## Setup

### Prerequisites

- Python 3.11 or higher

### Installation

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (for running tests only)
pip install -r requirements-dev.txt
```

## Local Execution

### Environment Variables

A `GITHUB_TOKEN` is required for the GitHub API.

```bash
export GITHUB_TOKEN=your_github_token
```

### Run

```bash
python -m scripts.main
```

This updates HTML files under `public/` and feed files under `public/feeds/`.

## GitHub Actions

### Automated (Weekly)

`.github/workflows/update-feeds.yml` runs automatically every Friday at UTC 22:00 (JST Saturday 07:00).

### Manual Trigger

Go to the **Actions** tab in the GitHub repository → **Update Feeds** → **Run workflow**.

### Required Configuration

- **Secrets**: `GITHUB_TOKEN` is provided automatically by GitHub Actions — no additional setup needed.
- **Permissions**: `contents: write` (for data commits) and `pages: write` (for GitHub Pages deployment) are preconfigured.
- **GitHub Pages**: In repository Settings → Pages, set Source to `GitHub Actions`.

## License

MIT License
