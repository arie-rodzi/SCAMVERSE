import io
from docx import Document

def extract_text(file):
    if file is None:
        return ""
    name = file.name.lower()
    raw = file.read()
    if name.endswith('.docx'):
        doc = Document(io.BytesIO(raw))
        return '\n'.join(p.text for p in doc.paragraphs)
    return raw.decode('utf-8', errors='ignore')
