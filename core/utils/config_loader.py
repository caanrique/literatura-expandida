# ================================
# MÓDULO: Cargador de configuraciones YAML
# ================================
# Propósito: Leer configs de libros desde archivos YAML
# ================================

import os
import yaml
from typing import Dict, Any

def load_book_config(book_id: str, config_dir: str = "configs/books") -> Dict[str, Any]:
    """
    Carga la configuración de un libro desde YAML.
    
    Args:
        book_id: ID del libro (ej: "don_quijote")
        config_dir: Directorio de configs (por defecto: "configs/books")
    
    Returns:
        Diccionario con la configuración completa
    
    Raises:
        FileNotFoundError: Si el YAML no existe
        yaml.YAMLError: Si el YAML tiene errores de sintaxis
    """
    config_path = os.path.join(config_dir, f"{book_id}.yaml")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config no encontrada: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Validaciones básicas
    if not config:
        raise ValueError(f"Config vacía: {config_path}")
    
    if 'book_id' not in config:
        raise ValueError(f"Config sin book_id: {config_path}")
    
    if config['book_id'] != book_id:
        raise ValueError(f"book_id mismatch: {config['book_id']} != {book_id}")
    
    return config

def get_config_value(config: Dict, *keys, default=None) -> Any:
    """
    Obtiene un valor anidado del config de forma segura.
    
    Ejemplo:
        get_config_value(config, 'preprocessing', 'chunk_size', default=512)
    """
    value = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value