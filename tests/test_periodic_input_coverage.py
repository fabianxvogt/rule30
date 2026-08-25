import json
import unittest
from contextlib import redirect_stdout
from io import StringIO

from experiments.periodic_input_coverage import (
    advance_period,
    analyze_macro_cycle,
    coverage_envelope,
    is_primitive_word,
    main,
    primitive_binary_words,
)
from experiments.rule30_successor import integer_successor, predictive_partition


class PeriodicInputCoverageTests(unittest.TestCase):
    def test_primitive_words_up_to_period_three(self):
        self.assertEqual(
            primitive_binary_words(3),
            (
                (0,),
                (1,),
                (0, 1),
                (1, 0),
                (0, 0, 1),
                (0, 1, 0),
                (0, 1, 1),
                (1, 0, 0),
                (1, 0, 1),
                (1, 1, 0),
            ),
        )
        self.assertTrue(is_primitive_word((0, 1, 0)))
        self.assertFalse(is_primitive_word((0, 1, 0, 1)))

    def test_advance_period_matches_individual_successors(self):
        expected = 0b001
        for boundary_bit in (1, 0, 1):
            expected = integer_successor(expected, boundary_bit, 3)
        self.assertEqual(
            advance_period(0b001, (1, 0, 1), 3),
            expected,
        )

    def test_fixed_zero_word_has_one_state_cycle(self):
        observation = analyze_macro_cycle(predictive_partition(3), (0,), 0)
        self.assertEqual(observation.macro_transient_steps, 0)
        self.assertEqual(observation.macro_cycle_steps, 1)
        self.assertEqual(observation.machine_period, 1)
        self.assertEqual(observation.cycle_states, (0,))
        self.assertEqual(observation.cycle_class_count, 1)
        self.assertEqual(observation.macro_cycle_class_count, 1)

    def test_precycle_count_uses_exact_input_phase(self):
        observation = analyze_macro_cycle(predictive_partition(2), (0, 1), 2)
        self.assertEqual(observation.macro_transient_steps, 1)
        self.assertEqual(observation.macro_cycle_steps, 2)
        self.assertEqual(observation.precycle_class_count, 1)
        self.assertEqual(observation.cycle_class_count, 2)

    def test_smallest_period_lift_counterexample(self):
        observation = analyze_macro_cycle(predictive_partition(1), (1,), 0)
        self.assertEqual(observation.machine_period, 2)
        self.assertEqual(observation.cycle_class_count, 2)
        self.assertEqual(observation.machine_cycle_classes, (0, 1))

    def test_envelope_is_bounded_and_reports_separate_cycle_coverage(self):
        observations = coverage_envelope(3, 2, initial_states=(0, 1))
        self.assertEqual(len(observations), 8)
        for observation in observations:
            self.assertEqual(
                observation.machine_period,
                observation.macro_cycle_steps * len(observation.boundary_word),
            )
            self.assertGreaterEqual(observation.cycle_class_count, 1)
            self.assertLessEqual(
                observation.cycle_class_count, observation.total_classes
            )

    def test_cli_emits_json_with_finite_bounds(self):
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(
                main(["--horizon", "2", "--max-period", "1"]),
                0,
            )
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["horizon"], 2)
        self.assertEqual(payload["max_period"], 1)
        self.assertEqual(payload["primitive_words"], 2)
        self.assertEqual(payload["initial_states"], 4)
        self.assertEqual(len(payload["observations"]), 8)


if __name__ == "__main__":
    unittest.main()
