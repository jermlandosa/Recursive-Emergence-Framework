# sareth_test_mode.py

import os
import time
from sareth import main as sareth_main  # assumes sareth.py has a main() function
                                        # if not, let me know and I’ll restructure it

# Simulated user prompts for CI testing
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
        # You can hook this into your actual REPL logic
        os.environ["SIMULATED_INPUT"] = prompt
        try:
            sareth_main(prompt)  # call your actual logic per turn
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(0.5)  # Simulate delay
    print("\n✅ Test session complete.")

if __name__ == "__main__":
    simulate_user_session()
