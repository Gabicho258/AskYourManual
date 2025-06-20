from pypdf import PdfReader


def extract_text_from_pdf(pdf_path):
    # Primero prueba con pypdf
    try:
        from pypdf import PdfReader

        reader = PdfReader(pdf_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        # Si falla, intenta con pdfplumber
        try:
            import pdfplumber

            with pdfplumber.open(pdf_path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception:
            # Si falla, intenta con fitz (PyMuPDF)
            try:
                import fitz

                doc = fitz.open(pdf_path)
                return "\n".join(page.get_text() for page in doc)
            except Exception as e:
                print(f"[ERROR] No se pudo extraer texto de {pdf_path}: {e}")
                return ""
