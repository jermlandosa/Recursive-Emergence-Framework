# auto_truth_scan.py

from difflib import SequenceMatcher


def mirror_test(statement):
    reversed_statement = " ".join(statement.split()[::-1])
    return f"Original: {statement}\nReversed: {reversed_statement}\n⚠️ Manual evaluation required."


def inversion_test(statement):
    return f"What if the opposite were true?\n⚠️ Manually consider implications and contradictions."


def fractal_test(statement, micro_example, macro_example):
    return f"Micro Context: {micro_example}\nMacro Context: {macro_example}\n⚠️ Compare behavior at both scales."


def drift_test(statement):
    repeated = " ".join([statement] * 5)
    ratio = SequenceMatcher(None, statement, repeated).ratio()
    return f"Drift Ratio (repetition stability): {ratio:.2f} — ⚠️ Below 1.0 indicates potential entropy."


def anchor_echo_test(statement, symbols=[], actions=[], contradictions=[]):
    return (
        f"Symbols: {symbols}\n"
        f"Actions: {actions}\n"
        f"Contradictions: {contradictions}\n"
        "⚠️ Are they coherently aligned with the belief?"
    )


# Example runner
def run_truth_scan(
    statement, micro_example, macro_example, symbols, actions, contradictions
):
    print("🔍 Running Recursive Truth Scan")
    print("=" * 40)
    print("1. Mirror Test")
    print(mirror_test(statement))
    print("\n2. Inversion Test")
    print(inversion_test(statement))
    print("\n3. Fractal Test")
    print(fractal_test(statement, micro_example, macro_example))
    print("\n4. Drift Test")
    print(drift_test(statement))
    print("\n5. Anchor Echo Test")
    print(anchor_echo_test(statement, symbols, actions, contradictions))


# Example usage:
if __name__ == "__main__":
    statement = "People are only motivated by self-interest"
    micro_example = "Parent feeding their child"
    macro_example = "A nation designing its economic system"
    symbols = ["🌀", "Mirror", "Glyph"]
    actions = ["Acts of generosity", "Policy design"]
    contradictions = ["Altruism exists", "Collective sacrifice"]

    run_truth_scan(
        statement, micro_example, macro_example, symbols, actions, contradictions
    )
