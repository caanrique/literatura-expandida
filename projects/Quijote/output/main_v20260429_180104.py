# Generado por LangGraph + Qwen Local
# Proyecto: Quijote
# Prompt: Escribe un script Python COMPLETO y EJECUTABLE que:
# Prompt: 1. Importe: from pypdf import PdfReader
# Prompt: 2. Lea el archivo: quijote_1.pdf
# Prompt: 3. Extraiga el texto de la primera página
# Prompt: 4. Imprima el texto con print()
# Prompt: 
# Prompt: El archivo está en la misma carpeta donde se ejecuta el script.
# Prompt: No incluyas explicaciones, solo el código.
# Modelo clasificador: qwen-2.5
# Modelo ejecutor: qwen-coder-7b
# Fecha: 2026-04-29 18:01:04
# Iteraciones de corrección: 7
# Switch Llama: False
# Ejecución exitosa: False

from PyPDF2 import PdfFileReader

# Crear un lector PDF
with open("quijote_1.pdf", "rb") as file:
    reader = PdfFileReader(file)

# Extraer el texto de la primera página
text = reader.getPage(0).extractText()

# Imprimir el texto
print(text)