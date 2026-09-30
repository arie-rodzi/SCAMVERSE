import io
from docx import Document

def extract_text(file):
    if file is None:
        return ""
    name = file.name.lower()
    raw = file.read()
    if name.endswith('.docx'):
        doc = Document(io.BytesIO(raw))
        parts = [p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                parts.append(' | '.join(cell.text for cell in row.cells))
        return '\n'.join(parts)
    return raw.decode('utf-8', errors='ignore')
