import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from .env")


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def interpret_query(user_query: str):

    prompt = f"""
You are an AI assistant for an e-commerce product search system.

Analyze the customer's search query:

"{user_query}"

Extract:

1. Product or category
2. Brand, if mentioned
3. Maximum budget, if mentioned
4. Desired attributes
5. Intended use
6. Other useful preferences

Return the result in a clear and concise format.

Do not invent products or information.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        print("Gemini API error:")
        print(e)

        return None