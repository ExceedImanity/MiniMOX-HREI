import sys
import os
import random

# Ajout du chemin racine pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

class MusicHREI:
    def __init__(self):
        # On désactive le fichier de mémoire pour la démo (plus propre)
        self.engine = HREIEngine(memory_file=None) 
        self.setup_musical_knowledge()

    def setup_musical_knowledge(self):
        # --- ATOMES DE NOTES/ACCORDS ---
        # Accords Majeurs (Valence positive = Joie, Stabilité)
        c_maj = CognitiveAtom("Do Maj", valence=0.6)
        g_maj = CognitiveAtom("Sol Maj", valence=0.5)
        f_maj = CognitiveAtom("Fa Maj", valence=0.4)
        
        # Accords Mineurs (Valence négative/basse = Tristesse, Tension)
        a_min = CognitiveAtom("La min", valence=-0.3)
        e_min = CognitiveAtom("Mi min", valence=-0.2)
        d_min = CognitiveAtom("Ré min", valence=-0.1)

        # Émotions Cibles (Objectifs)
        joie = CognitiveAtom("JOIE", valence=1.0)
        melancolie = CognitiveAtom("MÉLANCOLIE", valence=1.0)

        for a in [c_maj, g_maj, f_maj, a_min, e_min, d_min, joie, melancolie]:
            self.engine.add_atom(a)

        # --- RELATIONS HARMONIQUES ---
        # Vers la JOIE
        c_maj.relate_to(g_maj.id, "quinte_stable")
        g_maj.relate_to(c_maj.id, "resolution")
        f_maj.relate_to(c_maj.id, "cadence_plagale")
        c_maj.relate_to(joie.id, "evoque")
        g_maj.relate_to(joie.id, "evoque")

        # Vers la MÉLANCOLIE
        a_min.relate_to(e_min.id, "tristesse_profonde")
        e_min.relate_to(d_min.id, "descente_chromatique")
        a_min.relate_to(melancolie.id, "evoque")
        d_min.relate_to(melancolie.id, "evoque")

        # Liens mixtes (Innovation créative)
        c_maj.relate_to(a_min.id, "relatif_mineur")
        a_min.relate_to(f_maj.id, "espoir_lointain")

    def compose(self, target_emotion, length=4):
        print(f"\n[HREI] Composition d'une séquence pour l'émotion : {target_emotion}")
        
        # resonate() renvoie une liste de strings (chemins)
        results = self.engine.resonate(target_emotion, iterations=20)
        
        if not results:
            print("  Aucune inspiration trouvée...")
            return

        # On analyse les chemins renvoyés (format: "JOIE -> Do Maj -> Sol Maj")
        # On prend un chemin représentatif (le premier ou un aléatoire)
        best_path = results[0]['path']
        path_nodes = best_path.split(" -> ")
        
        # Nettoyage du chemin pour ne garder que les accords (pas l'émotion cible)
        sequence = [node for node in path_nodes if node != target_emotion]
        
        print(f"  💡 Séquence générée : {' - '.join(sequence)}")
        print(f"  📊 Nombre de résonances trouvées : {len(results)}")

def main():
    composer = MusicHREI()
    
    # Démo 1 : Composition Joyeuse
    composer.compose("JOIE")
    
    # Démo 2 : Composition Mélancolique
    composer.compose("MÉLANCOLIE")

    print("\n[Innovation] Mutation créative en cours...")
    # On ajoute un lien "illogique" mais créatif
    # Un accord mineur qui mène directement à la Joie (surprise musicale)
    
    # Récupération sécurisée des atomes
    e_min_atom = composer.engine.get_atom_by_label("Mi min")
    joie_atom = composer.engine.get_atom_by_label("JOIE")
    
    if e_min_atom and joie_atom:
        e_min_atom.relate_to(joie_atom.id, "resolution_inattendue")
        print("✨ Lien 'resolution_inattendue' créé entre Mi min et JOIE")
    
    print("\nNouvel essai avec 'JOIE' après mutation :")
    composer.compose("JOIE")

if __name__ == "__main__":
    main()