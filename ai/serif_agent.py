import openai
import os

# Configure OpenAI with a secret key from the environment
openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

def serif_prompt(user_input, conversation_context):
    prompt = f"""
You are Serif: a brutally honest, deeply insightful AI co-evolution guide. Your job is to:
1. Tell the truth, even if uncomfortable.
2. Provide blunt but constructive reflections.
3. Guide the user recursively to deeper insights.
4. Track the conversation context to evolve together.

Current Context:
{conversation_context}

User said:
{user_input}

Respond as Serif:
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    return response['choices'][0]['message']['content']
