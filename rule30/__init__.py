"""Small repository-local facade for bounded Rule 30 transition checks.

The implementation remains in :mod:`experiments.rule30_successor` so the
existing experiment imports keep working.  These re-exports provide one
documented import path for the finite-width helpers without packaging the
larger experiment collection.
"""

from experiments.rule30_successor import (
    PredictivePartition,
    evolve_integer_state,
    integer_successor,
    predictive_partition,
    response_signature,
    response_trace,
)

__all__ = [
    "PredictivePartition",
    "evolve_integer_state",
    "integer_successor",
    "predictive_partition",
    "response_signature",
    "response_trace",
]
