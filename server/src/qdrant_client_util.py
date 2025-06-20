from qdrant_client import QdrantClient
from qdrant_client.http import models
import uuid


def get_qdrant_client(collection_name, embedder):
    client = QdrantClient("localhost", port=6333)
    try:
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=embedder.dim, distance=models.Distance.COSINE
            ),
        )
    except Exception as e:
        print("Error al crear colección:", e)
    return client, embedder.dim


def index_chunks(client, collection, vectors, chunks, pdf_name):
    points = [
        models.PointStruct(
            id=str(uuid.uuid4()),  # Genera un ID único para cada chunk
            vector=vector,
            payload={"text": chunk, "pdf_name": pdf_name},
        )
        for chunk, vector in zip(chunks, vectors)
    ]
    client.upsert(collection_name=collection, points=points)


def search_chunks(client, collection, embedder, query, limit=3):
    query_vector = embedder.embed([query])[0]
    hits = client.search(
        collection_name=collection,
        query_vector=query_vector,
        limit=limit,
        with_payload=True,
    )
    results = []
    for hit in hits:
        results.append(
            {
                "text": hit.payload.get("text", ""),
                "pdf_name": hit.payload.get("pdf_name", ""),
                "score": hit.score,
            }
        )
    return results
