import numpy as np
import os
from pymilvus import Collection
from embeddings.extractor import extract_text_from_pdf
from embeddings.vectorizer import generate_embedding
from config.config import PDF_DIR


def insert_pdfs_to_milvus(collection: Collection):
    """
    Inserta los PDFs y sus embeddings en Milvus.
    :param collection: Colección de Milvus
    :return: None
    """
    pdf_files = [f for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]
    texts = []
    embeddings = []

    for pdf_file in pdf_files:
        pdf_path = os.path.join(PDF_DIR, pdf_file)
        text = extract_text_from_pdf(pdf_path)
        embedding = generate_embedding(text)  # Generar embedding del texto
        texts.append(text)
        embeddings.append(embedding)

    embeddings = np.array(
        embeddings
    ).tolist()  # Convertir los embeddings a formato adecuado
    collection.insert([texts, embeddings])
    print(f"{len(pdf_files)} PDFs insertados en Milvus.")
