# sareth_test_mode.py

import time
from sareth import main as sareth_main  # uses main(prompt) from sareth.py

test_prompts = [
    "What are you?",
    "Explain recursion.",
    "What's the REF?",
    "What happens if I say exit?",
    "exit"
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

if __name__ == "__main__":
    simulate_user_session()
