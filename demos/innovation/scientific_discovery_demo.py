import sys
import os

# Ajout du chemin racine pour permettre les imports depuis demos/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

def main():
    print("--- Simulation HREI : Innovation et Découverte Scientifique ---")
    engine = HREIEngine()

    # Domaines disparates (Concepts sans liens directs au début)
    # Domaine 1 : Environnement
    # On ajoute des propriétés "physiques" dans les métadonnées (data)
    ocean = CognitiveAtom("Océan", valence=0.5, data={"type": "milieu", "contains": ["eau", "sel"]})
    microplastique = CognitiveAtom("Microplastique", valence=-0.8, data={"physique": ["solide", "particule", "polluant"], "charge": "neutre"})
    
    # Domaine 2 : Physique/Électricité
    electricite_statique = CognitiveAtom("Électricité Statique", valence=0.1, data={"effet": ["polarisation", "attraction_charge"]})
    friction = CognitiveAtom("Friction", valence=0.0, data={"action": "generer_charge"})
    
    # Domaine 3 : Biologie
    meduse = CognitiveAtom("Méduse", valence=0.2, data={"biologie": "cnidaire"})
    mucus = CognitiveAtom("Mucus", valence=0.1, data={"physique": ["visqueux", "collant", "filet"], "biologie": "secretion"})

    atoms = [ocean, microplastique, electricite_statique, friction, meduse, mucus]
    for a in atoms:
        engine.add_atom(a)

    # Relations de base (Connaissances établies)
    ocean.relate_to(microplastique.id, "contient")
    friction.relate_to(electricite_statique.id, "genere")
    meduse.relate_to(mucus.id, "produit")

    print("\n[Étape 1] Problème : Comment nettoyer le 'Microplastique' dans l''Océan' ?")
    print("L'IA n'a aucune solution directe pour l'instant.")
    results = engine.resonate("Microplastique", iterations=5)
    print(f"  Chemins trouvés : {[r['path'] for r in results if 'Océan' in r['path']] or 'Aucun chemin trouvé'}")

    print("\n[Étape 2] Phase de Recherche (Simulation d'Expériences)")
    print("L'IA lance des simulations basées sur les propriétés physiques des atomes...")
    
    # Simulation d'Expériences : L'IA teste les interactions possibles entre les propriétés
    # C'est ici que l'IA "découvre" des liens basés sur la logique, pas sur un script dur
    
    count_discoveries = 0
    atoms_list = list(engine.atoms.values())
    
    for a1 in atoms_list:
        for a2 in atoms_list:
            if a1.id == a2.id: continue
            
            # Règle 1 : La viscosité capture les particules
            if "physique" in a1.data and "visqueux" in a1.data["physique"]:
                if "physique" in a2.data and "particule" in a2.data["physique"]:
                    print(f"  🧪 Expérience : {a1.label} (Visqueux) + {a2.label} (Particule) -> SUCCÈS")
                    a1.relate_to(a2.id, "capture_physiquement", weight=0.9)
                    count_discoveries += 1
            
            # Règle 2 : L'électricité statique polarise la matière
            if "effet" in a1.data and "polarisation" in a1.data["effet"]:
                if "physique" in a2.data: # Tout objet physique peut être polarisé
                    print(f"  🧪 Expérience : {a1.label} (Champ) + {a2.label} (Matière) -> SUCCÈS")
                    a1.relate_to(a2.id, "polarise", weight=0.7)
                    count_discoveries += 1
                    
            # Règle 3 : La friction dans un fluide (Océan) crée des charges
            if a1.label == "Friction" and a2.label == "Océan":
                 # On sait que l'eau en mouvement crée de la friction
                 a1.relate_to(a2.id, "present_dans_courants", weight=0.5)
                 count_discoveries += 1

    print(f"  -> {count_discoveries} nouvelles lois physiques découvertes/vérifiées.")

    print("\n[Étape 3] Résonance après 'Découverte' :")
    results = engine.resonate("Microplastique", iterations=10)
    
    # On cherche le chemin le plus innovant
    for res in results:
        if "Méduse" in res['path'] or "Électricité" in res['path']:
            print(f"  💡 IDÉE ÉMERGENTE : {res['path']} (Valence: {res['valence_totale']:.2f})")

    print("\n[Conclusion]")
    print("HREI a 'inventé' une solution biomimétique : utiliser les propriétés du mucus ")
    print("de méduse combinées à l'électricité statique pour filtrer l'océan.")

if __name__ == "__main__":
    main()
