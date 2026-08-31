from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments" / "trajectory_extension_consistency.py"
AUDIT = ROOT / "experiments" / "audit_trajectory_extension_consistency.py"
ARTIFACT = ROOT / "experiments" / "trajectory-extension-consistency.json"


class TrajectoryExtensionConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, str(EXPERIMENT)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_fixed_extension_gate_is_a_bounded_no_go(self) -> None:
        results = json.loads(ARTIFACT.read_text())
        self.assertEqual(results["definition"]["d"], 1)
        self.assertEqual(results["definition"]["k"], 1)
        self.assertEqual(
            results["definition"]["k_meaning"], "one fixed right-extension bit"
        )
        self.assertEqual(results["train_compatible_extensions"], [0])
        self.assertEqual(
            results["holdout_compatible_extensions"], {"0": True, "1": False}
        )
        self.assertEqual(results["information_bits"], 1.0)
        self.assertTrue(results["oracle_agreement"])
        self.assertTrue(results["separating_power"])
        self.assertEqual(results["decision"], "NO_GO_ZERO_PADDED_REFERENCE_ARTIFACT")

    def test_independent_audit_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(AUDIT)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("audit_ok", completed.stdout)
        self.assertEqual(completed.stderr, "")


if __name__ == "__main__":
    unittest.main()
