from pymilvus import connections, FieldSchema, Collection, CollectionSchema, DataType
from config.config import MILVUS_HOST, MILVUS_PORT

import logging

logging.basicConfig(level=logging.INFO)


def connect_to_milvus(host="localhost", port="19530"):
    """
    Conectar a Milvus.
    :param host: Dirección de Milvus
    :param port: Puerto de Milvus
    :return: None
    """
    connections.connect(alias="default", host=host, port=port)
    print(f"Conectado a Milvus en {host}:{port}")


# def create_milvus_collection():
#     # Definir el esquema de la colección
#     fields = [
#         FieldSchema(name="pdf_id", dtype=DataType.INT64, is_primary=True, auto_id=True),
#         FieldSchema(name="pdf_text", dtype=DataType.STRING),
#         FieldSchema(
#             name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768
#         ),  # Dimensión del embedding
#     ]

#     schema = CollectionSchema(fields, description="Colección de PDFs")

#     # Crear la colección
#     collection = Collection(name="pdf_collection", schema=schema)
#     logging.info("Colección 'pdf_collection' creada o ya existe.")
#     return collection
