import re


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def safe_chunk_text(text, max_length=4096, min_chunk=100):
    clean = text.replace("\n", " ").replace("\r", " ")
    chunks = []
    start = 0
    length = len(clean)
    while start < length:
        end = min(start + max_length, length)
        chunk = clean[start:end]
        if len(chunk) >= min_chunk:
            chunks.append(chunk)
        start += max_length
    return chunks
