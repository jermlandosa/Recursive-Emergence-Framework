# recursor.py
from memory import RecursiveMemory
from evaluator import Evaluator
from logger import StateLogger

class Recursor:
    def __init__(self, max_depth=10, tension_threshold=0.7):
        self.memory = RecursiveMemory()
        self.evaluator = Evaluator()
        self.logger = StateLogger()
        self.max_depth = max_depth
        self.tension_threshold = tension_threshold

    def run(self, input_state):
        current_state = input_state
        for depth in range(self.max_depth):
            self.logger.log_state(depth, current_state)

            tension = self.evaluator.calculate_tension(current_state)
            if tension > self.tension_threshold:
                print(f"[HALT] Tension too high: {tension} at depth {depth}")
                break

            next_state = self.evaluator.recurse(current_state, self.memory)
            if self.evaluator.has_converged(current_state, next_state):
                print(f"[CONVERGENCE] Stable state at depth {depth}")
                break

            self.memory.store_state(current_state)
            current_state = next_state

        return current_state
