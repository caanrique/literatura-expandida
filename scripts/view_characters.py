# scripts/view_characters.py
import json

book_id = "hamlet"
file_path = f"data/processed/{book_id}_characters.json"

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"\n📚 {data['book_id'].upper()} - {data['total_characters']} personajes\n")
print(f"{'#':<4} {'Nombre':<30} {'Menciones':<10} {'Rasgos':<10} {'Relaciones':<10}")
print("-" * 70)

chars = data['characters'].items()

# Ordenar: si hay mention_count, usarlo; si no, ordenar por nombre
try:
    chars = sorted(chars, key=lambda x: x[1].get('mention_count', 0), reverse=True)
except:
    chars = sorted(chars, key=lambda x: x[1].get('canonical_name', ''))

for i, (k, v) in enumerate(chars, 1):
    # Manejar ambos casos: automático (con mention_count) o manual (sin mention_count)
    mentions = v.get('mention_count', 'N/A')
    if mentions == 'N/A':
        mentions = 'manual'
    
    traits = len(v.get('traits', []))
    relationships = len(v.get('relationships', {}))
    
    print(f"{i:<4} {v.get('canonical_name', 'N/A'):<30} {str(mentions):<10} {traits:<10} {relationships:<10}")