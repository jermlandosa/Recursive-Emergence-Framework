# engine_runner.py
"""Thin wrapper for running the REF engine from the command line."""

from ref_engine import run_recursive_engine


def main(depth: int = 10, threshold: float = 0.7):
    """Execute the recursive engine and print results."""
    state, glyph, reason = run_recursive_engine(depth=depth, threshold=threshold)
    print(f"Final State: {state}")
    print(f"Last Glyph: {glyph}")
    print(f"Halt Reason: {reason}")


if __name__ == "__main__":  # pragma: no cover - CLI convenience
    main()
