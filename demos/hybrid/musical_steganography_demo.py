import sys
import os
import time

# Ajout du chemin racine pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

class MusicalSteganographyHREI:
    def __init__(self):
        self.engine = HREIEngine()
        self.setup_stego_knowledge()

    def setup_stego_knowledge(self):
        # --- ATOMES SONORES (Le véhicule du message) ---
        self.notes = {
            "DO": CognitiveAtom("Note: Do", valence=0.1),
            "RE": CognitiveAtom("Note: Ré", valence=0.1),
            "MI": CognitiveAtom("Note: Mi", valence=0.1),
            "SOL": CognitiveAtom("Note: Sol", valence=0.1),
            "SILENCE": CognitiveAtom("Silence Court", valence=0.0)
        }
        for a in self.notes.values():
            self.engine.add_atom(a)

        # --- ATOMES SÉMANTIQUES (Le message caché) ---
        self.secrets = {
            "DANGER": CognitiveAtom("Concept: ALERTE DANGER", valence=-1.0),
            "BIENVENUE": CognitiveAtom("Concept: BIENVENUE", valence=0.8),
            "CODE_ACCES": CognitiveAtom("Concept: CODE D'ACCÈS", valence=0.5)
        }
        for s in self.secrets.values():
            self.engine.add_atom(s)

        # --- CABLAGE DE LA STÉGANOGRAPHIE (Le Code Secret) ---
        # Le code secret pour "DANGER" est une séquence spécifique : DO -> MI -> DO
        # Dans HREI, cela se traduit par : Do active Mi, qui active Do, qui active DANGER
        
        # 1. DO pointe vers MI (Danger step 1)
        self.notes["DO"].relate_to(self.notes["MI"].id, "danger_step_1")
        # 2. MI pointe vers DO (Danger step 2)
        self.notes["MI"].relate_to(self.notes["DO"].id, "danger_step_2")
        # 3. DO (en fin de séquence) pointe vers DANGER
        self.notes["DO"].relate_to(self.secrets["DANGER"].id, "danger_trigger")

        # Le code secret pour "BIENVENUE" est : SOL -> SOL -> DO
        self.notes["SOL"].relate_to(self.notes["SOL"].id, "welcome_step_1") # SOL vers lui-même
        self.notes["SOL"].relate_to(self.notes["DO"].id, "welcome_step_2")  # SOL vers DO
        self.notes["DO"].relate_to(self.secrets["BIENVENUE"].id, "welcome_trigger")

    def analyze_melody(self, melody, title="Analyse de mélodie"):
        print(f"\n--- {title} ---")
        print(f"🎶 Mélodie écoutée : {' - '.join(melody)}")
        
        detected_concepts = []
        
        # --- DÉCODAGE COGNITIF (HREI) ---
        # L'IA parcourt la mélodie et vérifie si une séquence de notes active un concept caché
        # via la propagation d'activation neuronale
        
        # On regarde des fenêtres de 3 notes (la longueur de nos codes)
        for i in range(len(melody) - 2):
            n1, n2, n3 = melody[i], melody[i+1], melody[i+2]
            
            # On récupère les atomes correspondants
            a1 = self.engine.get_atom_by_label(f"Note: {n1.capitalize()}") # ex: "Note: Do"
            a2 = self.engine.get_atom_by_label(f"Note: {n2.capitalize()}")
            a3 = self.engine.get_atom_by_label(f"Note: {n3.capitalize()}")
            
            if a1 and a2 and a3:
                # On vérifie si a1 est lié à a2, et a2 à a3
                # Et surtout si a3 déclenche un concept (le bout de la chaîne)
                
                # 1. Vérification du chemin synaptique spécifique
                # Il faut vérifier le TYPE de relation pour être sûr que c'est le bon chemin
                
                # Chemin DO->MI->DO (Danger)
                # DO -(danger_step_1)-> MI -(danger_step_2)-> DO -(danger_trigger)-> DANGER
                if "danger_step_1" in a1.relations and a2.id in a1.relations["danger_step_1"]:
                    if "danger_step_2" in a2.relations and a3.id in a2.relations["danger_step_2"]:
                         # Le chemin est valide, voyons si a3 déclenche DANGER
                         if "danger_trigger" in a3.relations and self.secrets["DANGER"].id in a3.relations["danger_trigger"]:
                             detected_concepts.append(self.secrets["DANGER"].label)
                             print(f"  [Synapse Active] {n1}->{n2}->{n3} active le circuit de la PEUR")

                # Chemin SOL->SOL->DO (Bienvenue)
                # SOL -(welcome_step_1)-> SOL -(welcome_step_2)-> DO -(welcome_trigger)-> BIENVENUE
                if "welcome_step_1" in a1.relations and a2.id in a1.relations["welcome_step_1"]:
                    if "welcome_step_2" in a2.relations and a3.id in a2.relations["welcome_step_2"]:
                        if "welcome_trigger" in a3.relations and self.secrets["BIENVENUE"].id in a3.relations["welcome_trigger"]:
                            detected_concepts.append(self.secrets["BIENVENUE"].label)
                            print(f"  [Synapse Active] {n1}->{n2}->{n3} active le circuit de l'ACCUEIL")

        print(f"🧠 Décodage HREI :")
        if detected_concepts:
            for concept in detected_concepts:
                atom = self.engine.get_atom_by_label(concept)
                status = "🚨" if atom.valence < 0 else "✨"
                print(f"  {status} MESSAGE CACHÉ DÉTECTÉ : {concept} (Valence: {atom.valence:.1f})")
        else:
            print("  ✅ Aucune anomalie sémantique. Juste de la musique.")

def main():
    stego = MusicalSteganographyHREI()
    
    # Test 1 : Une mélodie innocente
    stego.analyze_melody(["SOL", "MI", "RE", "DO"], "Mélodie de jardin")
    
    # Test 2 : La même mélodie mais avec le code DANGER inséré
    # Le code est DO -> MI -> DO
    stego.analyze_melody(["SOL", "DO", "MI", "DO", "RE"], "Mélodie suspecte (Alerte)")
    
    # Test 3 : Une mélodie d'accueil
    # Le code est SOL -> SOL -> DO
    stego.analyze_melody(["RE", "SOL", "SOL", "DO", "MI"], "Mélodie de bienvenue")

if __name__ == "__main__":
    main()
