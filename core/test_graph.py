from graph import graph  # Importa tu grafo de graph.py

# Ejecutar directamente
result = graph.invoke({"messages": ["Escribe una función en Python que sume dos números"]})

print("📝 Respuesta de Qwen:")
print(result["response"])