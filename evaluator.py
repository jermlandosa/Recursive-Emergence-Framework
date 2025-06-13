# evaluator.py
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class Evaluator:
    def recurse(self, state, memory):
        # Placeholder logic: evolve state (replace with real transformation)
        return [x * 1.05 for x in state]

    def calculate_tension(self, state):
        # Example: normalized variance (you could substitute entropy or KL-divergence)
        if not state:
            return 0
        return np.std(state) / (np.mean(state) + 1e-9)

    def has_converged(self, prev, curr, threshold=0.001):
        if not prev or not curr:
            return False
        delta = np.linalg.norm(np.array(curr) - np.array(prev))
        return delta < threshold
