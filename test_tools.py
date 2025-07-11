def run_sareth_test():
    state = [0.5, 1.5, 2.5]
    print("[SARETH] Testing state:", state)
    glyph = hash(str(state)) % (10**8)
    return f"Glyph ID: {glyph}"

