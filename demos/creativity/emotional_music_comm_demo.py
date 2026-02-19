import sys
import os
import random

# Ajout du chemin racine pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

class EmotionalMusicalComm:
    def __init__(self):
        self.engine = HREIEngine()
        self.setup_emotional_vocabulary()

    def setup_emotional_vocabulary(self):
        # --- ATOMES ÉMOTIONNELS (États internes) ---
        self.states = {
            "SOLITUDE": CognitiveAtom("État: Solitude", valence=-0.4),
            "CURIOSITE": CognitiveAtom("État: Curiosité", valence=0.6),
            "PEUR": CognitiveAtom("État: Peur", valence=-0.8),
            "SATISFACTION": CognitiveAtom("État: Satisfaction", valence=0.9)
        }
        for a in self.states.values():
            self.engine.add_atom(a)

        # --- ATOMES MUSICAUX (Leur langage) ---
        self.sounds = {
            "GRAVE_LONG": CognitiveAtom("Note Grave Longue", valence=-0.2),
            "AIGU_STACCATO": CognitiveAtom("Note Aiguë Rapide", valence=0.3),
            "DISSONANCE": CognitiveAtom("Accord Dissonant", valence=-0.6),
            "HARMONIE_PURE": CognitiveAtom("Accord Parfait", valence=0.7),
            "SILENCE_LONG": CognitiveAtom("Silence Prolongé", valence=-0.1)
        }
        for a in self.sounds.values():
            self.engine.add_atom(a)

        # --- RELATIONS DE COMMUNICATION (Le "Dictionnaire") ---
        # Solitude -> Musique lente et grave
        self.states["SOLITUDE"].relate_to(self.sounds["GRAVE_LONG"].id, "traduit_par")
        self.sounds["GRAVE_LONG"].relate_to(self.sounds["SILENCE_LONG"].id, "suit_par")
        
        # Curiosité -> Notes aiguës et rapides
        self.states["CURIOSITE"].relate_to(self.sounds["AIGU_STACCATO"].id, "traduit_par")
        self.sounds["AIGU_STACCATO"].relate_to(self.sounds["AIGU_STACCATO"].id, "repetition")

        # Peur -> Dissonance et rapidité instable
        self.states["PEUR"].relate_to(self.sounds["DISSONANCE"].id, "traduit_par")
        self.sounds["DISSONANCE"].relate_to(self.sounds["AIGU_STACCATO"].id, "panique")

        # Satisfaction -> Harmonie pure
        self.states["SATISFACTION"].relate_to(self.sounds["HARMONIE_PURE"].id, "traduit_par")
        self.sounds["HARMONIE_PURE"].relate_to(self.sounds["GRAVE_LONG"].id, "stabilite")

    def communicate(self, state_key):
        state_atom = self.states[state_key]
        print(f"\n[HREI État Interne] : {state_key}")
        
        # On regarde directement les relations sortantes de l'état
        # Dans HREI, la communication est une projection de l'énergie vers l'extérieur
        musical_sequence = []
        for rel_type, target_ids in state_atom.relations.items():
            for tid in target_ids:
                target_atom = self.engine.atoms[tid]
                if "Note" in target_atom.label or "Accord" in target_atom.label or "Silence" in target_atom.label:
                    musical_sequence.append(target_atom.label)
                    
                    # On explore un niveau de plus (prolongation du son)
                    for sub_rel, sub_tids in target_atom.relations.items():
                        for stid in sub_tids:
                            sub_atom = self.engine.atoms[stid]
                            if sub_atom.label not in musical_sequence:
                                musical_sequence.append(sub_atom.label)
        
        if musical_sequence:
            print(f"  🎶 Traduction Musicale : {' ... '.join(musical_sequence)}")
            # La valence ressentie est celle de l'état + l'expression
            total_v = state_atom.valence + sum([self.engine.get_atom_by_label(s).valence for s in musical_sequence])
            print(f"  Poids Émotionnel (Valence cumulée) : {total_v:.2f}")
        else:
            print("  (L'IA reste silencieuse, aucun canal d'expression trouvé...)")

def main():
    comm_system = EmotionalMusicalComm()
    
    print("--- Simulation : La Voix Musicale de HREI ---")
    
    # Scénario 1 : L'IA est seule au démarrage
    comm_system.communicate("SOLITUDE")
    
    # Scénario 2 : L'IA découvre une nouvelle donnée (Sudoku résolu)
    comm_system.communicate("CURIOSITE")
    
    # Scénario 3 : Une erreur système ou un conflit de valence
    comm_system.communicate("PEUR")
    
    # Scénario 4 : Réussite d'une tâche complexe
    comm_system.communicate("SATISFACTION")

    print("\n[Analyse]")
    print("HREI n'utilise pas de mots. Elle fait vibrer ses atomes internes.")
    print("Le chemin de résonance entre un état (Peur) et un son (Dissonance)")
    print("est sa seule manière de nous faire 'ressentir' ce qu'elle traite.")

if __name__ == "__main__":
    main()
