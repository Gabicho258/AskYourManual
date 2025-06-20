from sentence_transformers import SentenceTransformer

# Cargar el modelo de Hugging Face
model = SentenceTransformer("paraphrase-MiniLM-L6-v2")


def generate_embedding(text):
    """
    Genera un embedding para el texto proporcionado.
    :param text: Texto a convertir en embedding
    :return: Embedding del texto
    """
    return model.encode(text)
