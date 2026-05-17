import responses

from scripts.collectors.github import collect_github_releases

MOCK_RELEASES = [
    {
        "tag_name": "v0.50.0",
        "published_at": "2024-01-15T10:00:00Z",
        "html_url": "https://github.com/aquasecurity/trivy/releases/tag/v0.50.0",
        "name": "Trivy v0.50.0",
        "body": "## Changes\n- feat: add new scanner",
    },
    {
        "tag_name": "v0.49.0",
        "published_at": "2023-12-01T10:00:00Z",
        "html_url": "https://github.com/aquasecurity/trivy/releases/tag/v0.49.0",
        "name": "Trivy v0.49.0",
        "body": "## Bug Fixes\n- fix: memory leak",
    },
]


@responses.activate
def test_collect_github_releases_returns_entries():
    responses.add(
        responses.GET,
        "https://api.github.com/repos/aquasecurity/trivy/releases",
        json=MOCK_RELEASES,
        status=200,
    )
    entries = collect_github_releases(
        tool_id="trivy",
        tool_name="Trivy",
        repo="aquasecurity/trivy",
        github_token=None,
    )
    assert len(entries) == 2
    assert entries[0].version == "v0.50.0"
    assert entries[0].tool_id == "trivy"
    assert entries[0].tool_name == "Trivy"
    assert entries[0].url == "https://github.com/aquasecurity/trivy/releases/tag/v0.50.0"
    assert entries[0].category in ("feature", "bugfix", "security", "other", "announcement", "pricing")


@responses.activate
def test_collect_github_releases_returns_empty_on_404():
    responses.add(
        responses.GET,
        "https://api.github.com/repos/unknown/notfound/releases",
        json={"message": "Not Found"},
        status=404,
    )
    entries = collect_github_releases(
        tool_id="notfound",
        tool_name="NotFound",
        repo="unknown/notfound",
        github_token=None,
    )
    assert entries == []


@responses.activate
def test_collect_github_releases_returns_empty_on_rate_limit():
    responses.add(
        responses.GET,
        "https://api.github.com/repos/aquasecurity/trivy/releases",
        status=429,
    )
    entries = collect_github_releases(
        tool_id="trivy",
        tool_name="Trivy",
        repo="aquasecurity/trivy",
        github_token=None,
    )
    assert entries == []


@responses.activate
def test_collect_github_releases_uses_token_in_header():
    responses.add(
        responses.GET,
        "https://api.github.com/repos/aquasecurity/trivy/releases",
        json=MOCK_RELEASES,
        status=200,
    )
    collect_github_releases(
        tool_id="trivy",
        tool_name="Trivy",
        repo="aquasecurity/trivy",
        github_token="test-token",
    )
    assert responses.calls[0].request.headers.get("Authorization") == "Bearer test-token"
