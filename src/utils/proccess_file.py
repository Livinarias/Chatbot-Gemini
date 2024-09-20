"""This file organice and send tada to RAG"""
import fitz  # PyMuPDF
from src.constants.constants import titles

def extract_text_spans(page):
    """Extract spans on this page."""
    blocks = page.get_text("dict")["blocks"]
    spans = []
    for block in blocks:
        if "lines" in block:
            for line in block["lines"]:
                spans.extend(line["spans"])
    return spans


def is_bold(span):
    """determinate if fragment is bold."""
    return "bold" in span["font"].lower()


def process_spans(spans):
    """proccess spam and organice by titles bold."""
    sections = {}
    current_title = None

    for span in spans:
        text = span["text"].strip()

        if not text:
            continue  # Omitir spans vacíos

        if is_bold(span):
            # Si es negrita, lo consideramos como un título
            current_title = text
            # Inicializar una lista para este título
            sections[current_title] = []
        elif current_title:
            # Si no es negrita, agregar el texto a la sección del título actual
            sections[current_title].append(text)

    # Eliminar títulos sin contenido
    sections = {title: content for title,
                content in sections.items() if content}
    return sections


def segment_text_by_bold_titles(path):
    """Organice text by bold."""
    doc = fitz.open(path)
    all_sections = {}

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        spans = extract_text_spans(page)
        sections_doc = process_spans(spans)
        all_sections.update(sections_doc)

    return all_sections


def modify_key(dict, old_key, new_key):
    return {clave if clave != old_key else new_key: valor for clave, valor in dict.items()}

def send_data_to_rag(pdf):
    sections = segment_text_by_bold_titles(pdf)

    sections_fixed = modify_key(
        sections, "plataforma?",
        " ¿Existe alguna política de conducta para las interacciones en la plataforma?"
    )


    sections_fixed['¿Puedo ajustar la velocidad de reproducción de los videos?'] = [
        'Sí, puedes ajustar la velocidad de reproducción de los videos:', '1.',
        'Durante la reproducción del video, busca el ícono de configuración (generalmente un', 'engranaje)', '2.', 'Selecciona "Velocidad de reproducción"', '3.', 'Elige entre opciones como 0.5x, 1x, 1.25x, 1.5x, o 2x', 'Esta función está disponible tanto en la versión web como en la aplicación móvil.']

    for key, item in titles.items():
        sections_fixed = modify_key(
            sections_fixed,
            item,
            key
        )

    return [dict([("id", title), ("text", content)])
            for title, content in sections_fixed.items()]
