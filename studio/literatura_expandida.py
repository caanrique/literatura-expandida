# ================================
# 📚 LITERATURA EXPANDIDA / EXPANDED LITERATURE
# ================================
# Interfaz genérica para chat con personajes de obras literarias clásicas
# RAG + Personajes con personalidad + Multilingüe + i18n support
# ================================

import streamlit as st
import json
import os
import sys
from typing import Dict, List, Any

# =============================================================================
# TRADUCCIONES DE INTERFAZ (i18n)
# =============================================================================
UI_TRANSLATIONS = {
    'es': {
        'page_title': 'Literatura Expandida',
        'title': '📚 Literatura Expandida',
        'subtitle': 'Conversa con personajes de la literatura clásica universal',
        'select_book': '📖 Selecciona una obra:',
        'select_character': '🎭 Selecciona un personaje:',
        'chat_input': 'Haz una pregunta al personaje...',
        'character_info': '📋 Personaje',
        'book_info': '📖 Obra',
        'data_info': '📊 Datos',
        'name': 'Nombre',
        'traits': 'Rasgos',
        'relationships': 'Relaciones',
        'title_label': 'Título',
        'author': 'Autor',
        'year': 'Año',
        'genre': 'Género',
        'language': 'Idioma',
        'chunks': 'Chunks',
        'characters': 'Personajes',
        'sidebar_title': '⚙️ Configuración',
        'sidebar_language': '🌐 Idioma de interfaz:',
        'sidebar_info': '💡 Consejo: Selecciona una obra y un personaje para comenzar a chatear.',
        'footer_title': '📚 Literatura Expandida | IA + Literatura Clásica',
        'footer_stats': '6 Obras • 6 Idiomas • 30 Personajes',
        'footer_credit': 'Desarrollado por <strong>Camilo Manrique</strong> • 2026 • Python + Streamlit + Qwen2.5',
        'footer_books': 'Don Quijote • Divina Commedia • Hamlet • Fausto • Les Misérables • Os Lusíadas',
        'warning_no_characters': '⚠️ No se encontraron personajes para esta obra.',
        'spinner_thinking': 'está pensando...',
        'view_sources': '📖 Ver fuentes de la obra',
        'fragment': 'Fragmento',
    },
    'en': {
        'page_title': 'Expanded Literature',
        'title': '📚 Expanded Literature',
        'subtitle': 'Chat with characters from classic universal literature',
        'select_book': '📖 Select a work:',
        'select_character': '🎭 Select a character:',
        'chat_input': 'Ask the character a question...',
        'character_info': '📋 Character',
        'book_info': '📖 Work',
        'data_info': '📊 Data',
        'name': 'Name',
        'traits': 'Traits',
        'relationships': 'Relationships',
        'title_label': 'Title',
        'author': 'Author',
        'year': 'Year',
        'genre': 'Genre',
        'language': 'Language',
        'chunks': 'Chunks',
        'characters': 'Characters',
        'sidebar_title': '⚙️ Settings',
        'sidebar_language': '🌐 Interface language:',
        'sidebar_info': '💡 Tip: Select a work and a character to start chatting.',
        'footer_title': '📚 Expanded Literature | AI + Classic Literature',
        'footer_stats': '6 Works • 6 Languages • 30 Characters',
        'footer_credit': 'Developed by <strong>Camilo Manrique</strong> • 2026 • Python + Streamlit + Qwen2.5',
        'footer_books': 'Don Quijote • Divina Commedia • Hamlet • Faust • Les Misérables • Os Lusíadas',
        'warning_no_characters': '⚠️ No characters found for this work.',
        'spinner_thinking': 'is thinking...',
        'view_sources': '📖 View sources from the work',
        'fragment': 'Fragment',
    }
}

def get_ui_text(key: str, lang: str = 'es') -> str:
    """Obtiene texto de interfaz en el idioma seleccionado."""
    return UI_TRANSLATIONS.get(lang, UI_TRANSLATIONS['es']).get(key, key)

# ================================
# CONFIGURACIÓN DE PÁGINA (con idioma dinámico)
# ================================
# Determinar idioma para page_title (antes de usar session_state)
default_lang = 'es'
try:
    # Intentar leer de session_state si ya existe
    if 'interface_lang' in st.session_state:
        default_lang = st.session_state.interface_lang
except:
    pass

st.set_page_config(
    page_title=get_ui_text('page_title', default_lang),
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
        'language_name': 'English',
        'genre': 'Tragedy',
        'description': 'The Prince of Denmark seeks to avenge his father\'s death',
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

def get_project_root() -> str:
    """Obtiene la ruta absoluta del proyecto."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    return project_root

def load_characters(book_id: str) -> Dict[str, Any]:
    """Carga los personajes de una obra desde el JSON."""
    project_root = get_project_root()
    file_path = os.path.join(project_root, f"data/processed/{book_id}_characters.json")
    
    print(f"🔍 DEBUG: Buscando personajes en: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ ERROR: Archivo no encontrado: {file_path}")
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Personajes cargados: {data.get('total_characters', 0)}")
    return data

def load_processed_data(book_id: str) -> Dict[str, Any]:
    """Carga los chunks procesados de una obra."""
    project_root = get_project_root()
    file_path = os.path.join(project_root, f"data/processed/{book_id}_processed.json")
    
    print(f"🔍 DEBUG: Buscando processed en: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ ERROR: Archivo no encontrado: {file_path}")
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
    query_words = query.lower().split()
    
    scored_chunks = []
    for chunk in chunks:
        text = chunk.get('text', '').lower()
        score = sum(1 for word in query_words if word in text)
        if score > 0:
            scored_chunks.append((score, chunk))
    
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored_chunks[:top_k]]

def generate_response(prompt: str, character_name: str, sources: List[Dict], book_config: Dict, character_data: Dict) -> str:
    """
    Genera respuesta usando Qwen2.5 vía Hugging Face Inference API.
    """
    import os
    from huggingface_hub import InferenceClient
    
    context_text = ""
    if sources:
        context_text = "\n\n".join([f"[Fragmento {i+1}] {s.get('text', '')[:400]}" for i, s in enumerate(sources[:3])])
    
    traits = ', '.join(character_data.get('traits', ['personaje principal']))
    relationships = character_data.get('relationships', {})
    description = character_data.get('description', '')
    language = book_config.get('language', 'es')
    
    language_instructions = {
        'es': 'Responde en español, usando lenguaje y estilo apropiados para la época de la obra.',
        'en': 'Respond in English, using language and style appropriate for the era of the work.',
        'it': 'Rispondi in italiano, usando linguaggio e stile appropriati per l\'epoca dell\'opera.',
        'de': 'Antworte auf Deutsch, verwende Sprache und Stil, die der Epoche des Werkes angemessen sind.',
        'fr': 'Répondez en français, en utilisant un langage et un style appropriés à l\'époque de l\'œuvre.',
        'pt': 'Responda em português, usando linguagem e estilo apropriados para a época da obra.'
    }
    
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

    hf_token = os.getenv("HF_TOKEN", "")
    
    if not hf_token:
        return f"*[Modo demo: Token de HF no configurado]*\n\nComo {character_name}, te comparto mi perspectiva sobre: {prompt}"
    
    try:
        # Cliente nativo de Hugging Face
        from huggingface_hub import InferenceClient
        
        client = InferenceClient(token=hf_token)
        
        # Usar modelo pequeño que SÍ funciona en capa gratuita
        response = client.text_generation(
            prompt=system_prompt + f"\n\nUsuario: {prompt}\n\n{character_name}:",
            model="google/gemma-2b-it",
            max_new_tokens=512,
            temperature=0.7,
            top_p=0.9,
            stop=["Usuario:", character_name + ":"]
        )
        
        return response.strip()
        
    except Exception as e:
        return f"*[Error al conectar con HF API: {str(e)}]*\n\nComo {character_name}, te comparto mi perspectiva: {prompt}"
# ================================
# INICIALIZAR SESSION STATE
# ================================

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'interface_lang' not in st.session_state:
    st.session_state.interface_lang = 'es'

# Determinar obra por defecto según idioma
default_book = 'hamlet' if st.session_state.interface_lang == 'en' else 'don_quijote'

if 'selected_book' not in st.session_state or st.session_state.selected_book is None:
    default_book = 'hamlet' if st.session_state.interface_lang == 'en' else 'don_quijote'
    st.session_state.selected_book = default_book

if 'selected_character' not in st.session_state:
    st.session_state.selected_character = None

if 'characters_data' not in st.session_state:
    st.session_state.characters_data = None

# ================================
# HEADER
# ================================

st.markdown(f'<h1 class="main-title">{get_ui_text("title", st.session_state.interface_lang)}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="subtitle">{get_ui_text("subtitle", st.session_state.interface_lang)}</p>', unsafe_allow_html=True)

# ================================
# BARRA LATERAL (UNIFICADA)
# ================================

with st.sidebar:
    # Selector de idioma de interfaz
    st.subheader(get_ui_text('sidebar_title', st.session_state.interface_lang))
    
    interface_lang = st.selectbox(
        get_ui_text('sidebar_language', st.session_state.interface_lang),
        options=['es', 'en'],
        format_func=lambda x: '🇪🇸 Español' if x == 'es' else '🇬🇧 English',
        index=0 if st.session_state.interface_lang == 'es' else 1
    )
    
    if interface_lang != st.session_state.interface_lang:
        st.session_state.interface_lang = interface_lang
        st.rerun()
    
    st.info(get_ui_text('sidebar_info', st.session_state.interface_lang))
    st.divider()
    
    # Selector de obra
    book_options = {
        f"{config['flag']} {config['title']} ({config['language_name']})": book_id 
        for book_id, config in BOOKS_CONFIG.items()
    }
    
    selected_label = st.selectbox(
        get_ui_text('select_book', st.session_state.interface_lang),
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
            get_ui_text('select_character', st.session_state.interface_lang),
            options=list(character_options.keys()),
            index=0
        )
        
        st.session_state.selected_character = character_options[selected_char_label]
        character_data = characters.get(st.session_state.selected_character, {})
        
        # Info del personaje
        st.divider()
        st.subheader(get_ui_text('character_info', st.session_state.interface_lang))
        st.markdown(f"**{get_ui_text('name', st.session_state.interface_lang)}:** {character_data.get('canonical_name', 'N/A')}")
        
        traits = character_data.get('traits', [])
        if traits:
            st.markdown(f"**{get_ui_text('traits', st.session_state.interface_lang)}:** {', '.join(traits)}")
        
        relationships = character_data.get('relationships', {})
        if relationships:
            st.markdown(f"**{get_ui_text('relationships', st.session_state.interface_lang)}:** {len(relationships)}")
        
        # Info de la obra
        st.divider()
        st.subheader(get_ui_text('book_info', st.session_state.interface_lang))
        st.markdown(f"**{get_ui_text('title_label', st.session_state.interface_lang)}:** {book_config['title']}")
        st.markdown(f"**{get_ui_text('author', st.session_state.interface_lang)}:** {book_config['author']}")
        st.markdown(f"**{get_ui_text('year', st.session_state.interface_lang)}:** {book_config['year']}")
        st.markdown(f"**{get_ui_text('genre', st.session_state.interface_lang)}:** {book_config['genre']}")
        st.markdown(f"**{get_ui_text('language', st.session_state.interface_lang)}:** {book_config['language_name']}")
        
        # Estadísticas
        st.divider()
        st.subheader(get_ui_text('data_info', st.session_state.interface_lang))
        processed_data = load_processed_data(st.session_state.selected_book)
        if processed_data:
            chunks = processed_data.get('chunks', [])
            st.markdown(f"**{get_ui_text('chunks', st.session_state.interface_lang)}:** {len(chunks)}")
            st.markdown(f"**{get_ui_text('characters', st.session_state.interface_lang)}:** {len(characters)}")
    else:
        st.warning(get_ui_text('warning_no_characters', st.session_state.interface_lang))

# ================================
# ÁREA PRINCIPAL - CHAT
# ================================

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander(get_ui_text('view_sources', st.session_state.interface_lang)):
                for i, chunk in enumerate(message["sources"], 1):
                    st.markdown(f"**{get_ui_text('fragment', st.session_state.interface_lang)} {i}:** {chunk.get('text', '')[:300]}...")

# Input del usuario
if prompt := st.chat_input(get_ui_text('chat_input', st.session_state.interface_lang)):
    # Agregar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generar respuesta
    with st.chat_message("assistant"):
        thinking_text = get_ui_text('spinner_thinking', st.session_state.interface_lang)
        with st.spinner(f"🎭 {st.session_state.selected_character} {thinking_text}"):
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

col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    # Título pequeño
    st.markdown(
        f"<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
        f"{get_ui_text('footer_title', st.session_state.interface_lang)}"
        "</div>",
        unsafe_allow_html=True
    )
    
    # Subtítulo
    st.markdown(
        f"<div style='text-align: center; color: #888; font-size: 0.8rem; margin: 10px 0;'>"
        f"{get_ui_text('footer_stats', st.session_state.interface_lang)}"
        "</div>",
        unsafe_allow_html=True
    )
    
    # Espacio
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    # Botones de redes
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
    
    # Créditos (se mantienen en español como atribución personal)
    st.markdown(
        f"<div style='text-align: center; color: #aaa; font-size: 0.75rem;'>"
        f"{get_ui_text('footer_credit', st.session_state.interface_lang)}"
        "</div>",
        unsafe_allow_html=True
    )
    
    st.markdown(
        f"<div style='text-align: center; color: #aaa; font-size: 0.75rem; margin-top: 5px;'>"
        f"{get_ui_text('footer_books', st.session_state.interface_lang)}"
        "</div>",
        unsafe_allow_html=True
    )
