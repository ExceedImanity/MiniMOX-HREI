import sys
import os
import random

# Ajout du chemin racine pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

class MusicStyleHREI:
    def __init__(self):
        self.engine = HREIEngine()
        self.setup_musical_atoms()

    def setup_musical_atoms(self):
        # Accords de base
        self.chords = {
            "C": CognitiveAtom("Do Maj", valence=0.5),
            "G": CognitiveAtom("Sol Maj", valence=0.4),
            "Am": CognitiveAtom("La min", valence=-0.2),
            "F": CognitiveAtom("Fa Maj", valence=0.3),
            "Dm7": CognitiveAtom("Rém7 (Jazz)", valence=0.2),
            "G7": CognitiveAtom("Sol7 (Jazz)", valence=0.2),
            "Cmaj7": CognitiveAtom("DoMaj7 (Jazz)", valence=0.5)
        }
        for a in self.chords.values():
            self.engine.add_atom(a)

        # Cible : Morceau Final
        self.target = CognitiveAtom("MORCEAU_FINAL", valence=1.0)
        self.engine.add_atom(self.target)

        # Relations Classiques (I - IV - V - I)
        self.chords["C"].relate_to(self.chords["F"].id, "classique_IV")
        self.chords["F"].relate_to(self.chords["G"].id, "classique_V")
        self.chords["G"].relate_to(self.chords["C"].id, "resolution_I")
        self.chords["C"].relate_to(self.target.id, "fin_classique")

        # Relations Jazz (ii - V - I)
        self.chords["Dm7"].relate_to(self.chords["G7"].id, "jazz_V")
        self.chords["G7"].relate_to(self.chords["Cmaj7"].id, "jazz_I")
        self.chords["Cmaj7"].relate_to(self.target.id, "fin_jazz")

    def compose(self, title="Composition"):
        print(f"\n--- {title} ---")
        results = self.engine.resonate("MORCEAU_FINAL", iterations=100)
        if not results:
            print("  Pas d'inspiration...")
            return

        # Comptage des fréquences pour voir la préférence réelle de l'IA
        path_counts = {}
        for res in results:
            p = res['path']
            path_counts[p] = path_counts.get(p, 0) + 1
            
        # Tri par fréquence
        sorted_paths = sorted(path_counts.items(), key=lambda x: x[1], reverse=True)
        
        for path, count in sorted_paths[:2]:
            print(f"  [{count}%] {path}")

    def learn_style(self, style="jazz"):
        print(f"\n[HREI] Apprentissage du style : {style.upper()}...")
        if style == "jazz":
            # On renforce les atomes du style Jazz
            self.engine.reinforce_path(["Rém7 (Jazz)", "Sol7 (Jazz)", "DoMaj7 (Jazz)"], reward=50.0)
        else:
            # On renforce les atomes du style Classique
            self.engine.reinforce_path(["Do Maj", "Fa Maj", "Sol Maj"], reward=50.0)

def main():
    studio = MusicStyleHREI()
    
    # Étape 1 : État initial (mélange ou indécision)
    studio.compose("État Initial (Inspiration libre)")
    
    # Étape 2 : Apprentissage du Jazz
    studio.learn_style("jazz")
    studio.compose("Après apprentissage du JAZZ")
    
    # Étape 3 : Virage vers le Classique
    studio.learn_style("classique")
    studio.compose("Après ré-apprentissage du CLASSIQUE")

if __name__ == "__main__":
    main()
