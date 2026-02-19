import sys
import os
from collections import Counter

# Ajout du chemin racine pour permettre les imports depuis demos/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

def demo_choice():
    print("--- Simulation HREI : Le Labyrinthe des Choix ---")
    engine = HREIEngine()

    # Objectif final
    bonheur = CognitiveAtom("Bonheur")
    
    # Chemin A : Travail acharné (Long)
    etudes = CognitiveAtom("Études")
    diplome = CognitiveAtom("Diplôme")
    travail = CognitiveAtom("Travail")
    argent = CognitiveAtom("Argent")
    
    # Chemin B : Loterie (Court mais incertain)
    ticket = CognitiveAtom("Ticket Loto")
    gain = CognitiveAtom("Gain Rapide")

    atoms = [bonheur, etudes, diplome, travail, argent, ticket, gain]
    for a in atoms:
        # Neutralisation des embeddings pour isoler l'effet du renforcement
        a.embedding = [1.0] * 64
        engine.add_atom(a)

    # Construction des relations
    etudes.relate_to(diplome.id, "mene_a")
    diplome.relate_to(travail.id, "permet")
    travail.relate_to(argent.id, "genere")
    argent.relate_to(bonheur.id, "contribue")
    
    ticket.relate_to(gain.id, "peut_donner")
    gain.relate_to(bonheur.id, "contribue")

    print("\n[Étape 1] Exploration initiale")
    results = engine.resonate("Bonheur", iterations=10)
    unique_paths = list(set([r['path'] for r in results]))
    for r in unique_paths:
        print(f"  - {r}")

    print("\n[Étape 2] Renforcement du chemin stable")
    engine.reinforce_path(["Études", "Diplôme", "Travail", "Argent", "Bonheur"], reward=10.0)

    print("\n[Étape 3] Observation de la préférence")
    all_res = engine.resonate("Bonheur", iterations=100)
    all_paths = [r['path'] for r in all_res]
    
    counts = Counter(all_paths)
    print("Répartition des 'pensées' de l'IA :")
    for path, count in counts.items():
        percentage = (count / 100) * 100
        print(f"  [{percentage}%] {path}")

if __name__ == "__main__":
    demo_choice()
