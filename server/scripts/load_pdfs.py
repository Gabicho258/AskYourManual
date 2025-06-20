import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from milvus.milvus_client import connect_to_milvus
from milvus.insert import insert_pdfs_to_milvus
from pymilvus import Collection, CollectionSchema, FieldSchema, DataType
from config.config import MILVUS_HOST, MILVUS_PORT


def create_collection():
    # Definir el esquema de la colección
    fields = [
        FieldSchema(name="pdf_id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(
            name="pdf_text", dtype=DataType.VARCHAR, max_length=10000
        ),  # Cambiar a VARCHAR con longitud máxima
        FieldSchema(
            name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768
        ),  # Dimensión del embedding
    ]

    schema = CollectionSchema(fields, description="Colección de PDFs")

    # Crear la colección
    collection = Collection(name="pdf_collection", schema=schema)
    print("Colección 'pdf_collection' creada.")
    return collection


def load_pdfs():
    # Conectar a Milvus
    connect_to_milvus(MILVUS_HOST, MILVUS_PORT)

    # Verificar si la colección existe
    collection_name = "pdf_collection"
    collection = None
    try:
        collection = Collection(collection_name)
        print(f"La colección '{collection_name}' ya existe.")
    except:
        # Si la colección no existe, la creamos
        print(f"La colección '{collection_name}' no existe. Creando la colección...")
        collection = create_collection()

    # Insertar los PDFs en Milvus
    insert_pdfs_to_milvus(collection)


if __name__ == "__main__":
    load_pdfs()
