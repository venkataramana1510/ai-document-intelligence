

import os

from dotenv import load_dotenv
from google import genai

from rag.embedding_service import create_embedding
from rag.vector_store import  search_documents

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=gemini_api_key)


def answer_question(question: str,source_file: str | None = None):

    # 1. Convert the question into an embedding
    question_embedding = create_embedding(question)

    # 2. Search ChromaDB
    results = search_documents(question_embedding,
    top_k=3,
    source_file=source_file)

    # 3. Get retrieved documents
    documents = results["documents"][0]

    # 4. Get document IDs
    ids = results["ids"][0]

    # 5. Get similarity distances
    distances = results["distances"][0]

    metadatas = results["metadatas"][0]
    # 6. Combine documents into context
    context = "\n\n".join(documents)
    
   

    # 7. Ask Gemini using the retrieved context
    prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the information
provided in the context below.

If the answer cannot be found in the context, say:
"I don't have enough information in the provided documents."

Context:
{context}

Question:
{question}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    answer = response.text

    # 8. Create source information
    sources = [] 
    
    for i in range(len(documents)):
       metadata = metadatas[i] or {}

       sources.append({
            "id": ids[i],
            "distance": distances[i],
            "source_file": metadata.get("source_file"),
            "chunk_number": metadata.get("chunk_number"),
            "text": documents[i]
        })

    # 9. Return answer + sources
    return {
        "question": question,
        "answer": answer,
        "sources": sources,
       
    }
   