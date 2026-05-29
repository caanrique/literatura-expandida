# Generado por LangGraph + Qwen Local
# Proyecto: Quijote
# Prompt: Escribe código Python que use 'from pypdf import PdfReader' para leer 'quijote_1.pdf'.
# Prompt: Extrae y muestra el texto de la primera página.
# Modelo clasificador: qwen-2.5
# Modelo ejecutor: qwen-coder-7b
# Fecha: 2026-04-29 17:54:05
# Iteraciones de corrección: 7
# Switch Llama: False
# Ejecución exitosa: False

from PyPDF2 import PdfReader

# Crear un objeto PdfReader para leer el archivo PDF
pdf_reader = PdfReader(open('quijote_1.pdf', 'rb'))

# Obtener el texto de la primera página
first_page_text = pdf_reader.pages[0].extract_text()

# Mostrar el texto de la primera página
print(first_page_text)