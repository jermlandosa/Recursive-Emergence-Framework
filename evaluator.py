# evaluator.py
"""Evaluation utilities with optional NumPy fallback."""

try:
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover - fallback when numpy unavailable
    np = None

class Evaluator:
    def recurse(self, state, memory):
        """Evolve the given state (placeholder logic)."""
        return [x * 1.05 for x in state]

    def calculate_tension(self, state):
        """Return a normalized measure of variance in ``state``."""
        if not state:
            return 0

        if np is not None:
            return float(np.std(state) / (np.mean(state) + 1e-9))

        mean = sum(state) / len(state)
        variance = sum((x - mean) ** 2 for x in state) / len(state)
        std = variance ** 0.5
        return std / (mean + 1e-9)

    def has_converged(self, prev, curr, threshold: float = 0.001) -> bool:
        """Check whether ``prev`` and ``curr`` are within ``threshold`` distance."""
        if not prev or not curr:
            return False

        if np is not None:
            delta = float(np.linalg.norm(np.array(curr) - np.array(prev)))
        else:
            delta = sum((c - p) ** 2 for p, c in zip(prev, curr)) ** 0.5

        return delta < threshold
