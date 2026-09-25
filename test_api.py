from dotenv import load_dotenv
import os
from anthropic import Anthropic

# Load the .env file so we can read the API key
load_dotenv()

# Get the key from .env
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("❌ No API key found. Check your .env file.")
else:
    print("✅ API key loaded successfully.")

    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=100,
        messages=[
            {"role": "user", "content": "Say hello in one short sentence, and confirm you're connected."}
        ]
    )

    print("\n🎉 Claude replied:")
    print(response.content[0].text)