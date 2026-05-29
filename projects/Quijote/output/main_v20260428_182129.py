# Generado por LangGraph + Qwen Local
# Proyecto: Quijote
# Prompt: Lee SOLO la primera página de 'quijote_1.pdf' y extrae el texto.
#Muestra el contenido. Usa pypdf y limita a reader.pages[0].
# Modelo clasificador: qwen-2.5
# Modelo ejecutor: qwen-coder-7b
# Fecha: 2026-04-28 18:21:29
# Iteraciones de corrección: 7
# Switch Llama: False
# Ejecución exitosa: False

import PyPDF2

# Abre el archivo PDF
with open('quijote_1.pdf', 'rb') as file:
    reader = PyPDF2.PdfFileReader(file)
    
    # Lee la primera página
    page = reader.getPage(0)
    
    # Extrae y muestra el texto
    text = page.extractText()
    print(text)