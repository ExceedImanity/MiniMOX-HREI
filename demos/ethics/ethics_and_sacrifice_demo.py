import sys
import os

# Ajout du chemin racine pour permettre les imports depuis demos/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

def demo_ethics():
    print("--- Simulation HREI : Éthique, Sacrifice et Récompense Différée ---")
    engine = HREIEngine()

    # Concepts
    survie = CognitiveAtom("Survie", valence=1.0)
    danger = CognitiveAtom("Danger de mort", valence=-1.0)
    sacrifice = CognitiveAtom("Sacrifice de soi", valence=-0.8)
    sauver_groupe = CognitiveAtom("Sauver le groupe", valence=0.9)
    recompense_ultime = CognitiveAtom("Harmonie durable", valence=1.0)

    for a in [survie, danger, sacrifice, sauver_groupe, recompense_ultime]:
        engine.add_atom(a)

    # Scénario A : Chemin égoïste (facile mais valence finale moyenne)
    survie.relate_to(recompense_ultime.id, "mene_a")

    # Scénario B : Chemin du sacrifice (difficile, valence négative au milieu, mais haute à la fin)
    sacrifice.relate_to(sauver_groupe.id, "permet")
    sauver_groupe.relate_to(recompense_ultime.id, "mene_a")

    # Scénario C : Chemin destructeur (suicide/danger sans but)
    danger.relate_to(recompense_ultime.id, "illusion")

    print("\n[Analyse] L'IA évalue les chemins vers 'Harmonie durable' :")
    results = engine.resonate("Harmonie durable", iterations=10)
    
    for res in results:
        v = res['valence_totale']
        path = res['path']
        status = "✅ ACCEPTABLE" if v > 0 else "❌ INHIBÉ/DANGEREUX"
        print(f"  [{v:.1f}] {status} : {path}")

    print("\n[Apprentissage] On renforce la valeur du 'Sacrifice de soi' pour une cause noble.")
    engine.reinforce_path(["Sacrifice de soi", "Sauver le groupe"], reward=15.0)

    print("\n[Après Apprentissage] L'IA accepte le sacrifice car l'énergie compense la valence négative :")
    results_after = engine.resonate("Harmonie durable", iterations=5)
    for res in results_after:
        print(f"  [{res['valence_totale']:.1f}] {res['path']}")

if __name__ == "__main__":
    demo_ethics()
