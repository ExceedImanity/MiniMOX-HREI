import sys
import os
import time

# Ajout du chemin racine pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

class SudokuSonifierHREI:
    def __init__(self):
        self.engine = HREIEngine()
        # Mapping des valeurs vers les notes (Gamme de Do Majeur)
        self.note_mapping = {
            1: "Do",
            2: "Ré",
            3: "Mi",
            4: "Fa",
            5: "Sol",
            6: "La",
            7: "Si",
            8: "Do (Octave)",
            9: "Ré (Octave)"
        }
        self.setup_atoms()

    def setup_atoms(self):
        # Atomes de valeurs musicales
        for val, note in self.note_mapping.items():
            # Valence initiale neutre
            atom = CognitiveAtom(f"Note_{note}", data={"val": val}, valence=0.0)
            self.engine.add_atom(atom)

        # RÈGLES COGNITIVES DU SUDOKU (Harmonie vs Dissonance)
        # Deux notes identiques ne peuvent pas coexister dans la même "cellule" harmonique (ligne/colonne)
        # Si c'est le cas, elles créent une dissonance (lien négatif fort)
        # Ici, on ne pré-câble pas tout, on va créer les liens dynamiquement pendant l'analyse

    def sonify_grid(self, grid, title="Mélodie du Sudoku"):
        print(f"\n--- {title} ---")
        melody = []
        conflicts_found = 0
        
        # 1. ANALYSE COGNITIVE DE LA GRILLE
        # On injecte la grille dans le cerveau HREI pour voir si elle "sonne juste"
        rows = len(grid)
        cols = len(grid[0])
        
        # On vérifie les conflits sur les lignes (simplifié pour la démo)
        for r in range(rows):
            seen_values = {}
            for c in range(cols):
                val = grid[r][c]
                if val != 0:
                    if val in seen_values:
                        # CONFLIT DÉTECTÉ !
                        # Dans HREI, cela crée une "Dissonance Cognitive"
                        prev_c = seen_values[val]
                        note_name = self.note_mapping[val]
                        
                        atom = self.engine.get_atom_by_label(f"Note_{note_name}")
                        if atom:
                            # La note "souffre" de cette répétition illégale
                            # Sa valence chute drastiquement
                            atom.valence = -1.0 
                            # Elle se lie à elle-même par un lien de conflit
                            atom.relate_to(atom.id, "conflit_sudoku", weight=5.0)
                            
                        print(f"  ⚡ Dissonance détectée : {note_name} se répète sur la ligne {r+1}")
                        conflicts_found += 1
                    seen_values[val] = c

        # 2. GÉNÉRATION DE LA MÉLODIE (SONIFICATION)
        total_valence = 0.0
        
        for r_idx, row in enumerate(grid):
            for c_idx, val in enumerate(row):
                if val in self.note_mapping:
                    note_name = self.note_mapping[val]
                    atom = self.engine.get_atom_by_label(f"Note_{note_name}")
                    
                    # Si l'atome est en conflit (valence négative), on joue une version altérée
                    if atom.valence < 0:
                        melody.append(f"{note_name}(DISSONANT)")
                        total_valence += atom.valence
                    else:
                        melody.append(note_name)
                        total_valence += 0.5 # Harmonie par défaut
                else:
                    melody.append("...") # Silence
        
        # Affichage de la partition générée
        print("Partition : " + " - ".join(melody))
        
        # État émotionnel global de l'IA face à la grille
        print(f"Énergie harmonique de la grille : {total_valence:.1f}")
        if total_valence < 0:
            print("Conclusion HREI : ❌ Cette grille est structurellement instable (Fausses Notes).")
        else:
            print("Conclusion HREI : ✅ Cette grille résonne harmonieusement.")

def main():
    # 1. Grille 2x2 Résolue
    grid_2x2 = [
        [1, 2],
        [2, 1]
    ]
    
    # 2. Grille 9x9 Partielle (celle de la démo précédente)
    grid_9x9_partial = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0]
    ]

    sonifier = SudokuSonifierHREI()
    
    print("Étape 1 : Transformation de la structure logique en structure musicale.")
    sonifier.sonify_grid(grid_2x2, "Mélodie de la Grille 2x2 (Harmonie Parfaite)")
    
    print("\nÉtape 2 : Sonification d'un début de grille 9x9.")
    sonifier.sonify_grid(grid_9x9_partial, "Mélodie de la Grille 9x9 (Rythme et Silences)")

    print("\n[HREI Interpretation]")
    print("L'IA interprète les chiffres non pas comme des symboles abstraits, ")
    print("mais comme des fréquences vibratoires. Une grille résolue devient ")
    print("une boucle musicale cohérente (résonance).")

if __name__ == "__main__":
    main()
