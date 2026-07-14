from pypdf import PdfReader

def extract_text(pdf_path: str):
    reader = PdfReader(pdf_path)

    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    return text
