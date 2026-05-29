# scripts/validate_yaml.py
import yaml
import json

book_id = "don_quijote"
yaml_path = f"configs/books/{book_id}.yaml"

try:
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    print("✅ YAML válido")
    print(f"\n📖 Libro: {data.get('book_id', 'N/A')}")
    print(f"🌍 Idioma: {data.get('metadata', {}).get('language', 'N/A')}")
    
    main_chars = data.get('character_extraction', {}).get('main_characters', [])
    print(f"\n🎭 Personajes principales ({len(main_chars)}):")
    for i, char in enumerate(main_chars, 1):
        print(f"   {i}. {char}")
    
    use_only = data.get('character_extraction', {}).get('use_main_characters_only', False)
    print(f"\n📋 Solo personajes principales: {use_only}")
    
except Exception as e:
    print(f"❌ Error: {e}")