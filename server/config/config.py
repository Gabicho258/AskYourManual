MILVUS_HOST = "localhost"
# MINIO_PORT = "9091"
MILVUS_PORT = "19530"

MINIO_ACCESS_KEY = "minioadmin"
# Credenciales predeterminadas, puedes cambiarlas si lo deseas
MINIO_SECRET_KEY = "minioadmin"


# Ruta a los archivos PDF
PDF_DIR = "./data/pdfs/"

# Parámetros para el modelo de embeddings
EMBEDDING_DIM = 384  # Dimensión del embedding
MODEL_NAME = "paraphrase-MiniLM-L6-v2"  # Nombre del modelo para obtener embeddings
