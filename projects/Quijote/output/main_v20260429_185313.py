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
# Fecha: 2026-04-29 18:53:13
# Iteraciones de corrección: 20
# Switch Llama: False
# Ejecución exitosa: False

from PyPDF2 import PdfFileReader

# Abre el archivo PDF con la ruta completa
with open('C:/ruta/completa/a/archivo.pdf', 'rb') as file:
    reader = PdfFileReader(file)
    
    # Verifica si el PDF está encriptado
    if reader.isEncrypted:
        # Desencripta el PDF con la contraseña (si es necesario)
        reader.decrypt('contraseña')
    
    # Lee el contenido del PDF
    for page_num in range(reader.numPages):
        page = reader.getPage(page_num)
        print(page.extractText())