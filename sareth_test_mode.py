# sareth_test_mode.py

import time
from sareth import main as sareth_main  # uses main(prompt) from sareth.py

test_prompts = [
    "What are you?",
    "Explain recursion.",
    "What's the REF?",
    "What happens if I say exit?",
    "exit"  # <- force stop at the end
]

def simulate_user_session():
    print("🧪 Starting REF test session (CI Mode)...\n")
    for prompt in test_prompts:
        print(f"You: {prompt}")
        try:
            sareth_main(prompt)
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(0.5)
    print("\n✅ Test session complete.")


def run_sareth_test() -> str:
    """Run the Sareth test session and capture the output as a string."""
    from io import StringIO
    import sys

    buffer = StringIO()
    original = sys.stdout
    sys.stdout = buffer
    try:
        simulate_user_session()
    finally:
        sys.stdout = original

    return buffer.getvalue()

if __name__ == "__main__":
    simulate_user_session()
