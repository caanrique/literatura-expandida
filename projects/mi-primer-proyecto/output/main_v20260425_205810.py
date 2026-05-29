# Generado por LangGraph + Qwen Local
# Prompt: "Crea una clase llamada Persona con nombre y edad"

# Modelo clasificador: qwen-2.5
# Modelo ejecutor: qwen-coder-7b
# Fecha: 2026-04-25 20:58:10
# Switch Llama: False

```python
class Persona:
    def __init__(self, nombre, edad):
        self.nombre = nombre
        self.edad = edad

# Ejemplo de uso
persona1 = Persona("Juan", 30)
print(f"Nombre: {persona1.nombre}, Edad: {persona1.edad}")
```