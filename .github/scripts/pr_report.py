#!/usr/bin/env python3
"""Build the pull-request comment body from a CI failure report artifact.

This script runs inside a *privileged* ``workflow_run`` context, which means it
holds a token that can write to the repository. Everything it reads originates
from a workflow that executed pull-request code, so all of it is treated as
untrusted text:

* report contents are only ever embedded inside a fenced code block, never
  interpreted, executed, or used to build a shell command;
* the fence is made longer than any backtick run in the content so the content
  cannot break out of the block;
* file names, the workflow name and the run URL are validated and sanitised
  before they are placed in Markdown, so a crafted name cannot inject a heading
  or an ``@mention``;
* the body is truncated well below GitHub's comment size limit;
* the comment marker is scoped per workflow, so two failing checks each own
  their own comment instead of overwriting one another.

Standard library only: no dependencies to install on the runner.
"""

from __future__ import annotations

import argparse
import io
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

# Hidden marker used to find and update our own comment instead of posting a
# new one on every failure.
#
# The marker is scoped per workflow. Both lint workflows can fail on the same
# commit, and with one shared marker the second report overwrites the first:
# the reader sees "Link Check failed" and never learns that markdownlint also
# failed. Scoping it means each workflow owns exactly one comment and can only
# ever update that one.
#
# The scope is a slug, never the raw workflow name. The name arrives in the
# event payload and a pull request can add a workflow whose name is arbitrary
# text, so the name is reduced to `[a-z0-9-]` with collapsed hyphen runs. That
# keeps the marker a single line, a syntactically valid HTML comment, and free
# of `--` in its body so it cannot be closed early.
MARKER_PREFIX = "<!-- rstg-ci-report"
MARKER_SUFFIX = "-->"

# Upper bound on the slug. Workflow names are short; this only bounds abuse.
MAX_SLUG = 40

# GitHub's hard limit is 65536 characters; stay comfortably below it.
MAX_BODY = 60000

# Never read more than this from a single report file.
MAX_FILE_BYTES = 400_000

# Caps that make a decompression bomb a non-event: entries are read one at a
# time into memory and nothing is ever written to disk.
MAX_ENTRIES = 20
MAX_TOTAL_BYTES = 1_000_000

# Conservative allow-list for anything that reaches Markdown outside a fence.
# `/` is included so artifact paths stay readable (`lychee/out.md`); on its own
# it cannot start a link, and the characters that could (`[`, `]`, `(`, `)`,
# backtick, `<`, `>`, `@`) are all excluded.
SAFE_LABEL = re.compile(r"^[A-Za-z0-9 ./_-]{1,60}$")
SAFE_URL = re.compile(r"^https://github\.com/[A-Za-z0-9_.\-/]+$")
SAFE_SHA = re.compile(r"^[0-9a-f]{7,40}$")


def sanitize_label(value: str, fallback: str = "CI") -> str:
    """Reduce an untrusted string to something safe to place in Markdown text.

    Anything outside ``[A-Za-z0-9 ._-]`` is dropped, so quotes, angle brackets,
    backticks and ``@`` cannot introduce formatting or mentions.
    """
    value = (value or "").strip()
    if SAFE_LABEL.match(value):
        return value
    cleaned = re.sub(r"[^A-Za-z0-9 ./_-]", "", value)[:60].strip()
    return cleaned or fallback


def marker_slug(workflow: str) -> str:
    """Reduce a workflow name to a stable ``[a-z0-9-]`` slug for the marker."""
    label = sanitize_label(workflow, fallback="CI")
    slug = re.sub(r"[^a-z0-9]+", "-", label.lower())
    slug = re.sub(r"-{2,}", "-", slug).strip("-")[:MAX_SLUG].strip("-")
    return slug or "ci"


def marker_for(workflow: str) -> str:
    """Return the per-workflow marker, e.g. ``<!-- rstg-ci-report:markdown-lint -->``.

    The workflow that searches for this comment compares it against the first
    line of a comment body, so the marker must stay byte-identical between the
    run that wrote the body and the run that looks it up. ``--marker-out``
    exists to guarantee exactly that.
    """
    return f"{MARKER_PREFIX}:{marker_slug(workflow)} {MARKER_SUFFIX}"


# Artifact member names are chosen by whoever produced the artifact, so they are
# never rendered. Only a known set is mapped to human labels; anything else gets
# a generic one. This also removes the last route by which a crafted name could
# become a live autolink (e.g. a member called `www.example.com/x`).
KNOWN_LABELS = {
    "markdownlint-report.txt": "markdownlint output",
    "out.md": "lychee link check",
}


def label_for_report(name: str) -> str:
    base = PurePosixPath((name or "").replace("\\", "/")).name
    return KNOWN_LABELS.get(base, "report")


def sanitize_url(value: str) -> str:
    """Return the URL only if it is a plain github.com URL, else an empty string."""
    value = (value or "").strip()
    return value if SAFE_URL.match(value) else ""


def sanitize_sha(value: str) -> str:
    """Return the commit SHA only if it looks like one, else an empty string."""
    value = (value or "").strip().lower()
    return value if SAFE_SHA.match(value) else ""


def fence_for(text: str) -> str:
    """Return a backtick fence strictly longer than any backtick run in ``text``.

    Without this, report content containing ``` could terminate the block early
    and let the remainder be rendered as live Markdown.
    """
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    return "`" * max(3, longest + 1)


def _decode(raw: bytes) -> str:
    return raw[:MAX_FILE_BYTES].decode("utf-8", "replace").strip()


def _read_zip(path: Path) -> list[tuple[str, str]]:
    """Read report entries straight out of the artifact archive.

    The archive is attacker-controlled, so it is never extracted to disk: every
    entry is read into memory with a per-entry and a total byte cap, and entry
    names are only ever used as display labels (they are sanitised later). A
    crafted name such as ``../../etc/passwd`` therefore has nowhere to escape to.
    """
    reports: list[tuple[str, str]] = []
    total = 0
    try:
        with zipfile.ZipFile(path) as archive:
            for info in sorted(archive.infolist(), key=lambda i: i.filename)[:MAX_ENTRIES]:
                if info.is_dir() or total >= MAX_TOTAL_BYTES:
                    continue
                try:
                    with archive.open(info) as handle:
                        raw = handle.read(MAX_FILE_BYTES)
                except (OSError, RuntimeError, zipfile.BadZipFile):
                    continue
                total += len(raw)
                text = _decode(raw)
                if text:
                    reports.append((info.filename, text))
    except (OSError, zipfile.BadZipFile):
        return []
    return reports


def read_reports(location: str) -> list[tuple[str, str]]:
    """Read reports from a directory, or from a .zip artifact, as text.

    Returns ``(display_name, text)`` pairs sorted by name so the output is
    deterministic. Unreadable or empty files are skipped rather than failing the
    job: a missing report should degrade the comment, not break it.
    """
    root = Path(location)
    if root.is_file() and zipfile.is_zipfile(root):
        return _read_zip(root)

    if not root.is_dir():
        return []

    # `actions/download-artifact` with `skip-decompress: true` leaves an archive
    # in the target directory. If one is present, read it and stop: falling
    # through would decode the archive itself as text and fill the comment with
    # binary noise.
    archives = sorted(p for p in root.glob("*.zip") if p.is_file())
    if archives:
        return _read_zip(archives[0])

    reports: list[tuple[str, str]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix == ".zip":
            continue
        try:
            with path.open("rb") as handle:
                raw = handle.read(MAX_FILE_BYTES)
        except OSError:
            continue
        text = _decode(raw)
        if text:
            reports.append((str(path.relative_to(root)), text))
    return reports


def build_body(
    workflow: str,
    run_url: str,
    sha: str,
    reports: list[tuple[str, str]],
    marker: str = "",
) -> str:
    """Assemble the full comment body.

    Truncation is applied to the report *text*, before it is fenced, so a cut can
    never remove a closing fence and leave the rest of the comment rendered as
    code. Each report is emitted as a complete, self-contained block.
    """
    label = sanitize_label(workflow)
    url = sanitize_url(run_url)
    short_sha = sanitize_sha(sha)[:7]
    marker = marker or marker_for(workflow)

    head: list[str] = [marker, "## CI failure report", ""]
    summary = f"**{label}** failed"
    if short_sha:
        summary += f" on `{short_sha}`"
    head.append(summary + ".")
    head.append("")
    if url:
        head.append(f"[Open the failing run]({url})")
        head.append("")

    footer = [
        "",
        "<sub>Posted automatically and updated in place on each failure. "
        "Not every failure produces a report artifact.</sub>",
    ]

    if not reports:
        head.append("_No report artifact was available for this run._")
        head.append("")
        head.append("See the run log for the failure details.")
    else:
        budget = MAX_BODY - len("\n".join(head)) - len("\n".join(footer)) - 200
        sections: list[str] = []
        remaining = budget
        for name, text in reports:
            label_line = f"**{label_for_report(name)}**"
            # label + blank line + both fences + blank line
            overhead = len(label_line) + 2 + 8 + 2
            allowance = remaining - overhead
            if allowance <= 40:
                sections.append("_… further reports omitted …_")
                break
            truncated = len(text) > allowance
            if truncated:
                text = text[:allowance].rstrip() + "\n… report truncated …"
            fence = fence_for(text)  # computed after truncation
            block = "\n".join([label_line, "", fence, text, fence, ""])
            sections.append(block)
            remaining -= len(block)
            if truncated:
                break
        head.append("\n".join(sections))

    body = "\n".join(head + footer).rstrip() + "\n"
    # Belt and braces: the contract with GitHub is a hard length limit.
    if len(body) > MAX_BODY:
        body = body[: MAX_BODY - 40].rstrip() + "\n\n… comment truncated …\n"
    return body


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports-dir", default="", help="Directory holding the artifact")
    parser.add_argument("--workflow", default="", help="Name of the workflow that failed")
    parser.add_argument("--run-url", default="", help="URL of the failing run")
    parser.add_argument("--sha", default="", help="Head commit SHA of the failing run")
    parser.add_argument("--out", required=True, help="Where to write the comment body")
    parser.add_argument(
        "--marker-out",
        default="",
        help="Optional path to write the marker the comment body starts with",
    )
    args = parser.parse_args(argv)

    reports = read_reports(args.reports_dir) if args.reports_dir else []
    marker = marker_for(args.workflow)
    body = build_body(args.workflow, args.run_url, args.sha, reports, marker=marker)

    Path(args.out).write_text(body, encoding="utf-8")
    if args.marker_out:
        # Written from the same computation that produced the body, so the step
        # that searches for the comment cannot drift from the step that built
        # it. Duplicating the slug rules in shell would be a second source of
        # truth, and a drift there silently disables in-place updates.
        Path(args.marker_out).write_text(marker, encoding="utf-8")
    print(
        f"wrote {len(body)} chars from {len(reports)} report file(s) to {args.out}"
        f" (marker: {marker})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
