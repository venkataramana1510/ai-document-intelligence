
from dotenv import load_dotenv
import os
from google import genai

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")  

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=gemini_api_key)

def create_embedding(text: str):
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return response.embeddings[0].values



