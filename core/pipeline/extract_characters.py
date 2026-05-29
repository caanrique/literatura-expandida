# ================================
# MÓDULO: Extracción de Personajes de Obras Literarias
# ================================
# Propósito: Analizar chunks procesados y extraer perfiles de personajes
# ================================

import os
import sys
import json
import re
from typing import Dict, List, Any, Set
from collections import Counter, defaultdict
import spacy

# ================================
# IMPORTS DEL PROYECTO
# ================================
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.config_loader import load_book_config, get_config_value

# ================================
# MODELOS SPACY POR IDIOMA
# ================================
SPACY_MODELS = {
    'es': 'es_core_news_sm',
    'en': 'en_core_web_sm',
    'it': 'it_core_news_sm',
    'de': 'de_core_news_sm',
    'fr': 'fr_core_news_sm',
    'pt': 'pt_core_news_sm'
}

# ================================
# PATRONES DE NOMBRES POR IDIOMA
# ================================
NAME_PATTERNS = {
    'es': [
        r'Don\s+[A-Z][a-z]+',
        r'Doña\s+[A-Z][a-z]+',
        r'San\s+[A-Z][a-z]+',
        r'Santa\s+[A-Z][a-z]+',
        r'el\s+[a-z]+\s+de\s+[A-Z][a-z]+',
        r'[A-Z][a-z]+\s+[A-Z][a-z]+',
    ],
    'en': [
        r'Sir\s+[A-Z][a-z]+',
        r'Lord\s+[A-Z][a-z]+',
        r'Lady\s+[A-Z][a-z]+',
        r'King\s+[A-Z][a-z]+',
        r'Queen\s+[A-Z][a-z]+',
        r'Prince\s+[A-Z][a-z]+',
        r'Princess\s+[A-Z][a-z]+',
        r'[A-Z][a-z]+\s+[A-Z][a-z]+',
    ],
    'it': [
        r'Don\s+[A-Z][a-z]+',
        r'Donna\s+[A-Z][a-z]+',
        r'San\s+[A-Z][a-z]+',
        r'Santa\s+[A-Z][a-z]+',
        r'[A-Z][a-z]+\s+[A-Z][a-z]+',
    ],
    'de': [
        r'Herr\s+[A-Z][a-z]+',
        r'Frau\s+[A-Z][a-z]+',
        r'Prinz\s+[A-Z][a-z]+',
        r'Prinzessin\s+[A-Z][a-z]+',
        r'[A-Z][a-z]+\s+[A-Z][a-z]+',
    ],
    'fr': [
        r'Monsieur\s+[A-Z][a-z]+',
        r'Madame\s+[A-Z][a-z]+',
        r'Mademoiselle\s+[A-Z][a-z]+',
        r'Roi\s+[A-Z][a-z]+',
        r'Reine\s+[A-Z][a-z]+',
        r'[A-Z][a-z]+\s+[A-Z][a-z]+',
    ],
    'pt': [
        r'Dom\s+[A-Z][a-z]+',
        r'Dona\s+[A-Z][a-z]+',
        r'São\s+[A-Z][a-z]+',
        r'Santa\s+[A-Z][a-z]+',
        r'[A-Z][a-z]+\s+[A-Z][a-z]+',
    ],
}

# ================================
# PALABRAS A EXCLUIR (NO son nombres de personajes)
# ================================
EXCLUDED_WORDS = {
    'es': {'así', 'llegó', 'jamás', 'también', 'qué', 'quién', 'cuál', 'dónde', 
           'cuándo', 'cómo', 'página', 'señor', 'señora', 'aquel', 'aquél', 
           'esta', 'ese', 'eso', 'ello', 'cielo', 'dios', 'parte', 'modo', 
           'vez', 'tiempo', 'año', 'día', 'noche', 'mañana', 'tarde', 'fin', 
           'principio', 'medio', 'lado', 'mano', 'ojo', 'voz', 'nombre', 'cosa', 
           'hecho', 'caso', 'punto', 'lugar', 'sitio', 'manera', 'forma', 
           'razón', 'causa', 'efecto', 'resultado', 'triste', 'figura', 
           'hermandad', 'santa'},
    'en': {'the', 'and', 'what', 'who', 'which', 'when', 'where', 'how', 'why',
           'lord', 'lady', 'sir', 'page', 'heaven', 'god', 'time', 'day', 'night'},
    'it': {'così', 'arrivò', 'mai', 'anche', 'che', 'chi', 'quale', 'dove',
           'signore', 'signora', 'cielo', 'dio', 'tempo', 'giorno', 'notte'},
    'de': {'also', 'kam', 'nie', 'was', 'wer', 'welche', 'wo', 'herr', 'frau',
           'himmel', 'gott', 'zeit', 'tag', 'nacht'},
    'fr': {'ainsi', 'arriva', 'jamais', 'aussi', 'que', 'qui', 'quel', 'où',
           'monsieur', 'madame', 'ciel', 'dieu', 'temps', 'jour', 'nuit'},
    'pt': {'assim', 'chegou', 'nunca', 'também', 'que', 'quem', 'qual', 'onde',
           'senhor', 'senhora', 'céu', 'deus', 'tempo', 'dia', 'noite'},
}

# ================================
# FUNCIONES AUXILIARES
# ================================

def load_spacy_model(language: str):
    """Carga el modelo NER de Spacy para un idioma específico."""
    model_name = SPACY_MODELS.get(language, 'en_core_news_sm')
    try:
        return spacy.load(model_name)
    except OSError:
        print(f"⚠️ Modelo {model_name} no encontrado. Usando modelo en inglés como fallback.")
        try:
            return spacy.load('en_core_news_sm')
        except OSError:
            print("❌ Error: Ningún modelo Spacy disponible.")
            return None

def extract_names_with_patterns(text: str, language: str) -> List[str]:
    """Extrae nombres de personajes usando patrones regex específicos por idioma."""
    patterns = NAME_PATTERNS.get(language, NAME_PATTERNS['en'])
    names = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        names.extend(matches)
    return names

def extract_names_with_ner(text: str, nlp) -> List[str]:
    """Extrae nombres de personajes usando NER de Spacy."""
    if nlp is None:
        return []
    doc = nlp(text)
    names = []
    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'PER', 'Mensch']:
            names.append(ent.text)
    return names

def normalize_name(name: str) -> str:
    """Normaliza un nombre para usar como clave (minúsculas, sin espacios extra)."""
    return name.lower().strip().replace(' ', '_')

def is_valid_character_name(name: str, language: str) -> bool:
    """Verifica si un nombre es válido (no es una palabra común excluida)."""
    name_lower = name.lower().strip()
    excluded = EXCLUDED_WORDS.get(language, EXCLUDED_WORDS['es'])
    if name_lower in excluded:
        return False
    if len(name_lower) < 3:
        return False
    return True

def extract_traits_for_character(character_name: str, chunks: List[Dict], language: str, nlp) -> List[str]:
    """Extrae rasgos de personalidad para un personaje basándose en adjetivos cercanos."""
    traits = []
    trait_keywords = {
        'es': ['valiente', 'loco', 'idealista', 'sabio', 'fiel', 'astuto', 'noble', 'triste', 'generoso', 'honesto'],
        'en': ['brave', 'mad', 'idealistic', 'wise', 'loyal', 'cunning', 'noble', 'sad', 'generous', 'honest'],
        'it': ['coraggioso', 'pazzo', 'idealista', 'saggio', 'fedele', 'astuto', 'nobile', 'triste', 'generoso'],
        'de': ['mutig', 'verrückt', 'idealistisch', 'weise', 'treu', 'gerissen', 'edel', 'traurig'],
        'fr': ['courageux', 'fou', 'idéaliste', 'sage', 'fidèle', 'rusé', 'noble', 'triste'],
        'pt': ['corajoso', 'louco', 'idealista', 'sábio', 'fiel', 'astuto', 'nobre', 'triste'],
    }
    keywords = trait_keywords.get(language, trait_keywords['es'])
    char_name_variants = [
        character_name.replace('_', ' ').lower(),
        character_name.split('_')[0].lower(),
        character_name.split('_')[-1].lower(),
    ]
    for chunk in chunks[:100]:
        text = chunk.get('text', '').lower()
        if any(variant in text for variant in char_name_variants):
            for keyword in keywords:
                if keyword in text:
                    traits.append(keyword)
    trait_counts = Counter(traits)
    return [trait for trait, count in trait_counts.most_common(5)] if trait_counts else ['personaje_principal']

def extract_relationships(character_name: str, chunks: List[Dict], all_characters: Set[str], language: str) -> Dict[str, str]:
    """Extrae relaciones entre personajes basándose en co-ocurrencia en chunks."""
    relationships = {}
    return relationships

def extract_key_quotes(character_name: str, chunks: List[Dict], top_k: int = 5) -> List[Dict]:
    """Extrae las citas más relevantes para un personaje."""
    character_quotes = []
    for i, chunk in enumerate(chunks):
        text = chunk.get('text', '')
        if character_name.replace('_', ' ') in text.lower():
            character_quotes.append({
                'text': text[:200],
                'chunk_id': chunk.get('id', i),
                'position': chunk.get('metadata', {}).get('position', 'N/A')
            })
    return character_quotes[:top_k]

# ================================
# FUNCIÓN PRINCIPAL DE EXTRACCIÓN
# ================================

def extract_characters(book_id: str, config: Dict = None):
    """
    Pipeline completo de extracción de personajes.
    """
    print("=" * 60)
    print("🎭 INICIANDO EXTRACCIÓN DE PERSONAJES")
    print("=" * 60)
    
    # Cargar config si no se proporciona
    if config is None:
        config = load_book_config(book_id)
    
    # Extraer configuración
    language = get_config_value(config, 'metadata', 'language', default='es')
    processed_file = get_config_value(config, 'source', 'output')
    min_mentions = get_config_value(config, 'character_extraction', 'min_mentions', default=3)
    
    # Construir ruta al archivo procesado
    if not processed_file:
        processed_file = f"data/processed/{book_id}_processed.json"
    
    print(f"📖 Libro: {book_id}")
    print(f"🌍 Idioma: {language}")
    print(f"📄 Archivo procesado: {processed_file}")
    
    # Validar que el archivo existe
    if not os.path.exists(processed_file):
        print(f"❌ Error: Archivo no encontrado: {processed_file}")
        return None
    
    # Cargar chunks procesados
    print("📚 Cargando chunks procesados...")
    with open(processed_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chunks = data.get('chunks', [])
    print(f"✅ {len(chunks)} chunks cargados")
    
    # Cargar modelo NER
    print(f"🔧 Cargando modelo NER para {language}...")
    nlp = load_spacy_model(language)
    
    # ================================
    # EXTRACCIÓN DE NOMBRES
    # ================================
    print("🔍 Extrayendo nombres de personajes...")
    
    all_names = []
    name_sources = defaultdict(lambda: {'patterns': 0, 'ner': 0, 'chunks': []})
    
    for i, chunk in enumerate(chunks):
        text = chunk.get('text', '')
        
        # Extraer con patrones
        pattern_names = extract_names_with_patterns(text, language)
        all_names.extend(pattern_names)
        for name in pattern_names:
            norm_name = normalize_name(name)
            name_sources[norm_name]['patterns'] += 1
            name_sources[norm_name]['chunks'].append(i)
        
        # Extraer con NER
        ner_names = extract_names_with_ner(text, nlp)
        all_names.extend(ner_names)
        for name in ner_names:
            norm_name = normalize_name(name)
            name_sources[norm_name]['ner'] += 1
    
    # Filtrar nombres válidos
    valid_names = [name for name in all_names if is_valid_character_name(name, language)]
    
    # Contar frecuencias
    name_counts = Counter(valid_names)
    print(f"✅ {len(name_counts)} nombres únicos encontrados")
    
    # ================================
    # FILTRAR POR FRECUENCIA
    # ================================
    print(f"📊 Filtrando personajes con >= {min_mentions} menciones...")
    
    filtered_characters = {
        name: count 
        for name, count in name_counts.items() 
        if count >= min_mentions
    }
    
    print(f"✅ {len(filtered_characters)} personajes identificados")
    
    # ================================
    # CONSTRUIR PERFILES
    # ================================
    print("📝 Construyendo perfiles de personajes...")
    
    character_profiles = {}
    all_character_keys = set(filtered_characters.keys())
    
    for char_key, mention_count in filtered_characters.items():
        canonical_name = char_key.replace('_', ' ').title()
        traits = extract_traits_for_character(char_key, chunks, language, nlp)
        relationships = extract_relationships(char_key, chunks, all_character_keys, language)
        key_quotes = extract_key_quotes(char_key, chunks, top_k=5)
        
        character_profiles[char_key] = {
            'canonical_name': canonical_name,
            'aliases': [canonical_name],
            'traits': traits if traits else ['personaje_principal'],
            'relationships': relationships,
            'key_quotes': key_quotes,
            'mention_count': mention_count,
            'first_appearance_chunk': min(name_sources[char_key]['chunks']) if name_sources[char_key]['chunks'] else 0,
            'metadata': {
                'language': language,
                'book_id': book_id,
                'extraction_method': 'spacy_ner+patterns'
            }
        }
        
        print(f"   - {canonical_name}: {mention_count} menciones, {len(traits)} rasgos, {len(relationships)} relaciones")
    
       # ================================
    # FILTRAR POR PERSONAJES PRINCIPALES (si está configurado)
    # ================================
    use_main = get_config_value(config, 'character_extraction', 'use_main_characters_only', default=False)
    main_list = get_config_value(config, 'character_extraction', 'main_characters', default=[])
    
    print(f"\n🔍 DEBUG FILTRO:")
    print(f"   use_main = {use_main}")
    print(f"   main_list = {main_list}")
    print(f"   character_profiles antes = {len(character_profiles)}")
    
    if use_main and main_list:
        # Diccionario para agrupar variantes del mismo personaje
        grouped_profiles = {}
        
        for char_key, profile in character_profiles.items():
            canonical = profile['canonical_name'].lower()
            
            # Encontrar el personaje principal que coincide
            for main_name in main_list:
                main_lower = main_name.lower()
                
                # Coincidencia: el nombre del perfil está contenido en el nombre principal O viceversa
                if main_lower in canonical or canonical in main_lower:
                    # Usar el nombre más largo como clave (es más completo)
                    best_key = max(char_key, main_lower.replace(' ', '_'), key=len)
                    
                    if best_key not in grouped_profiles:
                        grouped_profiles[best_key] = profile
                        print(f"   ✅ {profile['canonical_name']} incluido (coincide con '{main_name}')")
                    else:
                        # Si ya existe, mantener el que tiene más menciones
                        if profile['mention_count'] > grouped_profiles[best_key]['mention_count']:
                            print(f"   🔄 {profile['canonical_name']} reemplaza a {grouped_profiles[best_key]['canonical_name']} (más menciones)")
                            grouped_profiles[best_key] = profile
                        else:
                            print(f"   ⏭️ {profile['canonical_name']} omitido (ya existe variante más completa)")
                    break
        
        character_profiles = grouped_profiles
        print(f"\n📋 Filtrado: {len(character_profiles) + sum(1 for p in character_profiles.values())} → {len(character_profiles)} personajes principales (variantes unificadas)")
    else:
        print(f"\n⚠️ FILTRO NO APLICADO (use_main={use_main}, main_list={len(main_list) if main_list else 0} elementos)")
    
    # ================================
    # GUARDAR RESULTADO
    # ================================
    output_file = f"data/processed/{book_id}_characters.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    output_data = {
        'book_id': book_id,
        'language': language,
        'total_characters': len(character_profiles),
        'extraction_info': {
            'min_mentions': min_mentions,
            'spacy_model': SPACY_MODELS.get(language, 'en_core_news_sm'),
            'extracted_at': __import__('datetime').datetime.now().isoformat()
        },
        'characters': character_profiles
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print("=" * 60)
    print("✅ EXTRACCIÓN DE PERSONAJES COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print(f"📊 Resumen:")
    print(f"   - Libro: {book_id}")
    print(f"   - Personajes: {len(character_profiles)}")
    print(f"   - Output: {output_file}")
    print("=" * 60)
    
    return character_profiles


# ================================
# PUNTO DE ENTRADA (CLI)
# ================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extraer personajes de obra literaria")
    parser.add_argument("--book", "-b", required=True, help="ID del libro (ej: don_quijote)")
    
    args = parser.parse_args()
    
    profiles = extract_characters(args.book)
    
    if profiles:
        print(f"\n🎉 ¡{len(profiles)} personajes extraídos para {args.book}!")
        sys.exit(0)
    else:
        print("\n❌ Error en la extracción")
        sys.exit(1)