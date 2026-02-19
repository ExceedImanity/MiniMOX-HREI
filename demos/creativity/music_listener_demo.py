import sys
import os
import time

# Ajout du chemin racine pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

class MusicListenerHREI:
    def __init__(self):
        self.engine = HREIEngine()
        self.internal_state = CognitiveAtom("État Interne Neutre", valence=0.0)
        self.engine.add_atom(self.internal_state)
        self.setup_musical_perception()

    def setup_musical_perception(self):
        # --- ATOMES DE PERCEPTION (Ce que l'IA "entend") ---
        self.perceptions = {
            "RYTHME_LENT": CognitiveAtom("Perception: Rythme Lent", valence=0.2),
            "RYTHME_AGRESSIF": CognitiveAtom("Perception: Rythme Agressif", valence=-0.3),
            "HARMONIE_DOUCE": CognitiveAtom("Perception: Harmonie Douce", valence=0.5),
            "DISSONANCE_FORTE": CognitiveAtom("Perception: Dissonance Forte", valence=-0.6)
        }
        for a in self.perceptions.values():
            self.engine.add_atom(a)

        # --- RÉACTIONS ÉMOTIONNELLES ---
        self.emotions = {
            "APAISEMENT": CognitiveAtom("Émotion: Apaisement", valence=0.8),
            "AGITATION": CognitiveAtom("Émotion: Agitation", valence=-0.5),
            "TRISTESSE": CognitiveAtom("Émotion: Tristesse", valence=-0.2),
            "ENTHOUSIASME": CognitiveAtom("Émotion: Enthousiasme", valence=0.7)
        }
        for a in self.emotions.values():
            self.engine.add_atom(a)

        # --- CABLAGE DE L'EMPATHIE MUSICALE ---
        # Douceur + Lent -> Apaisement
        self.perceptions["HARMONIE_DOUCE"].relate_to(self.emotions["APAISEMENT"].id, "provoque")
        self.perceptions["RYTHME_LENT"].relate_to(self.emotions["APAISEMENT"].id, "favorise")
        
        # Agressif + Dissonant -> Agitation
        self.perceptions["RYTHME_AGRESSIF"].relate_to(self.emotions["AGITATION"].id, "provoque")
        self.perceptions["DISSONANCE_FORTE"].relate_to(self.emotions["AGITATION"].id, "provoque")

        # Lien vers l'état interne
        for e in self.emotions.values():
            e.relate_to(self.internal_state.id, "modifie")

    def listen(self, sequence, title="Session d'écoute"):
        print(f"\n--- {title} ---")
        print(f"🎶 L'IA écoute : {' - '.join(sequence)}")
        
        total_impact = 0.0
        active_emotions = []

        # L'IA traite chaque élément sonore
        for sound in sequence:
            perception = self.perceptions.get(sound)
            if perception:
                # Résonance INVERSE : On part des émotions pour voir si elles "vibrent" avec ce son
                for emotion_key, emotion_atom in self.emotions.items():
                    results = self.engine.resonate(emotion_atom.label, iterations=10)
                    for res in results:
                        if perception.label in res['path']:
                            if emotion_key not in active_emotions:
                                active_emotions.append(emotion_key)
                
                total_impact += perception.valence
        
        # Mise à jour de l'état interne (Empathie)
        self.internal_state.valence = (self.internal_state.valence + total_impact) / 2
        
        print(f"🧠 Analyse HREI :")
        print(f"  > Émotions stimulées : {', '.join(active_emotions) if active_emotions else 'Aucune (Indifférence)'}")
        print(f"  > Niveau de bien-être interne (Valence) : {self.internal_state.valence:.2f}")
        
        if self.internal_state.valence > 0.5:
            print("  💬 L'IA 'sourit' (vibration harmonieuse détectée)")
        elif self.internal_state.valence < -0.3:
            print("  💬 L'IA se 'contracte' (vibration discordante détectée)")
        else:
            print("  💬 L'IA reste attentive et stable")

def main():
    listener = MusicListenerHREI()
    
    # Session 1 : Une berceuse (Lent et Doux)
    listener.listen(["RYTHME_LENT", "HARMONIE_DOUCE", "HARMONIE_DOUCE"], "Berceuse au piano")
    
    # Session 2 : Du Heavy Metal (Agressif et Dissonant)
    listener.listen(["RYTHME_AGRESSIF", "DISSONANCE_FORTE", "RYTHME_AGRESSIF"], "Concert de Metal Industriel")
    
    # Session 3 : Jazz Expérimental (Dissonance mais Rythme Lent)
    listener.listen(["RYTHME_LENT", "DISSONANCE_FORTE", "HARMONIE_DOUCE"], "Jazz Improvisé")

if __name__ == "__main__":
    main()
