class Visualizer:
    """Simple visualization for recursion states using matplotlib."""
    def __init__(self, logger):
        self.logger = logger

    def plot_state_evolution(self):
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("[WARN] matplotlib not installed; skipping visualization")
            return

        if not getattr(self.logger, "logs", None):
            print("[WARN] No logs to visualize")
            return

        depths = [entry["depth"] for entry in self.logger.logs]
        states = [entry["state"] for entry in self.logger.logs]

        if not states:
            print("[WARN] No state data available")
            return

        # assume state is iterable with numeric values
        num_dims = len(states[0])
        for i in range(num_dims):
            plt.plot(depths, [s[i] for s in states], label=f"dim {i}")

        plt.xlabel("Depth")
        plt.ylabel("State Value")
        plt.title("State Evolution")
        plt.legend()
        plt.show()
