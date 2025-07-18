# logger.py
class StateLogger:
    def __init__(self):
        self.logs = []

    def log_state(self, depth, state):
        log_entry = {"depth": depth, "state": state}
        self.logs.append(log_entry)
        print(f"[DEPTH {depth}] State: {state}")
