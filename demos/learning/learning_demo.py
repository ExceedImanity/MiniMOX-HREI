import sys
import os

# Ajout du chemin racine pour permettre les imports depuis demos/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

def demo_learning():
    print("--- Démonstration de l'Apprentissage Immédiat (HREI) ---")
    engine = HREIEngine()

    # Création d'un mini-monde de décision
    faim = CognitiveAtom("Faim")
    manger_pomme = CognitiveAtom("Manger Pomme")
    manger_caillou = CognitiveAtom("Manger Caillou")
    energie = CognitiveAtom("Énergie")
    mal_ventre = CognitiveAtom("Mal de Ventre")

    for a in [faim, manger_pomme, manger_caillou, energie, mal_ventre]:
        engine.add_atom(a)

    # Relations de base (État Naïf : Tout ce qui rentre dans la bouche donne de l'énergie ?)
    faim.relate_to(manger_pomme.id, "action_possible")
    faim.relate_to(manger_caillou.id, "action_possible")
    
    # Croyance initiale erronée : Le caillou donne aussi de l'énergie
    manger_pomme.relate_to(energie.id, "resultat", weight=1.0)
    manger_caillou.relate_to(energie.id, "resultat", weight=1.0) # <--- Erreur cognitive
    
    # La réalité (cachée pour l'instant dans la conséquence)
    manger_caillou.relate_to(mal_ventre.id, "consequence_reelle")

    print("\n[Avant Apprentissage] L'IA est naïve (Bébé) et pense que tout se mange :")
    results = engine.resonate("Énergie", iterations=10)
    paths = [r['path'] for r in results]
    
    # Affichage simplifié
    unique_paths = list(set(paths))
    for p in unique_paths:
        print(f"  ? Hypothèse : {p}")

    print("\n[Expérience & Feedback]")
    print("1. L'IA mange la Pomme -> Miam ! (Renforcement Positif)")
    engine.reinforce_path(["Manger Pomme", "Énergie"], reward=5.0)
    
    print("2. L'IA mange le Caillou -> Aïe ! (Punition / Renforcement Négatif)")
    # On affaiblit le lien Caillou -> Énergie car ce n'est pas vrai
    # Dans HREI, une "punition" peut être vue comme une stimulation négative ou une baisse de poids
    atom_caillou = engine.get_atom_by_label("Manger Caillou")
    if atom_caillou:
        # On réduit manuellement le poids vers Énergie pour simuler la déception
        current_w = atom_caillou.link_weights.get(energie.id, 1.0)
        atom_caillou.link_weights[energie.id] = max(0.1, current_w * 0.1) # Chute drastique de la croyance
        print(f"  -> La croyance 'Caillou=Énergie' s'effondre (Poids: {current_w} -> {atom_caillou.link_weights[energie.id]})")

    print("\n[Après Apprentissage] L'IA a corrigé son modèle du monde :")
    results = engine.resonate("Énergie", iterations=10)
    paths = [r['path'] for r in results]
    
    counts = {}
    for p in paths:
        counts[p] = counts.get(p, 0) + 1
        
    for p, c in counts.items():
        print(f"  {p} (Probabilité: {c*10}%)")

    print("\nNote : L'IA a appris par l'expérience (Heuristique) et non par statistiques massives.")

if __name__ == "__main__":
    demo_learning()
