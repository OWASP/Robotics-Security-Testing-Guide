#!/usr/bin/env python3
"""Tests for the PR failure-report builder.

Run with:  python3 -m unittest discover -s .github/scripts -v

The important cases are the adversarial ones: the report text comes from a
workflow that ran pull-request code, so it must never be able to escape its
code fence, inject a mention, or break out of the comment structure.
"""

from __future__ import annotations

import re
import tempfile
import zipfile
import unittest
from pathlib import Path

import pr_report as R


class FenceTests(unittest.TestCase):
    def test_plain_text_gets_three_backticks(self):
        self.assertEqual(R.fence_for("no backticks here"), "```")

    def test_fence_outgrows_longest_run(self):
        for run in (3, 4, 7):
            text = "x" + "`" * run + "y"
            self.assertEqual(R.fence_for(text), "`" * (run + 1))

    def test_fence_is_always_at_least_three(self):
        self.assertEqual(R.fence_for("`"), "```")


class InjectionTests(unittest.TestCase):
    """Content must stay literal inside the fence."""

    def test_content_cannot_close_the_fence(self):
        hostile = "```\n</details>\n@someone please review\n```"
        body = R.build_body("Link Check", "", "", [("out.md", hostile)])
        fence = R.fence_for(hostile)
        # The exact fenced block must be present and self-consistent.
        self.assertIn(f"{fence}\n{hostile}\n{fence}", body)
        # The fence we chose must be longer than anything inside the content.
        longest = max(len(r) for r in re.findall(r"`+", hostile))
        self.assertGreater(len(fence), longest)

    def test_html_and_mentions_stay_inside_the_fence(self):
        hostile = "@octocat <img src=x onerror=alert(1)>"
        body = R.build_body("Markdown Lint", "", "", [("r.txt", hostile)])
        # Everything after the opening fence line up to the closing fence is literal.
        opening = body.index(R.fence_for(hostile))
        closing = body.rindex(R.fence_for(hostile))
        self.assertLess(opening, body.index("@octocat"))
        self.assertGreater(closing, body.index("onerror"))

    def test_malicious_filename_cannot_inject_a_heading_or_mention(self):
        body = R.build_body("Link Check", "", "", [("@evil\n## Heading", "text")])
        self.assertNotIn("@evil", body)
        self.assertNotIn("## Heading", body)


class SanitizerTests(unittest.TestCase):
    def test_label_keeps_safe_names(self):
        self.assertEqual(R.sanitize_label("Markdown Lint"), "Markdown Lint")

    def test_label_strips_dangerous_characters(self):
        for hostile in ("@user", "<script>", "a`b", 'x"y', "line\nbreak"):
            cleaned = R.sanitize_label(hostile)
            self.assertNotIn("@", cleaned)
            self.assertNotIn("<", cleaned)
            self.assertNotIn("`", cleaned)
            self.assertNotIn('"', cleaned)
            self.assertNotIn("\n", cleaned)

    def test_label_keeps_path_separators_readable(self):
        self.assertEqual(R.sanitize_label("lychee/out.md"), "lychee/out.md")
        self.assertEqual(R.sanitize_label("a/b/c.txt"), "a/b/c.txt")

    def test_label_for_report_uses_known_names_only(self):
        self.assertEqual(R.label_for_report("markdownlint-report.txt"), "markdownlint output")
        self.assertEqual(R.label_for_report("out.md"), "lychee link check")
        self.assertEqual(R.label_for_report("nested/dir/out.md"), "lychee link check")

    def test_label_for_report_never_renders_an_attacker_chosen_name(self):
        # A member name that GFM would autolink must not reach the comment.
        for hostile in ("www.example.com/pwn", "../../etc/passwd", "@evil", "[x](y)"):
            self.assertEqual(R.label_for_report(hostile), "report", msg=hostile)

    def test_label_strips_link_and_bracket_characters(self):
        # Characters that could start a link or an image must not survive.
        for hostile in ("[click](javascript:alert(1))", "![x](y)", "<a href=x>"):
            cleaned = R.sanitize_label(hostile)
            for ch in "[]()<>":
                self.assertNotIn(ch, cleaned)

    def test_label_falls_back_when_everything_is_stripped(self):
        self.assertEqual(R.sanitize_label("!!!@@@###", fallback="CI"), "CI")
        self.assertEqual(R.sanitize_label("", fallback="CI"), "CI")

    def test_url_accepts_only_github_https(self):
        self.assertEqual(
            R.sanitize_url("https://github.com/OWASP/repo/actions/runs/1"),
            "https://github.com/OWASP/repo/actions/runs/1",
        )
        for bad in (
            "javascript:alert(1)",
            "http://github.com/x",
            "https://evil.example.com/x",
            "https://github.com/x y",
            "",
        ):
            self.assertEqual(R.sanitize_url(bad), "", msg=bad)

    def test_sha_accepts_only_hex(self):
        self.assertEqual(R.sanitize_sha("ABCDEF1234567"), "abcdef1234567")
        for bad in ("", "xyz", "abc", "a" * 41, "abcdefg"):
            self.assertEqual(R.sanitize_sha(bad), "", msg=bad)


class ReportReadingTests(unittest.TestCase):
    def test_missing_directory_yields_no_reports(self):
        self.assertEqual(R.read_reports("/nonexistent/path/for/tests"), [])

    def test_empty_directory_yields_no_reports(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(R.read_reports(d), [])

    def test_reads_nested_files_and_skips_empty_ones(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "lychee").mkdir()
            (root / "lychee" / "out.md").write_text("Errors: 2\n")
            (root / "empty.txt").write_text("   \n")
            reports = R.read_reports(d)
            self.assertEqual(len(reports), 1)
            self.assertEqual(reports[0][0], "lychee/out.md")
            self.assertIn("Errors: 2", reports[0][1])

    def test_binary_content_does_not_raise(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "blob.bin").write_bytes(bytes(range(256)))
            reports = R.read_reports(d)
            self.assertEqual(len(reports), 1)


class ZipTests(unittest.TestCase):
    """The artifact archive is attacker-controlled; reading it must be bounded."""

    def _zip(self, entries):
        path = Path(tempfile.mkdtemp()) / "ci-failure-report.zip"
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            for name, data in entries:
                z.writestr(name, data)
        return str(path)

    def test_reads_entries_from_archive(self):
        path = self._zip([("lychee/out.md", "Errors: 2\n"), ("lint.txt", "MD013\n")])
        reports = dict(R.read_reports(path))
        self.assertIn("lychee/out.md", reports)
        self.assertIn("Errors: 2", reports["lychee/out.md"])
        self.assertEqual(len(reports), 2)

    def test_traversal_entry_name_is_read_but_never_written(self):
        path = self._zip([("../../etc/passwd", "root:x:0:0")])
        reports = R.read_reports(path)
        self.assertEqual(len(reports), 1)
        # Nothing is extracted, so no file can appear outside the archive.
        self.assertFalse(Path("/etc/passwd.bak").exists())
        # The hostile name is not rendered at all.
        body = R.build_body("Link Check", "", "", reports)
        self.assertNotIn("..", body)
        self.assertNotIn("passwd", body)

    def test_single_huge_entry_is_capped(self):
        path = self._zip([("big.txt", "x" * (R.MAX_FILE_BYTES * 3))])
        reports = R.read_reports(path)
        self.assertEqual(len(reports), 1)
        self.assertLessEqual(len(reports[0][1]), R.MAX_FILE_BYTES)

    def test_many_entries_are_capped(self):
        path = self._zip([(f"f{i}.txt", "data") for i in range(R.MAX_ENTRIES * 3)])
        self.assertLessEqual(len(R.read_reports(path)), R.MAX_ENTRIES)

    def test_zip_bomb_total_is_bounded(self):
        # Many highly compressible entries: total read must stay bounded.
        path = self._zip([(f"b{i}.txt", "y" * R.MAX_FILE_BYTES) for i in range(R.MAX_ENTRIES)])
        reports = R.read_reports(path)
        total = sum(len(text) for _, text in reports)
        self.assertLessEqual(total, R.MAX_TOTAL_BYTES + R.MAX_FILE_BYTES)

    def test_archive_wins_over_stray_files_and_is_not_decoded_as_text(self):
        zpath = self._zip([("out.md", "boom")])
        d = Path(tempfile.mkdtemp())
        (d / "ci-failure-report.zip").write_bytes(Path(zpath).read_bytes())
        (d / "notes.txt").write_text("unrelated")
        reports = R.read_reports(str(d))
        self.assertEqual(len(reports), 1)
        self.assertIn("boom", reports[0][1])

    def test_corrupt_archive_yields_no_reports(self):
        path = Path(tempfile.mkdtemp()) / "broken.zip"
        path.write_bytes(b"PK\x03\x04 not really a zip")
        self.assertEqual(R.read_reports(str(path)), [])

    def test_directory_containing_only_an_archive_is_read_as_zip(self):
        zpath = self._zip([("out.md", "boom")])
        d = Path(tempfile.mkdtemp())
        (d / "ci-failure-report.zip").write_bytes(Path(zpath).read_bytes())
        self.assertEqual(len(R.read_reports(str(d))), 1)


class TruncationTests(unittest.TestCase):
    """Truncation must never leave a fence unterminated."""

    def _fences(self, body):
        return re.findall(r"^(`{3,})$", body, re.M)

    def test_long_report_keeps_fences_balanced(self):
        body = R.build_body("Link Check", "", "", [("out.md", "line\n" * 20000)])
        self.assertEqual(len(self._fences(body)) % 2, 0, "unbalanced fence")
        self.assertEqual(len(self._fences(body)), 2, "expected exactly one fenced block")

    def test_footer_survives_truncation_outside_the_fence(self):
        body = R.build_body("Link Check", "", "", [("out.md", "line\n" * 20000)])
        self.assertIn("Posted automatically", body)
        # the footer must come after the closing fence
        last_fence = max(m.start() for m in re.finditer(r"^`{3,}$", body, re.M))
        self.assertGreater(body.index("Posted automatically"), last_fence)

    def test_many_reports_stay_within_limit_and_balanced(self):
        reports = [(f"out{i}.md", "x" * 20000) for i in range(10)]
        body = R.build_body("Link Check", "", "", reports)
        self.assertLessEqual(len(body), R.MAX_BODY)
        self.assertEqual(len(self._fences(body)) % 2, 0)

    def test_no_report_case_is_unchanged(self):
        body = R.build_body("Link Check", "", "", [])
        self.assertIn("No report artifact", body)
        self.assertEqual(self._fences(body), [])


class MarkerTests(unittest.TestCase):
    """The marker is scoped per workflow so two failures cannot collide."""

    def test_marker_names_the_workflow(self):
        self.assertEqual(
            R.marker_for("Markdown Lint"), "<!-- rstg-ci-report:markdown-lint -->"
        )
        self.assertEqual(R.marker_for("Link Check"), "<!-- rstg-ci-report:link-check -->")

    def test_two_workflows_get_different_markers(self):
        # This is the whole point: the second report must not overwrite the first.
        self.assertNotEqual(R.marker_for("Markdown Lint"), R.marker_for("Link Check"))

    def test_body_starts_with_its_own_scoped_marker(self):
        for name in ("Markdown Lint", "Link Check"):
            body = R.build_body(name, "", "", [])
            self.assertEqual(body.split("\n")[0], R.marker_for(name))

    def test_explicit_marker_overrides_the_derived_one(self):
        body = R.build_body("Link Check", "", "", [], marker="<!-- custom -->")
        self.assertEqual(body.split("\n")[0], "<!-- custom -->")

    def test_hostile_workflow_name_cannot_forge_a_second_marker(self):
        """A pull request can add a workflow with any name it likes.

        The slug must stay a single-line, valid HTML comment built only from
        ``[a-z0-9-]``: anything else would let the name close the comment early
        or imitate another workflow's marker.
        """
        for hostile in (
            "Markdown Lint -->\n<!-- rstg-ci-report:link-check",
            "@evil",
            "<script>",
            "a`b",
            "x--y",
            "",
            "   ",
            "Ünïcödé",
        ):
            marker = R.marker_for(hostile)
            self.assertNotIn("\n", marker)
            self.assertRegex(
                marker, r"^<!-- rstg-ci-report:[a-z0-9]+(-[a-z0-9]+)* -->$", msg=hostile
            )

    def test_empty_or_unsafe_name_falls_back_to_ci(self):
        self.assertEqual(R.marker_for(""), "<!-- rstg-ci-report:ci -->")
        self.assertEqual(R.marker_for("!!!"), "<!-- rstg-ci-report:ci -->")

    def test_slug_is_bounded(self):
        self.assertLessEqual(len(R.marker_slug("x" * 500)), R.MAX_SLUG)

    def test_marker_out_is_identical_to_the_body_first_line(self):
        """--marker-out is what the workflow greps for, so it must not drift."""
        with tempfile.TemporaryDirectory() as d:
            body_path = Path(d) / "comment.md"
            marker_path = Path(d) / "marker.txt"
            R.main(
                [
                    "--workflow",
                    "Link Check",
                    "--out",
                    str(body_path),
                    "--marker-out",
                    str(marker_path),
                ]
            )
            marker = marker_path.read_text(encoding="utf-8")
            self.assertEqual(marker, R.marker_for("Link Check"))
            self.assertEqual(
                body_path.read_text(encoding="utf-8").split("\n")[0], marker
            )

    def test_marker_out_is_optional(self):
        with tempfile.TemporaryDirectory() as d:
            body_path = Path(d) / "comment.md"
            self.assertEqual(R.main(["--workflow", "Link Check", "--out", str(body_path)]), 0)
            self.assertTrue(body_path.is_file())


class BodyTests(unittest.TestCase):
    def test_marker_is_present_so_the_comment_can_be_updated(self):
        body = R.build_body("Link Check", "", "", [])
        self.assertTrue(body.startswith(R.MARKER_PREFIX))

    def test_no_reports_says_so_instead_of_failing(self):
        body = R.build_body("Link Check", "", "", [])
        self.assertIn("No report artifact", body)

    def test_includes_run_url_and_short_sha(self):
        body = R.build_body(
            "Link Check",
            "https://github.com/o/r/actions/runs/9",
            "abcdef1234567890",
            [("out.md", "boom")],
        )
        self.assertIn("https://github.com/o/r/actions/runs/9", body)
        self.assertIn("`abcdef1`", body)

    def test_long_report_is_truncated_under_the_limit(self):
        huge = "x" * (R.MAX_BODY * 2)
        body = R.build_body("Link Check", "", "", [("big.txt", huge)])
        self.assertLessEqual(len(body), R.MAX_BODY)
        self.assertIn("truncated", body)

    def test_multiple_reports_are_all_included(self):
        body = R.build_body("Link Check", "", "", [("a.txt", "alpha"), ("b.txt", "beta")])
        self.assertIn("alpha", body)
        self.assertIn("beta", body)


if __name__ == "__main__":
    unittest.main()
