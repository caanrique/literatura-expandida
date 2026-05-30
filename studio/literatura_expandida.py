# ================================
# 📚 LITERATURA EXPANDIDA
# ================================
# Interfaz genérica para chat con personajes de obras literarias clásicas
# RAG + Personajes con personalidad + Multilingüe
# ================================

import streamlit as st
import json
import os
import sys
from typing import Dict, List, Any

# ================================
# CONFIGURACIÓN DE PÁGINA
# ================================
st.set_page_config(
    page_title="Literatura Expandida",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# ESTILOS PERSONALIZADOS
# ================================
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .character-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ================================
# CARGA DE CONFIGURACIONES
# ================================

BOOKS_CONFIG = {
    'don_quijote': {
        'title': 'Don Quijote de la Mancha',
        'author': 'Miguel de Cervantes',
        'year': 1605,
        'language': 'es',
        'language_name': 'Español',
        'genre': 'Novela',
        'description': 'Obra fundacional de la literatura moderna española',
        'flag': '🇪🇸'
    },
    'divina_comedia': {
        'title': 'Divina Commedia',
        'author': 'Dante Alighieri',
        'year': 1320,
        'language': 'it',
        'language_name': 'Italiano',
        'genre': 'Poema Épico',
        'description': 'Viaje de Dante a través del Infierno, Purgatorio y Paraíso',
        'flag': '🇮🇹'
    },
    'hamlet': {
        'title': 'Hamlet',
        'author': 'William Shakespeare',
        'year': 1603,
        'language': 'en',
        'language_name': 'Inglés',
        'genre': 'Tragedia',
        'description': 'El príncipe de Dinamarca busca vengar la muerte de su padre',
        'flag': '🇬🇧'
    },
    'fausto': {
        'title': 'Fausto',
        'author': 'Johann Wolfgang von Goethe',
        'year': 1808,
        'language': 'de',
        'language_name': 'Alemán',
        'genre': 'Drama Filosófico',
        'description': 'Un erudito hace un pacto con el diablo buscando conocimiento infinito',
        'flag': '🇩🇪'
    },
    'los_miserables': {
        'title': 'Les Misérables',
        'author': 'Victor Hugo',
        'year': 1862,
        'language': 'fr',
        'language_name': 'Francés',
        'genre': 'Novela Social',
        'description': 'Justicia, redención y revolución en la Francia del siglo XIX',
        'flag': '🇫🇷'
    },
    'lusiadas': {
        'title': 'Os Lusíadas',
        'author': 'Luís de Camões',
        'year': 1572,
        'language': 'pt',
        'language_name': 'Portugués',
        'genre': 'Poema Épico',
        'description': 'Los viajes de Vasco da Gama y la historia de Portugal',
        'flag': '🇵🇹'
    }
}

# ================================
# FUNCIONES AUXILIARES
# ================================

# ================================
# FUNCIONES AUXILIARES (CORREGIDAS)
# ================================

def get_project_root() -> str:
    """Obtiene la ruta absoluta del proyecto."""
    # Literatura Expandida está en studio/, así que subimos un nivel
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)  # Sube de studio/ a local-assistant/
    return project_root

def load_characters(book_id: str) -> Dict[str, Any]:
    """Carga los personajes de una obra desde el JSON."""
    project_root = get_project_root()
    file_path = os.path.join(project_root, f"data/processed/{book_id}_characters.json")
    
    print(f"🔍 DEBUG: Buscando personajes en: {file_path}")  # Debug
    
    if not os.path.exists(file_path):
        print(f"❌ ERROR: Archivo no encontrado: {file_path}")  # Debug
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Personajes cargados: {data.get('total_characters', 0)}")  # Debug
    return data

def load_processed_data(book_id: str) -> Dict[str, Any]:
    """Carga los chunks procesados de una obra."""
    project_root = get_project_root()
    file_path = os.path.join(project_root, f"data/processed/{book_id}_processed.json")
    
    print(f"🔍 DEBUG: Buscando processed en: {file_path}")  # Debug
    
    if not os.path.exists(file_path):
        print(f"❌ ERROR: Archivo no encontrado: {file_path}")  # Debug
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
    

def get_character_prompt(character: Dict, book_config: Dict) -> str:
    """Genera el prompt de sistema para un personaje."""
    name = character.get('canonical_name', 'Personaje')
    traits = ', '.join(character.get('traits', ['personaje principal']))
    relationships = character.get('relationships', {})
    description = character.get('description', '')
    language = book_config.get('language', 'es')
    
    # Instrucciones de idioma
    language_instructions = {
        'es': 'Responde en español, usando lenguaje apropiado para la época.',
        'en': 'Respond in English, using language appropriate for the era.',
        'it': 'Rispondi in italiano, usando linguaggio appropriato per l\'epoca.',
        'de': 'Antworte auf Deutsch, verwende sprachliche Angemessenheit für die Epoche.',
        'fr': 'Répondez en français, en utilisant un langage approprié pour l\'époque.',
        'pt': 'Responda em português, usando linguagem apropriada para a época.'
    }
    
    prompt = f"""Eres {name}, un personaje literario clásico.

TU PERSONALIDAD: {traits}
TU CONTEXTO: {description}

RELACIONES: {', '.join([f'{k} ({v})' for k, v in relationships.items()]) if relationships else 'N/A'}

{language_instructions.get(language, 'Responde en el idioma original de la obra.')}

INSTRUCCIONES:
- Responde siempre en primera persona como {name}
- Mantén coherencia con tu personalidad y época
- Si no sabes algo, responde con la sabiduría de tu personaje
- Sé fiel a tu rol en la obra original

Usuario:"""
    
    return prompt

def search_chunks(query: str, chunks: List[Dict], top_k: int = 5) -> List[Dict]:
    """Búsqueda simple por similitud de texto (TF-IDF básico)."""
    # Para MVP, retornamos los primeros chunks que contengan palabras clave
    query_words = query.lower().split()
    
    scored_chunks = []
    for chunk in chunks:
        text = chunk.get('text', '').lower()
        score = sum(1 for word in query_words if word in text)
        if score > 0:
            scored_chunks.append((score, chunk))
    
    # Ordenar por score y retornar top_k
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored_chunks[:top_k]]

def generate_response(prompt: str, character_name: str, sources: List[Dict], book_config: Dict, character_data: Dict) -> str:
    """
    Genera respuesta usando Qwen2.5 vía Hugging Face Inference API.
    """
    import os
    from huggingface_hub import InferenceClient
    
    # Preparar contexto de RAG
    context_text = ""
    if sources:
        context_text = "\n\n".join([f"[Fragmento {i+1}] {s.get('text', '')[:400]}" for i, s in enumerate(sources[:3])])
    
    # Preparar datos del personaje
    traits = ', '.join(character_data.get('traits', ['personaje principal']))
    relationships = character_data.get('relationships', {})
    description = character_data.get('description', '')
    language = book_config.get('language', 'es')
    
    # Instrucciones de idioma
    language_instructions = {
        'es': 'Responde en español, usando lenguaje y estilo apropiados para la época de la obra.',
        'en': 'Respond in English, using language and style appropriate for the era of the work.',
        'it': 'Rispondi in italiano, usando linguaggio e stile appropriati per l\'epoca dell\'opera.',
        'de': 'Antworte auf Deutsch, verwende Sprache und Stil, die der Epoche des Werkes angemessen sind.',
        'fr': 'Répondez en français, en utilisant un langage et un style appropriés à l\'époque de l\'œuvre.',
        'pt': 'Responda em português, usando linguagem e estilo apropriados para a época da obra.'
    }
    
    # Construir prompt de sistema
    system_prompt = f"""Eres {character_name}, un personaje de literatura clásica.

TU PERSONALIDAD: {traits}
TU CONTEXTO EN LA OBRA: {description}
TUS RELACIONES: {', '.join([f'{k} ({v})' for k, v in relationships.items()]) if relationships else 'N/A'}

{language_instructions.get(language, 'Responde en el idioma original de la obra.')}

INSTRUCCIONES:
1. Responde SIEMPRE en primera persona como {character_name}
2. Mantén coherencia con tu personalidad, época y rol en la obra
3. Usa el contexto proporcionado para fundamentar tu respuesta, pero NO lo copies literalmente
4. Si no sabes algo, responde con la sabiduría y perspectiva de tu personaje
5. Sé auténtico: habla como lo haría {character_name} en la obra original

CONTEXTO DE LA OBRA (fragmentos relevantes):
{context_text if context_text else 'No hay contexto específico disponible para esta pregunta.'}

Ahora, responde a la pregunta del usuario como {character_name}:"""

    # Obtener token de Hugging Face
    hf_token = os.getenv("HF_TOKEN", "")
    
    if not hf_token:
        return f"*[Modo demo: Token de HF no configurado]*\n\nComo {character_name}, te comparto mi perspectiva sobre: {prompt}"
    
    try:
        # Inicializar cliente de HF Inference API
        client = InferenceClient(token=hf_token)
        
        # Construir mensajes para API conversacional
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        # Generar respuesta con Qwen2.5 usando chat_completion
        response = client.chat_completion(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=messages,
            max_tokens=512,
            temperature=0.7,
            top_p=0.9
        )
        
        # Extraer el contenido de la respuesta
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"*[Error al conectar con HF API: {str(e)}]*\n\nComo {character_name}, te comparto mi perspectiva: {prompt}"
    
# ================================
# INICIALIZAR SESSION STATE
# ================================

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'selected_book' not in st.session_state:
    st.session_state.selected_book = 'don_quijote'

if 'selected_character' not in st.session_state:
    st.session_state.selected_character = None

if 'characters_data' not in st.session_state:
    st.session_state.characters_data = None

# ================================
# HEADER
# ================================

st.markdown('<h1 class="main-title">📚 Literatura Expandida</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Conversa con personajes de la literatura clásica universal</p>', unsafe_allow_html=True)

# ================================
# BARRA LATERAL
# ================================

with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Selector de obra
    book_options = {
        f"{config['flag']} {config['title']} ({config['language_name']})": book_id 
        for book_id, config in BOOKS_CONFIG.items()
    }
    
    selected_label = st.selectbox(
        "📖 Selecciona una obra:",
        options=list(book_options.keys()),
        index=list(book_options.values()).index(st.session_state.selected_book)
    )
    
    st.session_state.selected_book = book_options[selected_label]
    book_config = BOOKS_CONFIG[st.session_state.selected_book]
    
    # Cargar personajes
    st.session_state.characters_data = load_characters(st.session_state.selected_book)

        # DEBUG: Ver qué está cargando
    print(f"🔍 DEBUG: selected_book = {st.session_state.selected_book}")
    print(f"🔍 DEBUG: characters_data = {st.session_state.characters_data}")
    
    if st.session_state.characters_data:
        characters = st.session_state.characters_data.get('characters', {})
        print(f"🔍 DEBUG: characters keys = {list(characters.keys())}")
    
    if st.session_state.characters_data:
        characters = st.session_state.characters_data.get('characters', {})
        character_options = {
            v.get('canonical_name', k): k 
            for k, v in characters.items()
        }
        
        selected_char_label = st.selectbox(
            "🎭 Selecciona un personaje:",
            options=list(character_options.keys()),
            index=0
        )
        
        st.session_state.selected_character = character_options[selected_char_label]
        character_data = characters.get(st.session_state.selected_character, {})
        
        # Info del personaje
        st.divider()
        st.subheader("📋 Personaje")
        st.markdown(f"**Nombre:** {character_data.get('canonical_name', 'N/A')}")
        
        traits = character_data.get('traits', [])
        if traits:
            st.markdown(f"**Rasgos:** {', '.join(traits)}")
        
        relationships = character_data.get('relationships', {})
        if relationships:
            st.markdown(f"**Relaciones:** {len(relationships)}")
        
        # Info de la obra
        st.divider()
        st.subheader("📖 Obra")
        st.markdown(f"**Título:** {book_config['title']}")
        st.markdown(f"**Autor:** {book_config['author']}")
        st.markdown(f"**Año:** {book_config['year']}")
        st.markdown(f"**Género:** {book_config['genre']}")
        st.markdown(f"**Idioma:** {book_config['language_name']}")
        
        # Estadísticas
        st.divider()
        st.subheader("📊 Datos")
        processed_data = load_processed_data(st.session_state.selected_book)
        if processed_data:
            chunks = processed_data.get('chunks', [])
            st.markdown(f"**Chunks:** {len(chunks)}")
            st.markdown(f"**Personajes:** {len(characters)}")
    else:
        st.warning("⚠️ No se encontraron personajes para esta obra.")

# ================================
# ÁREA PRINCIPAL - CHAT
# ================================

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📖 Ver fuentes de la obra"):
                for i, chunk in enumerate(message["sources"], 1):
                    st.markdown(f"**Fragmento {i}:** {chunk.get('text', '')[:300]}...")

# Input del usuario
if prompt := st.chat_input("Haz una pregunta al personaje..."):
    # Agregar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generar respuesta
    with st.chat_message("assistant"):
        with st.spinner(f"🎭 {st.session_state.selected_character} está pensando..."):
            # Cargar datos
            processed_data = load_processed_data(st.session_state.selected_book)
            chunks = processed_data.get('chunks', []) if processed_data else []
            
            # Buscar chunks relevantes
            sources = search_chunks(prompt, chunks, top_k=3)
            
           # Generar respuesta
            character_data = st.session_state.characters_data['characters'][st.session_state.selected_character]
            character_name = character_data.get('canonical_name', 'Personaje')
            response = generate_response(prompt, character_name, sources, book_config, character_data)
            
            st.markdown(response)
            
            # Agregar a historial
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "sources": sources
            })

# ================================
# FOOTER CON REDES SOCIALES
# ================================

st.divider()

# Usar columnas para centrar el contenido
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    # Título pequeño
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
        "📚 <strong>Literatura Expandida</strong> | IA + Literatura Clásica"
        "</div>",
        unsafe_allow_html=True
    )
    
    # Subtítulo
    st.markdown(
        "<div style='text-align: center; color: #888; font-size: 0.8rem; margin: 10px 0;'>"
        "6 Obras • 6 Idiomas • 30 Personajes"
        "</div>",
        unsafe_allow_html=True
    )
    
    # Espacio
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    # Botones de redes (cada uno en su propio markdown para evitar conflictos)
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        st.markdown(
            f"""
            <a href="https://github.com/Caanrique" target="_blank" style="text-decoration: none;">
                <div style="background-color: #24292e; color: white; padding: 10px 20px; 
                            border-radius: 6px; text-align: center; font-size: 0.9rem; 
                            font-weight: bold; cursor: pointer;">
                    GitHub 💻
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )
    
    with btn_col2:
        st.markdown(
            f"""
            <a href="https://linkedin.com/in/camilo-manrique-027b732b" target="_blank" style="text-decoration: none;">
                <div style="background-color: #0077b5; color: white; padding: 10px 20px; 
                            border-radius: 6px; text-align: center; font-size: 0.9rem; 
                            font-weight: bold; cursor: pointer;">
                    LinkedIn 💼
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )
    
    # Espacio
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    # Créditos
    st.markdown(
        "<div style='text-align: center; color: #aaa; font-size: 0.75rem;'>"
        "Desarrollado por <strong>Camilo Manrique</strong> • 2026 • Python + Streamlit + Qwen2.5"
        "</div>",
        unsafe_allow_html=True
    )
    
    st.markdown(
        "<div style='text-align: center; color: #aaa; font-size: 0.75rem; margin-top: 5px;'>"
        "Don Quijote • Divina Commedia • Hamlet • Fausto • Les Misérables • Os Lusíadas"
        "</div>",
        unsafe_allow_html=True
    )