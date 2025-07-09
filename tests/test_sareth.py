import os
import sys

# Ensure repository root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sareth


def test_exit():
    assert sareth.main("exit") == "exit"


def test_deep_prompt():
    prompt = "Explain recursive logic across time"
    expected = f"🪞 Reflecting on: '{prompt}'"
    assert sareth.main(prompt) == expected


def test_rejected_prompt():
    prompt = "maybe this will be rejected"
    assert sareth.main(prompt) == "⟁∅ Insight rejected"
