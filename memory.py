# memory.py
class RecursiveMemory:
    def __init__(self):
        self.history = []

    def store_state(self, state):
        self.history.append(state)

    def get_history(self):
        return self.history

    def latest(self):
        return self.history[-1] if self.history else None
