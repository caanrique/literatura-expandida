# Generado por LangGraph + Qwen Local
# Proyecto: Quijote
# Prompt: Lee SOLO la primera página de 'quijote_1.pdf' y extrae el texto.
# Usa la librería 'pypdf'. Muestra el resultado.
# Modelo clasificador: qwen-2.5
# Modelo ejecutor: qwen-coder-7b
# Fecha: 2026-04-29 17:40:16
# Iteraciones de corrección: 3
# Switch Llama: False
# Ejecución exitosa: True

import PyPDF2

def extract_text_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfFileReader(file)
            if reader.numPages > 0:
                page = reader.getPage(0)
                text = page.extractText()
                return text
            else:
                return "No pages found in the PDF."
    except FileNotFoundError:
        return f"Error: The file '{file_path}' was not found."

# Example usage
file_path = 'C:/ruta/completa/a/quijote_1.pdf'  # Asegúrate de que el archivo esté en el mismo directorio o proporciona la ruta completa
text = extract_text_from_pdf(file_path)
print(text)