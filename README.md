# 📚 Literatura Expandida

**Conversa con personajes de la literatura clásica universal mediante Inteligencia Artificial**

---

## ✨ ¿Qué es?

Literatura Expandida es una plataforma web que te permite chatear con personajes de 6 obras clásicas de la literatura mundial. Cada personaje responde con su propia personalidad, en el idioma original de la obra, y basa sus respuestas en fragmentos reales del texto.

---

## 🌍 Obras y Personajes Disponibles

| Obra | Autor | Idioma | Personajes Principales |
|------|-------|--------|----------------------|
| 📖 Don Quijote | Cervantes | 🇪🇸 Español | Don Quijote, Sancho Panza, Dulcinea, Rocinante, El Cura |
| 👹 Divina Comedia | Dante | 🇮🇹 Italiano | Dante, Virgilio, Beatrice, Lucifero, San Pedro |
| 🎭 Hamlet | Shakespeare | 🇬🇧 Inglés | Hamlet, Ofelia, Claudio, Gertrudis, El Fantasma |
| ⚗️ Fausto | Goethe | 🇩🇪 Alemán | Fausto, Mefistófeles, Gretchen, Wagner, Dios |
| 📜 Los Miserables | Victor Hugo | 🇫🇷 Francés | Jean Valjean, Javert, Cosette, Fantine, Marius |
| ⚓ Lusiadas | Camões | 🇵🇹 Portugués | Vasco da Gama, Adamastor, Inês de Castro, Rey Manuel, Tethys |

**Total:** 6 obras • 6 idiomas • 30 personajes

---

## 🚀 Cómo usar la demo

1.  **Selecciona una obra** del menú lateral
2.  **Elige un personaje** de los 5 disponibles
3.  **Escribe tu pregunta** en el chat
4.  **Recibe respuesta** en el estilo y idioma del personaje

### 💡 Ejemplos de preguntas:

- *"Sancho, ¿qué harías si te ofrecieran gobernar una ínsula?"*
- *"Dante, ¿qué fue lo más terrible que viste en el Infierno?"*
- *"Hamlet, ¿por qué dudas tanto en vengar a tu padre?"*
- *"Jean Valjean, ¿cómo encontraste la redención?"*

---

## 🛠️ Tecnologías usadas

- **Python 3.11** - Lenguaje principal
- **Streamlit** - Interfaz web interactiva
- **Docker** - Containerización para deployment
- **Qwen2.5:7b** - Modelo de IA para generar respuestas
- **Ollama** - Servidor local para ejecutar el modelo
- **Nomic Embed** - Embeddings multilingües para búsqueda
- **SpaCy** - Procesamiento de lenguaje natural
- **PyPDF + python-docx** - Lectura de documentos

---

## 📁 Estructura del proyecto

- **studio/** - Interfaz principal (literatura_expandida.py)
- **core/pipeline/** - Pre-procesamiento y extracción de personajes
- **core/utils/** - Utilidades (config_loader.py)
- **configs/books/** - Configuración de cada obra (6 archivos YAML)
- **configs/templates/** - Plantillas de personalidad
- **data/raw/** - Documentos originales (PDF, DOCX)
- **data/processed/** - Chunks y personajes procesados (JSON)
- **scripts/** - Utilidades y tests
- **requirements.txt** - Dependencias de Python
- **README.md** - Este archivo


---

## 💻 Ejecutar en tu computador

```bash
# 1. Clonar o descargar el proyecto
git clone https://github.com/Caanrique/literatura-expandida.git
cd literatura-expandida

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar la app
cd studio
streamlit run literatura_expandida.py


La aplicación se abrirá en: http://localhost:8501

---

## 🐳 Ejecutar con Docker

```bash
# 1. Construir la imagen Docker
docker build -t literatura-expandida .

# 2. Ejecutar el container
docker run -p 8501:8501 literatura-expandida

# 3. Abrir en el navegador
http://localhost:8501

Deploy en Hugging Face Spaces
Este proyecto está configurado para deploy automático en Hugging Face Spaces usando Docker:
El Dockerfile incluye todas las dependencias necesarias
El .dockerignore excluye archivos innecesarios
Al subir los archivos a HF Spaces, el build es automático
Demo pública: https://huggingface.co/spaces/Caanrique/literatura-expandida



🤝 Contribuciones
¡Las ideas y contribuciones son bienvenidas! Algunas sugerencias:
➕ Añadir nuevas obras literarias
🌐 Soporte para más idiomas
🎨 Mejoras en la interfaz
🧪 Tests automatizados
🐳 Versión Dockerizada


👨‍💻 Desarrollador
Camilo Manrique

- **GitHub:** https://github.com/Caanrique
- **LinkedIn:** https://linkedin.com/in/camilo-manrique-027b732b

📄 Licencia
Este proyecto está bajo la Licencia MIT.

---

📚 Literatura Expandida © 2026