from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments" / "padding_free_path_compatibility.py"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments import padding_free_path_compatibility as compatibility  # noqa: E402


class PaddingFreePathCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        completed = subprocess.run(
            [sys.executable, "-S", str(EXPERIMENT)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.results = json.loads(completed.stdout)
        cls.stderr = completed.stderr

    def test_all_frozen_cases_match_the_symbolic_fibers(self) -> None:
        self.assertEqual(self.results["case_count"], 16)
        self.assertEqual(len(self.results["cases"]), 16)
        self.assertEqual(
            self.results["compatibility_fibers"],
            {
                "00": ["00"],
                "01": ["00"],
                "10": ["00", "01"],
                "11": ["00", "01"],
            },
        )
        self.assertTrue(self.results["oracle_agreement"])
        self.assertEqual(self.stderr, "")

    def test_minimized_nonzero_witness_and_matched_control(self) -> None:
        witness = self.results["minimized_witness"]
        self.assertEqual(witness["raw_states"], ["000", "001"])
        self.assertEqual(witness["encoded_states"], [0, 4])
        self.assertEqual(witness["boundary"], "11")
        self.assertEqual(witness["traces"], ["010", "010"])
        self.assertTrue(witness["nonzero_bit_in_causal_cone"])

        control = self.results["matched_control"]
        self.assertEqual(control["boundary"], "00")
        self.assertEqual(control["traces"], ["000", "001"])
        self.assertTrue(control["classes_distinct"])
        self.assertNotEqual(*control["class_ids"])

    def test_scope_and_quantifiers_remain_bounded(self) -> None:
        self.assertEqual(self.results["classification"], "INCREMENTAL")
        self.assertEqual(self.results["definition"]["updates"], 2)
        self.assertEqual(self.results["definition"]["samples"], 3)
        self.assertEqual(
            self.results["definition"]["quantifier"],
            "exists X != Y and fixed b; for all t in {0,1,2}",
        )
        self.assertEqual(
            self.results["minimized_witness"]["minimal"],
            "relative to X=0^infinity and initial observed zero",
        )
        self.assertEqual(
            self.results["decision"],
            "BOUNDED_PADDING_FREE_COMPATIBILITY_COUNTEREXAMPLE",
        )
        self.assertIn("no coverage, recurrence, or aperiodicity claim", self.results["limitations"])

    def test_raw_state_disagreement_fails_closed(self) -> None:
        with patch.object(compatibility, "production_trace", return_value=(1, 1, 1)):
            with self.assertRaisesRegex(AssertionError, "raw-state/production mismatch"):
                compatibility.evaluate()


if __name__ == "__main__":
    unittest.main()
