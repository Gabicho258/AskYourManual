import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from milvus.search import search_in_milvus
from milvus.milvus_client import connect_to_milvus
from pymilvus import Collection
from config.config import MILVUS_HOST, MILVUS_PORT
from embeddings.vectorizer import generate_embedding


def search(query_text):
    # Conectar a Milvus
    connect_to_milvus(MILVUS_HOST, MILVUS_PORT)

    # Crear colección si no existe
    collection = Collection("pdf_collection")

    # Generar el embedding de la consulta
    query_embedding = generate_embedding(query_text)

    # Realizar la búsqueda
    results = search_in_milvus(collection, query_embedding)
    for result in results:
        print(result)


if __name__ == "__main__":
    query_text = input("Ingrese su consulta: ")
    search(query_text)
