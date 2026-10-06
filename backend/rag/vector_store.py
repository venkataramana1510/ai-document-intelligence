import chromadb

client = chromadb.PersistentClient(path="rag/chromadb")


collection = client.get_or_create_collection(
    name="company_policies"
)


def add_document(chunk_id:str,text:str,embedding:list[float],metadata:dict):
    collection.upsert(
        ids =[chunk_id],
        documents = [text],
        embeddings =[embedding],
        metadatas=[metadata]
    )
def search_documents(
    query_embedding: list[float],
    top_k: int = 3,
    source_file: str | None = None
):

    query_args = {
        "query_embeddings": [query_embedding],
        "n_results": top_k
    }

    if source_file:
        query_args["where"] = {
            "source_file": source_file
        }

    results = collection.query(**query_args)

    return results


