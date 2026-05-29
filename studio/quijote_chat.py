# ================================
# INTERFAZ: Chat con personajes del Quijote (Local)
# ================================
# Propósito: Interfaz Streamlit para interactuar con personajes usando RAG
# ================================

import streamlit as st
import os
import sys
import json
from datetime import datetime

# Agregar raíz del proyecto al path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.quijote_rag import (
    load_quijote_data, search_chunks, format_context_for_prompt, 
    get_character_context_hint, EMBEDDING_MODEL
)
from core.quijote_characters import get_character_prompt, list_available_characters
from langchain_ollama import ChatOllama
from sentence_transformers import SentenceTransformer

# ================================
# CONFIGURACIÓN DE PÁGINA
# ================================
st.set_page_config(
    page_title="🎭 Quijote Characters AI",
    page_icon="🗡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# ESTADO DE SESIÓN
# ================================
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'selected_character' not in st.session_state:
    st.session_state.selected_character = "don_quijote"
if 'quijote_data' not in st.session_state:
    st.session_state.quijote_data = None
if 'embedding_model' not in st.session_state:
    st.session_state.embedding_model = None

# ================================
# CARGA INICIAL DE DATOS
# ================================
@st.cache_resource
def load_quijote_resources():
    """
    Carga datos y modelo de embeddings (cacheado para rendimiento).
    """
    # Cargar JSON procesado
    json_path = os.path.join(project_root, "projects", "Quijote", "data", "quijote_processed.json")
    if not os.path.exists(json_path):
        st.error(f"❌ No se encontró: {json_path}")
        return None, None
    
    data = load_quijote_data(json_path)
    
    # Cargar modelo de embeddings
    model = SentenceTransformer(EMBEDDING_MODEL, trust_remote_code=True)
    
    return data, model

# ================================
# BARRA LATERAL
# ================================
with st.sidebar:
    st.title("🎭 Quijote Characters AI")
    st.markdown("*Conversa con los personajes del Quijote, con contexto real del libro*")
    
    # Selector de personaje
    characters = list_available_characters()
    character_names = {
        "don_quijote": "🗡️ Don Quijote",
        "sancho_panaza": "🫖 Sancho Panza", 
        "dulcinea": "👑 Dulcinea"
    }
    
    selected_char_key = st.selectbox(
        "Elige un personaje:",
        options=characters,
        format_func=lambda x: character_names.get(x, x),
        index=characters.index(st.session_state.selected_character) if st.session_state.selected_character in characters else 0
    )
    
    if selected_char_key != st.session_state.selected_character:
        st.session_state.selected_character = selected_char_key
        st.session_state.messages = []  # Resetear chat al cambiar personaje
        st.rerun()
    
    st.divider()
    
    # Información del personaje
    char_descriptions = {
        "don_quijote": "El caballero de la triste figura. Idealista, valiente, y un poco loco.",
        "sancho_panaza": "El escudero fiel. Práctico, sabio en refranes, y de buen corazón.",
        "dulcinea": "La musa inspiradora. Poética, sabia, y amor idealizado."
    }
    st.info(f"**{character_names[selected_char_key]}**\n\n{char_descriptions.get(selected_char_key, '')}")
    
    st.divider()
    
    # Estado de carga
    if st.session_state.quijote_data is None:
        with st.spinner("📚 Cargando el Quijote..."):
            data, model = load_quijote_resources()
            if data and model:
                st.session_state.quijote_data = data
                st.session_state.embedding_model = model
                st.success("✅ ¡Listo para conversar!")
            else:
                st.error("❌ Error al cargar datos")
    
    st.caption(f"Chunks disponibles: {len(st.session_state.quijote_data.get('chunks', [])) if st.session_state.quijote_data else 0}")
    st.caption(f"Embeddings: {st.session_state.quijote_data.get('processing_info', {}).get('embedding_model', 'N/A') if st.session_state.quijote_data else 'N/A'}")

# ================================
# FUNCIONES DE CHAT
# ================================

def generate_response(query: str, character: str, context: str) -> str:
    """
    Genera respuesta del personaje usando Qwen + contexto RAG.
    """
    # Configurar modelo
    llm = ChatOllama(
        model="qwen2.5:7b",
        base_url="http://localhost:11434",
        temperature=0.7,  # Más creatividad para personajes
        num_ctx=4096
    )
    
    # Generar prompt con personalidad + contexto
    system_prompt = get_character_prompt(character, context)
    
    # Mensajes para el modelo
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]
    
    # Generar respuesta
    response = llm.invoke(messages)
    return response.content

def search_and_respond(query: str, character: str) -> tuple[str, list]:
    """
    Busca contexto relevante y genera respuesta del personaje.
    Returns: (respuesta, chunks usados)
    """
    if not st.session_state.quijote_data or not st.session_state.embedding_model:
        return "⚠️ Los datos del Quijote aún no están cargados. Por favor espera...", []
    
    # Preparar datos
    chunks = st.session_state.quijote_data["chunks"]
    embeddings = [c["embedding"] for c in chunks]
    
    # Añadir pista de personaje a la búsqueda
    character_hint = get_character_context_hint(character)
    enhanced_query = f"{query} {character_hint}".strip()
    
    # Buscar chunks relevantes
    relevant_chunks = search_chunks(
        query=enhanced_query,
        chunks=chunks,
        embeddings=embeddings,
        query_embedding=st.session_state.embedding_model.encode(enhanced_query).tolist(),
        top_k=5
    )
    
    # Formatear contexto para prompt
    context = format_context_for_prompt(relevant_chunks, character)
    
    # Generar respuesta
    response = generate_response(query, character, context)
    
    return response, relevant_chunks

# ================================
# INTERFAZ PRINCIPAL
# ================================

st.title(f"💬 Conversando con {character_names.get(st.session_state.selected_character, st.session_state.selected_character)}")

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📖 Ver fuentes del Quijote"):
                for i, chunk in enumerate(message["sources"], 1):
                    st.markdown(f"**Fragmento {i}:** {chunk['text'][:300]}...")
                    st.caption(f"Posición: {chunk.get('metadata', {}).get('position', 'N/A')}")

# Input del usuario
if prompt := st.chat_input("Escribe tu mensaje..."):
    # Agregar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generar respuesta del personaje
    with st.chat_message("assistant"):
        with st.spinner(f"🎭 {character_names.get(st.session_state.selected_character)} está pensando..."):
            response, sources = search_and_respond(prompt, st.session_state.selected_character)
            st.markdown(response)
            
            # Mostrar fuentes si hay
            if sources:
                with st.expander("📖 Ver fuentes del Quijote"):
                    for i, chunk in enumerate(sources, 1):
                        st.markdown(f"**Fragmento {i}:** {chunk['text'][:300]}...")
                        
                        # ✅ Similitud con validación (CORRECTAMENTE INDENTADO)
                        similarity = chunk.get('similarity')
                        if isinstance(similarity, (int, float)):
                            sim_text = f"{similarity:.3f}"
                        else:
                            sim_text = "N/A"
                        st.caption(f"Posición: {chunk.get('metadata', {}).get('position', 'N/A')} | Similitud: {sim_text}")
            
            # Agregar respuesta al historial
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response,
                "sources": sources
            })

# ================================
# FOOTER
# ================================
st.divider()
st.caption("🎭 Quijote Characters AI | Basado en Don Quijote de la Mancha de Miguel de Cervantes | RAG + Qwen 2.5 + LangGraph")