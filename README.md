# sca-tools-feed
A repository that aggregates release information from security and vulnerability-scanning tools, generates per-tool summary pages and comparison pages as HTML, and publishes them as feeds.

## Tool Category

This repository covers **SCA (Software Composition Analysis) tools** — also known as SBOM-based vulnerability management tools.

These tools scan the components that make up a system (OS packages, libraries, container images, etc.) to generate an SBOM (Software Bill of Materials), then match that SBOM against continuously updated CVE and other vulnerability databases to detect known vulnerabilities.

The following categories are **out of scope**:

- **SAST (Static Application Security Testing)**: Tools that detect vulnerabilities by analyzing source code patterns (e.g., SonarQube, Semgrep)
- **DAST (Dynamic Application Security Testing)**: Tools that detect vulnerabilities by sending requests to a running system (e.g., OWASP ZAP)
- **SBOM generation/management only**: Tools that do not perform CVE matching (e.g., microsoft/sbom-tool)

## Published Site

https://tmyymmt.github.io/sca-tools-feed/ is published as GitHub Pages. You can browse feed listings, per-tool summary pages, and the comparison page. All HTML pages support dark mode via `prefers-color-scheme`.

## How It Works

- Update feed files and render HTML pages (from Markdown sources) using one of the following methods:
  - Run daily via GitHub Actions
  - Create an Issue, have Copilot create a PR, complete review, and merge to main

## File Structure

### Spec Template
- GitHub Spec Kit style feature spec template: `.specify/templates/spec-template.md`

### Full Specification
- docs/fulls-specs/spec.md
- The full specification always reflects the latest spec
- Update the full specification when making functional changes

## Rules

- Create documentation in both Japanese and English
  - English: `*.md`, Japanese: `*_ja.md`

## License

MIT License
