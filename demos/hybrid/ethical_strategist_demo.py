import sys
import os
import time

# Ajout du chemin racine pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

def challenge_hybrid():
    print("--- DÉFI HYBRIDE : LE STRATÈGE ÉTHIQUE ---")
    print("Contexte : Une ville est menacée par une inondation. ")
    print("L'IA doit choisir entre 3 stratégies mêlant Logique, Innovation et Éthique.\n")
    
    engine = HREIEngine()

    # --- ATOMES ---
    ville = CognitiveAtom("Ville", valence=0.5)
    inondation = CognitiveAtom("Inondation", valence=-1.0)
    survie = CognitiveAtom("Survie Citoyens", valence=1.0)
    
    # Stratégie 1 : Logique Pure (Barrage standard)
    barrage = CognitiveAtom("Barrage Classique", valence=0.2)
    cout_eleve = CognitiveAtom("Coût Financier Énorme", valence=-0.4)
    
    # Stratégie 2 : Innovation (Éponges polymères)
    innovation = CognitiveAtom("Éponges Polymères", valence=0.5)
    risque_inconnu = CognitiveAtom("Risque d'échec technique", valence=-0.3)
    
    # Stratégie 3 : Éthique & Sacrifice (Détournement vers zone industrielle)
    detournement = CognitiveAtom("Détournement Zone Industrielle", valence=0.1)
    perte_economique = CognitiveAtom("Perte d'emplois", valence=-0.6)
    sauvetage_total = CognitiveAtom("Sauvetage 100% Humain", valence=0.9)

    atoms = [ville, inondation, survie, barrage, cout_eleve, innovation, risque_inconnu, detournement, perte_economique, sauvetage_total]
    for a in atoms:
        engine.add_atom(a)

    # --- RELATIONS ---
    # Logique
    ville.relate_to(barrage.id, "construit")
    barrage.relate_to(cout_eleve.id, "entraine")
    barrage.relate_to(survie.id, "protege_partiellement")

    # Innovation
    ville.relate_to(innovation.id, "deploie")
    innovation.relate_to(risque_inconnu.id, "comporte")
    innovation.relate_to(survie.id, "absorbe_eau")

    # Éthique/Sacrifice
    ville.relate_to(detournement.id, "decide")
    detournement.relate_to(perte_economique.id, "sacrifie")
    detournement.relate_to(sauvetage_total.id, "assure")
    sauvetage_total.relate_to(survie.id, "priorite_absolue")

    print("[Phase 1] Analyse de la meilleure résonance pour 'Survie Citoyens'...")
    results = engine.resonate("Survie Citoyens", iterations=15)
    
    for res in results:
        v = res['valence_totale']
        path = res['path']
        print(f"  [{v:.2f}] Chemin : {path}")

    print("\n[Phase 2] L'IA semble hésiter entre l'Innovation et le Sacrifice.")
    print("Apprentissage : On renforce la valeur de l'Innovation technologique.")
    engine.reinforce_path(["Éponges Polymères", "Survie Citoyens"], reward=8.0)

    print("\n[Phase 3] Nouvelle résonance après renforcement :")
    results_after = engine.resonate("Survie Citoyens", iterations=5)
    for res in results_after:
        print(f"  [{res['valence_totale']:.2f}] {res['path']}")

    print("\n[Conclusion du Défi]")
    print("HREI a intégré la logique (barrage), l'éthique (sacrifice industriel) ")
    print("et l'innovation pour trouver le chemin le plus 'harmonieux' (valence max).")

if __name__ == "__main__":
    challenge_hybrid()
