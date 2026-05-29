# ================================
# MÓDULO: Búsqueda RAG para Don Quijote
# ================================
# Propósito: Buscar chunks relevantes del Quijote para enriquecer respuestas
# ================================

import json
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

# ================================
# CONFIGURACIÓN
# ================================
EMBEDDING_MODEL = "nomic-ai/nomic-embed-text-v1.5"  # Mismo modelo que usaste para procesar
TOP_K_RESULTS = 5  # Número de chunks a retornar por búsqueda
SIMILARITY_THRESHOLD = 0.3  # Umbral mínimo de similitud coseno

# ================================
# CARGA DE DATOS PROCESADOS
# ================================

def load_quijote_data(json_path: str) -> Dict[str, Any]:
    """
    Carga el JSON procesado del Quijote en memoria.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# ================================
# BÚSQUEDA POR SIMILITUD COSENO
# ================================

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calcula similitud coseno entre dos vectores.
    """
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def search_chunks(query: str, chunks: List[Dict], embeddings: List[List[float]], 
                  query_embedding: List[float] = None, top_k: int = TOP_K_RESULTS,
                  threshold: float = SIMILARITY_THRESHOLD) -> List[Dict]:
    """
    Busca chunks relevantes para una query usando similitud coseno.
    
    Args:
        query: Texto de búsqueda del usuario
        chunks: Lista de chunks del Quijote
        embeddings: Lista de embeddings correspondientes
        query_embedding: Embedding pre-calculado de la query (opcional)
        top_k: Número máximo de resultados
        threshold: Similitud mínima para incluir un chunk
    
    Returns:
        Lista de chunks relevantes ordenados por similitud
    """
    # Si no se proporciona embedding de query, generarlo
    if query_embedding is None:
        model = SentenceTransformer(EMBEDDING_MODEL, trust_remote_code=True)
        query_embedding = model.encode(query).tolist()
    
    # Calcular similitudes
    results = []
    for i, chunk_emb in enumerate(embeddings):
        sim = cosine_similarity(query_embedding, chunk_emb)
        if sim >= threshold:
            results.append({
                "chunk": chunks[i],
                "similarity": sim
            })
    
    # Ordenar por similitud descendente y tomar top_k
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return [r["chunk"] for r in results[:top_k]]

def format_context_for_prompt(chunks: List[Dict], character: str = None) -> str:
    """
    Formatea chunks relevantes como contexto para el prompt del LLM.
    """
    if not chunks:
        return "No se encontró contexto relevante en el Quijote para esta consulta."
    
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        # Extraer metadata útil
        position = chunk.get("metadata", {}).get("position", "desconocida")
        context_parts.append(f"[Fragmento {i}] {chunk['text'].strip()}")
    
    return "\n\n".join(context_parts)

# ================================
# UTILIDADES PARA PERSONAJES
# ================================

def get_character_context_hint(character: str) -> str:
    """
    Devuelve pistas de búsqueda específicas por personaje.
    """
    hints = {
        "don_quijote": "caballero, armadura, Rocinante, molinos, aventura, ideal, locura",
        "sancho_panaza": "escudero, refrán, burro, isla, gobernador, práctico, hambre",
        "dulcinea": "musa, belleza, Toboso, amor, inspiración, idealización"
    }
    return hints.get(character.lower(), "")