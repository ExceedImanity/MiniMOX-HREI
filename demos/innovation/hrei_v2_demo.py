import sys
import os
import numpy as np

# Ajout du chemin racine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

def main():
    print("--- Démonstration HREI v2.0 : Embeddings & Hebbian Learning ---")
    engine = HREIEngine()

    # 1. Création d'atomes avec Embeddings simulés (vecteurs 3D pour simplifier)
    # Proximité : Chat (1,0,0) est proche de Tigre (0.9, 0.1, 0)
    # Loin de : Ordinateur (0, 0, 1)
    
    chat = CognitiveAtom("Chat")
    chat.embedding = [1.0, 0.05, 0.0]
    
    tigre = CognitiveAtom("Tigre")
    tigre.embedding = [0.95, 0.1, 0.0]
    
    lion = CognitiveAtom("Lion")
    lion.embedding = [0.9, 0.0, 0.1]
    
    ordi = CognitiveAtom("Ordinateur")
    ordi.embedding = [0.0, 0.1, 0.95]
    
    clavier = CognitiveAtom("Clavier")
    clavier.embedding = [0.05, 0.0, 0.9]

    # Ajout
    for a in [chat, tigre, lion, ordi, clavier]:
        engine.add_atom(a)

    print("\n[Test 1] Auto-Connexion par similarité vectorielle")
    print(f"Avant: Chat a {len(chat.relations)} relations.")
    
    # Seuil 0.8 devrait lier Chat-Tigre-Lion entre eux, et Ordi-Clavier entre eux.
    # Mais pas Chat-Ordi.
    result = engine.auto_connect_by_similarity(threshold=0.8)
    print(result)
    
    print(f"Après: Chat a {len(chat.relations)} relations.")
    if 'semantic_similarity' in chat.relations:
        targets = [engine.atoms[tid].label for tid in chat.relations['semantic_similarity']]
        print(f"  Chat est maintenant lié à : {targets}")
    
    # 2. Test Bidirectionnel
    print("\n[Test 2] Recherche Bidirectionnelle")
    # Créons une chaîne manuelle pour relier Lion à Clavier (un peu absurde mais pour le test)
    # Lion -> Zoo -> Guichet -> Ordinateur -> Clavier
    zoo = CognitiveAtom("Zoo")
    guichet = CognitiveAtom("Guichet")
    
    engine.add_atom(zoo)
    engine.add_atom(guichet)
    
    lion.relate_to(zoo.id, "vit_dans")
    zoo.relate_to(guichet.id, "a_entree")
    guichet.relate_to(ordi.id, "utilise")
    ordi.relate_to(clavier.id, "possede")
    
    print("Recherche de chemin entre 'Lion' et 'Clavier'...")
    path = engine.resonate_bidirectional("Lion", "Clavier", max_depth=5)
    print(f"Résultat : {path}")

    # 3. Test Apprentissage Hebbien
    print("\n[Test 3] Apprentissage Hebbien")
    # On renforce le lien Lion -> Zoo
    print(f"Poids initial Lion->Zoo : {lion.link_weights.get(zoo.id, 'Non défini')}")
    
    # Supposons qu'on a validé ce chemin
    path_list = ["Lion", "Zoo", "Guichet"]
    engine.reinforce_path(path_list, reward=2.0)
    
    print(f"Poids après renforcement Lion->Zoo : {lion.link_weights.get(zoo.id)}")
    print(f"Poids après renforcement Zoo->Guichet : {zoo.link_weights.get(guichet.id)}")

if __name__ == "__main__":
    main()
