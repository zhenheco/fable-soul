"""Tests for sync_soul.py (zhenheco fork: marker-block injection).

Run from the skill root:
    python -m unittest scripts.test_sync_soul -v
or  python scripts/test_sync_soul.py
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync_soul


class SyncSoulTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self._orig_blocks = sync_soul.BLOCK_TARGETS
        self._orig_mirrors = sync_soul.SKILL_MIRRORS
        self._orig_hook = sync_soul.POST_SYNC_HOOK
        self._orig_agents = sync_soul.AGENTS_MD
        self._orig_link = sync_soul.CODEX_SKILL_LINK
        self.global_md = self.tmp / "CLAUDE-global.md"
        self.tail_md = self.tmp / "codex-tail.md"
        sync_soul.BLOCK_TARGETS = {
            self.global_md: sync_soul.render_soul_block,
            self.tail_md: sync_soul.render_codex_block,
        }
        sync_soul.SKILL_MIRRORS = []
        sync_soul.POST_SYNC_HOOK = None
        sync_soul.AGENTS_MD = None
        sync_soul.CODEX_SKILL_LINK = self.tmp / "codex-link" / "fable-soul"
        self._orig_argv = sys.argv
        sys.argv = ["sync_soul.py"]

    def tearDown(self) -> None:
        sync_soul.BLOCK_TARGETS = self._orig_blocks
        sync_soul.SKILL_MIRRORS = self._orig_mirrors
        sync_soul.POST_SYNC_HOOK = self._orig_hook
        sync_soul.AGENTS_MD = self._orig_agents
        sync_soul.CODEX_SKILL_LINK = self._orig_link
        sys.argv = self._orig_argv
        self._tmp.cleanup()

    def _seed(self, global_text: str = "# My global rules\n\nkeep me\n", tail_text: str = "") -> None:
        self.global_md.write_text(global_text, encoding="utf-8")
        self.tail_md.write_text(tail_text, encoding="utf-8")

    def test_soul_body_starts_at_marker(self) -> None:
        body = sync_soul.soul_body()
        self.assertTrue(body.startswith(sync_soul.BODY_MARKER))

    def test_compact_parity_with_canonical(self) -> None:
        self.assertEqual(sync_soul.parity_errors(), [])

    def test_injects_block_preserving_existing_content(self) -> None:
        self._seed()
        sync_soul.main()
        content = self.global_md.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("# My global rules"))
        self.assertIn("keep me", content)
        self.assertIn(sync_soul.BEGIN_MARK, content)
        self.assertIn(sync_soul.END_MARK, content)
        self.assertIn(sync_soul.BODY_MARKER, content)

    def test_replaces_stale_block_only(self) -> None:
        self._seed(
            "# My global rules\n\nkeep me\n\n"
            f"{sync_soul.BEGIN_MARK}\nstale soul\n{sync_soul.END_MARK}\n\ntrailing kept\n"
        )
        sync_soul.main()
        content = self.global_md.read_text(encoding="utf-8")
        self.assertNotIn("stale soul", content)
        self.assertIn("keep me", content)
        self.assertIn("trailing kept", content)
        self.assertIn(sync_soul.BODY_MARKER, content)
        self.assertEqual(content.count(sync_soul.BEGIN_MARK), 1)

    def test_missing_target_fails_loud(self) -> None:
        # codex-tail.md exists but CLAUDE-global.md does not -> wrong machine setup.
        self.tail_md.write_text("", encoding="utf-8")
        with self.assertRaises(SystemExit):
            sync_soul.main()

    def test_check_mode_reports_drift_without_writing(self) -> None:
        self._seed()
        sys.argv = ["sync_soul.py", "--check"]
        with self.assertRaises(SystemExit):
            sync_soul.main()
        # untouched: no block written in check mode
        self.assertNotIn(sync_soul.BEGIN_MARK, self.global_md.read_text(encoding="utf-8"))

    def test_idempotent_second_run(self) -> None:
        self._seed()
        sync_soul.main()
        first = self.global_md.read_text(encoding="utf-8")
        sync_soul.main()
        self.assertEqual(first, self.global_md.read_text(encoding="utf-8"))
        # and --check passes cleanly
        sys.argv = ["sync_soul.py", "--check"]
        sync_soul.main()  # should not raise

    def test_codex_tail_gets_directives(self) -> None:
        self._seed()
        sync_soul.main()
        tail = self.tail_md.read_text(encoding="utf-8")
        self.assertIn("Reasoning Directives", tail)
        self.assertIn(sync_soul.BEGIN_MARK, tail)

    def test_stale_agents_md_reported_in_check_mode(self) -> None:
        self._seed()
        sync_soul.main()  # blocks now current
        stale = self.tmp / "AGENTS.md"
        stale.write_text("# generated but missing soul blocks\n", encoding="utf-8")
        sync_soul.AGENTS_MD = stale
        sys.argv = ["sync_soul.py", "--check"]
        with self.assertRaises(SystemExit):
            sync_soul.main()

    def test_dangling_codex_link_relinked(self) -> None:
        self._seed()
        mirror = self.tmp / "vault-skill"
        sync_soul.SKILL_MIRRORS = [mirror]
        link = sync_soul.CODEX_SKILL_LINK
        link.parent.mkdir(parents=True)
        link.symlink_to(self.tmp / "gone")  # dangling
        sync_soul.main()
        self.assertTrue(link.is_symlink())
        self.assertEqual(link.resolve(), mirror.resolve())

    def test_real_dir_at_codex_link_fails_loud(self) -> None:
        self._seed()
        mirror = self.tmp / "vault-skill"
        sync_soul.SKILL_MIRRORS = [mirror]
        link = sync_soul.CODEX_SKILL_LINK
        link.mkdir(parents=True)  # old-layout full copy
        (link / "stale.md").write_text("old", encoding="utf-8")
        with self.assertRaises(SystemExit):
            sync_soul.main()
        self.assertTrue((link / "stale.md").exists())  # never deleted


if __name__ == "__main__":
    unittest.main()
