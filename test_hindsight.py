import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

API_KEY = os.getenv("HINDSIGHT_API_KEY")

if not API_KEY:
    raise ValueError("HINDSIGHT_API_KEY is missing from .env")

client = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=API_KEY
)

BANK_ID = "clientpulse-demo"

print("Creating ClientPulse memory bank...")

try:
    client.create_bank(
        bank_id=BANK_ID,
        name="ClientPulse"
    )
    print("✅ Memory bank ready!")
except Exception as e:
    print("ℹ️ Bank may already exist:", e)


print("\nStoring client interaction...")

client.retain(
    bank_id=BANK_ID,
    content="""
    Client: Acme Studios.

    During a client interaction, Acme said that they prefer
    minimal and clean website designs.

    Their approximate project budget is ₹50,000.

    They dislike excessive animations and prefer simple,
    professional presentations.
    """
)

print("✅ Client interaction stored in Hindsight!")


print("\nRecalling client memory...")

result = client.recall(
    bank_id=BANK_ID,
    query="What does Acme Studios prefer, dislike, and what is their budget?"
)

print("\n🧠 CLIENTPULSE MEMORY")
print("=" * 50)

for memory in result.results:
    print(f"- {memory.text}")

print("=" * 50)
print("\n🎉 Hindsight test completed!")