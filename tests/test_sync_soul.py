from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_TEST = ROOT / "scripts" / "test_sync_soul.py"

sys.path.insert(0, str(SCRIPT_TEST.parent))
spec = importlib.util.spec_from_file_location("fable_soul_script_test_sync_soul", SCRIPT_TEST)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load {SCRIPT_TEST}")

module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

SyncSoulTests = module.SyncSoulTests
