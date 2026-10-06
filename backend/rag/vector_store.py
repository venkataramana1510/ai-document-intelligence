import os
from dotenv import load_dotenv
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if not QDRANT_URL:
    raise ValueError("QDRANT_URL not found in .env")

if not QDRANT_API_KEY:
    raise ValueError("QDRANT_API_KEY not found in .env")

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

COLLECTION_NAME = "company_policies"

# Gemini embedding-001 produces 3072-dimensional embeddings by default
VECTOR_SIZE = 3072

existing_collections = [
    collection.name
    for collection in client.get_collections().collections
]

if COLLECTION_NAME not in existing_collections:
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE
        )
    )
client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="source_file",
    field_schema="keyword"
)


def add_document(
    chunk_id: str,
    text: str,
    embedding: list[float],
    metadata: dict
):
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
               id=str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id)),
                vector=embedding,
                payload={
                    "text": text,
                    **metadata
                }
            )
        ]
    )


def search_documents(
    query_embedding: list[float],
    top_k: int = 3,
    source_file: str | None = None
):
    query_filter = None

    if source_file:
        query_filter = {
            "must": [
                {
                    "key": "source_file",
                    "match": {
                        "value": source_file
                    }
                }
            ]
        }

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        query_filter=query_filter,
        limit=top_k,
        with_payload=True
    )

    documents = []
    ids = []
    distances = []
    metadatas = []

    for result in results.points:
        ids.append(str(result.id))
        documents.append(result.payload.get("text", ""))
        metadatas.append({
            key: value
            for key, value in result.payload.items()
            if key != "text"
        })
        distances.append(result.score)

    return {
        "documents": [documents],
        "ids": [ids],
        "distances": [distances],
        "metadatas": [metadatas]
    }