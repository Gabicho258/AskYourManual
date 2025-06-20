from src.pdf_reader import extract_text_from_pdf
from src.text_cleaner import clean_text, safe_chunk_text
from src.embedder import get_embedder
from src.qdrant_client_util import get_qdrant_client, index_chunks, search_chunks
import os
from tqdm import tqdm

PDF_DIR = "data/pdfs/"
COLLECTION = "pdf_chunks"


def main():
    # Carga PDFs
    pdfs = [
        os.path.join(PDF_DIR, f)
        for f in os.listdir(PDF_DIR)
        if f.lower().endswith(".pdf")
    ]
    print(f"Encontrados {len(pdfs)} PDFs.")

    # Inicializa embedder y Qdrant
    embedder = get_embedder()
    client, vector_dim = get_qdrant_client(COLLECTION, embedder)

    # Indexa cada PDF
    for pdf in tqdm(pdfs, desc="Indexando PDFs"):
        text = extract_text_from_pdf(pdf)
        clean = clean_text(text)
        chunks = safe_chunk_text(clean, max_length=4096)
        if not chunks:
            continue
        vectors = embedder.embed(chunks)
        index_chunks(
            client, COLLECTION, vectors, chunks, pdf_name=os.path.basename(pdf)
        )

    # Prueba de búsqueda
    print("\nEjemplo de búsqueda:")
    while True:
        query = input("Pregunta ('exit' para salir): ").strip()
        if query.lower() == "exit":
            break
        result = search_chunks(client, COLLECTION, embedder, query)
        for r in result:
            print(f"\nArchivo: {r['pdf_name']}\nTexto: {r['text']}\n---")


if __name__ == "__main__":
    main()
