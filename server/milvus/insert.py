import numpy as np
import os
from pymilvus import Collection
from embeddings.extractor import extract_text_from_pdf
from embeddings.vectorizer import generate_embedding
from config.config import PDF_DIR

MAX_TEXT_LENGTH = 5000  # Longitud máxima permitida para el campo `pdf_text`


def split_text(text: str, max_length: int = MAX_TEXT_LENGTH):
    """Función para dividir un texto en fragmentos más pequeños si supera el tamaño máximo"""
    return [text[i : i + max_length] for i in range(0, len(text), max_length)]


def insert_pdfs_to_milvus(collection: Collection):
    """
    Inserta los PDFs y sus embeddings en Milvus, asegurándose de que los textos no excedan los 10,000 caracteres.
    :param collection: Colección de Milvus
    :return: None
    """
    pdf_files = [f for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]
    texts = []
    embeddings = []

    for pdf_file in pdf_files:
        pdf_path = os.path.join(PDF_DIR, pdf_file)
        text = extract_text_from_pdf(pdf_path)  # Extraer texto del PDF

        # Dividir el texto en fragmentos más pequeños si es necesario
        text_fragments = split_text(text)
        for fragment in text_fragments:
            if len(fragment) <= MAX_TEXT_LENGTH:
                embedding = generate_embedding(
                    fragment
                )  # Generar embedding para cada fragmento de texto
                texts.append(fragment)
                embeddings.append(embedding)
            else:
                print(
                    f"Warning: El texto de {pdf_file} supera el límite de tamaño y no fue insertado."
                )

    embeddings = np.array(
        embeddings
    ).tolist()  # Convertir los embeddings a formato adecuado

    # Insertar los datos en la colección
    collection.insert([texts, embeddings])
    print(
        f"{len(pdf_files)} PDFs insertados en Milvus. Total de fragmentos insertados: {len(texts)}."
    )
