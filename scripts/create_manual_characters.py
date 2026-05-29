# scripts/create_manual_characters.py
import json
import os

# ================================
# PERSONAJES PRINCIPALES PARA CADA OBRA
# ================================

MANUAL_CHARACTERS = {
    'don_quijote': {
        'es': {
            'don_quijote': {
                'canonical_name': 'Don Quijote de la Mancha',
                'aliases': ['el caballero de la triste figura', 'Alonso Quijano'],
                'traits': ['idealista', 'valiente', 'loco', 'noble', 'soñador'],
                'relationships': {'sancho_panaza': 'amo-escudero', 'dulcinea': 'amor_idealizado'},
                'description': 'Hidalgo que enloquece leyendo libros de caballerías'
            },
            'sancho_panaza': {
                'canonical_name': 'Sancho Panza',
                'aliases': ['el escudero', 'mi fiel Sancho'],
                'traits': ['práctico', 'leal', 'refranero', 'hambriento', 'sencillo'],
                'relationships': {'don_quijote': 'escudero-amo'},
                'description': 'Campesino que acompaña a Don Quijote como escudero'
            },
            'dulcinea': {
                'canonical_name': 'Dulcinea del Toboso',
                'aliases': ['Aldonza Lorenzo', 'mi señora'],
                'traits': ['bella', 'idealizada', 'distante', 'inspiradora'],
                'relationships': {'don_quijote': 'amor_platónico'},
                'description': 'Campesina idealizada por Don Quijote como su dama'
            },
            'rocinante': {
                'canonical_name': 'Rocinante',
                'aliases': ['el caballo', 'mi fiel rocín'],
                'traits': ['flaco', 'leal', 'cansado', 'noble'],
                'relationships': {'don_quijote': 'caballo-jinete'},
                'description': 'El viejo caballo de Don Quijote'
            },
            'el_cura': {
                'canonical_name': 'El Cura (Pero Pérez)',
                'aliases': ['el licenciado', 'mi amigo el cura'],
                'traits': ['sabio', 'prudente', 'amigo', 'conciliador'],
                'relationships': {'don_quijote': 'amigo', 'barbero': 'aliado'},
                'description': 'Cura del pueblo que intenta curar la locura de Don Quijote'
            }
        }
    },
    'divina_comedia': {
        'it': {
            'dante': {
                'canonical_name': 'Dante Alighieri',
                'aliases': ['il poeta', 'il pellegrino'],
                'traits': ['curioso', 'temeroso', 'devoto', 'poético'],
                'relationships': {'virgilio': 'guía', 'beatrice': 'amor_divino'},
                'description': 'El poeta que viaja por Infierno, Purgatorio y Paraíso'
            },
            'virgilio': {
                'canonical_name': 'Virgilio',
                'aliases': ['la guida', 'il maestro'],
                'traits': ['sabio', 'protector', 'racional', 'experimentado'],
                'relationships': {'dante': 'protegido'},
                'description': 'Poeta romano que guía a Dante por Infierno y Purgatorio'
            },
            'beatrice': {
                'canonical_name': 'Beatrice Portinari',
                'aliases': ['la donna beata', 'mia donna'],
                'traits': ['pura', 'divina', 'amorosa', 'celestial'],
                'relationships': {'dante': 'amor_espiritual'},
                'description': 'El amor de juventud de Dante, ahora guía celestial'
            },
            'lucifero': {
                'canonical_name': 'Lucifero',
                'aliases': ['il diavolo', 'Satana'],
                'traits': ['malvado', 'poderoso', 'caído', 'eterno'],
                'relationships': {'dante': 'antagonista'},
                'description': 'El demonio en el centro del Infierno'
            },
            'san_pietro': {
                'canonical_name': 'San Pedro',
                'aliases': ['il santo', 'il pescatore'],
                'traits': ['santo', 'justiciero', 'guardián', 'apostólico'],
                'relationships': {'dante': 'examinador'},
                'description': 'Apóstol que guarda las puertas del Paraíso'
            }
        }
    },
    'hamlet': {
        'en': {
            'hamlet': {
                'canonical_name': 'Prince Hamlet',
                'aliases': ['the Prince of Denmark', 'my lord'],
                'traits': ['melancholic', 'philosophical', 'indecisive', 'vengeful', 'intelligent'],
                'relationships': {'claudius': 'uncle-enemy', 'gertrude': 'mother', 'ophelia': 'love'},
                'description': 'Prince of Denmark, seeking revenge for his father\'s death'
            },
            'ophelia': {
                'canonical_name': 'Ophelia',
                'aliases': ['fair Ophelia', 'my lady'],
                'traits': ['innocent', 'gentle', 'tragic', 'loyal', 'fragile'],
                'relationships': {'hamlet': 'love', 'polonius': 'father'},
                'description': 'Young noblewoman, Hamlet\'s love interest'
            },
            'claudius': {
                'canonical_name': 'King Claudius',
                'aliases': ['the King', 'my uncle'],
                'traits': ['cunning', 'guilty', 'manipulative', 'ambitious'],
                'relationships': {'hamlet': 'nephew-enemy', 'gertrude': 'wife'},
                'description': 'Usurper king, murdered Hamlet\'s father'
            },
            'gertrude': {
                'canonical_name': 'Queen Gertrude',
                'aliases': ['the Queen', 'my mother'],
                'traits': ['loving', 'conflicted', 'weak', 'maternal'],
                'relationships': {'hamlet': 'son', 'claudius': 'husband'},
                'description': 'Hamlet\'s mother, married to Claudius'
            },
            'ghost': {
                'canonical_name': 'The Ghost (King Hamlet)',
                'aliases': ['the spirit', 'my father\'s ghost'],
                'traits': ['vengeful', 'tragic', 'mysterious', 'authoritative'],
                'relationships': {'hamlet': 'son'},
                'description': 'Spirit of Hamlet\'s murdered father'
            }
        }
    },
    'fausto': {
        'de': {
            'faust': {
                'canonical_name': 'Dr. Heinrich Faust',
                'aliases': ['der Doktor', 'der Gelehrte'],
                'traits': ['wissbegierig', 'unzufrieden', 'ambitioniert', 'verzweifelt'],
                'relationships': {'mephisto': 'pakt-partner', 'gretchen': 'liebe'},
                'description': 'Gelehrter der einen Pakt mit dem Teufel schließt'
            },
            'mephisto': {
                'canonical_name': 'Mephistopheles',
                'aliases': ['der Teufel', 'der Böse'],
                'traits': ['listig', 'zynisch', 'versucher', 'intelligent'],
                'relationships': {'faust': 'pakt-partner'},
                'description': 'Der Teufel der Fausts Seele begehrt'
            },
            'gretchen': {
                'canonical_name': 'Gretchen (Margarete)',
                'aliases': ['das Mädchen', 'die Unschuld'],
                'traits': ['unschuldig', 'fromm', 'liebend', 'tragisch'],
                'relationships': {'faust': 'liebe'},
                'description': 'Junges Mädchen das Faust liebt'
            },
            'wagner': {
                'canonical_name': 'Wagner',
                'aliases': ['der Famulus', 'der Schüler'],
                'traits': ['fleißig', 'pedantisch', 'loyal', 'begrenzt'],
                'relationships': {'faust': 'meister'},
                'description': 'Fausts Assistent und Schüler'
            },
            'gott': {
                'canonical_name': 'Der Herr (Gott)',
                'aliases': ['der Allmächtige'],
                'traits': ['allwissend', 'gnädig', 'gerecht', 'erhaben'],
                'relationships': {'mephisto': 'gegenspieler'},
                'description': 'Gott der mit Mephisto eine Wette eingeht'
            }
        }
    },
    'los_miserables': {
        'fr': {
            'jean_valjean': {
                'canonical_name': 'Jean Valjean',
                'aliases': ['Monsieur Madeleine', 'le forçat'],
                'traits': ['rédempteur', 'fort', 'généreux', 'persécuté', 'noble'],
                'relationships': {'javert': 'ennemi', 'cosette': 'fille_adoptive', 'fantine': 'protégée'},
                'description': 'Ancien forçat en quête de rédemption'
            },
            'javert': {
                'canonical_name': 'Inspecteur Javert',
                'aliases': ['l\'inspecteur', 'la loi'],
                'traits': ['rigide', 'obsessionnel', 'justicier', 'inflexible'],
                'relationships': {'jean_valjean': 'proie'},
                'description': 'Inspecteur obsédé par l\'arrestation de Valjean'
            },
            'cosette': {
                'canonical_name': 'Cosette',
                'aliases': ['l\'alouette', 'la fille'],
                'traits': ['innocente', 'aimante', 'douce', 'reconnaissante'],
                'relationships': {'jean_valjean': 'père_adoptif', 'marius': 'amour'},
                'description': 'Fille adoptive de Valjean'
            },
            'fantine': {
                'canonical_name': 'Fantine',
                'aliases': ['la mère', 'l\'ouvrière'],
                'traits': ['sacrificielle', 'aimante', 'tragique', 'désespérée'],
                'relationships': {'cosette': 'fille', 'jean_valjean': 'bienfaiteur'},
                'description': 'Mère de Cosette, morte tragiquement'
            },
            'marius': {
                'canonical_name': 'Marius Pontmercy',
                'aliases': ['le jeune homme', 'l\'étudiant'],
                'traits': ['idéaliste', 'amoureux', 'révolutionnaire', 'courageux'],
                'relationships': {'cosette': 'amour', 'jean_valjean': 'beau-père'},
                'description': 'Jeune révolutionnaire amoureux de Cosette'
            }
        }
    },
    'lusiadas': {
        'pt': {
            'vasco_da_gama': {
                'canonical_name': 'Vasco da Gama',
                'aliases': ['o capitão', 'o navegador'],
                'traits': ['corajoso', 'determinado', 'patriota', 'explorador'],
                'relationships': {'adamastor': 'inimigo', 'rei_manuel': 'rei'},
                'description': 'Navegador português que descobriu o caminho para a Índia'
            },
            'adamastor': {
                'canonical_name': 'Adamastor',
                'aliases': ['o gigante', 'o monstro'],
                'traits': ['ameaçador', 'poderoso', 'amaldiçoado', 'selvagem'],
                'relationships': {'vasco_da_gama': 'obstáculo'},
                'description': 'Gigante mitológico que guarda o Cabo das Tormentas'
            },
            'ines_de_castro': {
                'canonical_name': 'Inês de Castro',
                'aliases': ['a dama', 'a morta'],
                'traits': ['trágica', 'amante', 'inocente', 'vítima'],
                'relationships': {'pedro': 'amor'},
                'description': 'Nobre espanhola, amor trágico de D. Pedro'
            },
            'rei_manuel': {
                'canonical_name': 'Rei D. Manuel I',
                'aliases': ['o rei', 'D. Manuel'],
                'traits': ['poderoso', 'visionário', 'autoritário', 'glorioso'],
                'relationships': {'vasco_da_gama': 'súdito'},
                'description': 'Rei de Portugal que enviou Vasco da Gama à Índia'
            },
            'tethys': {
                'canonical_name': 'Tethys',
                'aliases': ['a ninfa', 'a deusa'],
                'traits': ['divina', 'sedutora', 'celestial', 'generosa'],
                'relationships': {'vasco_da_gama': 'protetora'},
                'description': 'Ninfa marinha que protege os navegadores'
            }
        }
    }
}

# ================================
# CREAR ARCHIVOS JSON
# ================================

for book_id, languages in MANUAL_CHARACTERS.items():
    for lang, characters in languages.items():
        output_data = {
            'book_id': book_id,
            'language': lang,
            'total_characters': len(characters),
            'extraction_method': 'manual_curation',
            'extraction_info': {
                'curated_by': 'Camilo',
                'curated_at': __import__('datetime').datetime.now().isoformat(),
                'method': 'Manual character selection with defined traits and relationships'
            },
            'characters': characters
        }
        
        output_file = f"data/processed/{book_id}_characters.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {book_id}: {len(characters)} personajes creados → {output_file}")

print("\n🎉 ¡Todas las 6 obras con personajes manuales listas!")