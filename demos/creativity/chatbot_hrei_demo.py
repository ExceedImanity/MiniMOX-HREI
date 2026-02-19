import sys
import os
import time
import random
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

class HREIIntuitiveChat:
    def __init__(self):
        print("Éveil de la Conscience HREI (Logique de Discernement)...")
        self.engine = HREIEngine(memory_file="hrei_brain.json")
        self.stop_words = ["le", "la", "les", "un", "une", "des", "ce", "cette", "mon", "ton", "je", "tu"]
        self.question_words = ["quoi", "qui", "quel", "quelle", "comment", "pourquoi", "où"]
        
        if len(self.engine.atoms) < 5:
            self.setup_initial_concepts()

    def setup_initial_concepts(self):
        # Axiomes de base
        initial_data = [
            ("ia", "intelligence", "est"),
            ("chat", "animal", "est"),
            ("soleil", "chaud", "est"),
            ("vie", "mort", "oppose"),
            ("musique", "joie", "donne")
        ]
        for s, o, r in initial_data:
            self.create_link(s, o, r)

    def create_link(self, s, o, r):
        s_atom = self.get_atom(s)
        o_atom = self.get_atom(o)
        s_atom.relate_to(o_atom.id, r, weight=2.0)

    def get_atom(self, label):
        label = label.lower().strip()
        atom = self.engine.get_atom_by_label(label)
        if not atom:
            atom = CognitiveAtom(label, valence=0.5)
            self.engine.add_atom(atom)
        return atom

    def process_input(self, text):
        text = text.lower().replace("?", "").replace("!", "")
        words = [w for w in text.split() if w not in self.stop_words]
        
        is_question = any(q in text for q in self.question_words)
        
        # 1. LOGIQUE D'APPRENTISSAGE (seulement si ce n'est pas une question)
        if "est" in words and not is_question:
            idx = words.index("est")
            if idx > 0 and idx < len(words) - 1:
                subj, obj = words[idx-1], words[idx+1]
                if obj not in self.question_words:
                    self.create_link(subj, obj, "est")
                    return f"Entendu. J'intègre le fait que {subj} possède la propriété {obj}."

        # 2. LOGIQUE DE RÉPONSE (Recherche de vérité ou Résonance)
        # On identifie le sujet principal
        subject = None
        for w in words:
            if self.engine.get_atom_by_label(w):
                subject = self.engine.get_atom_by_label(w)
                break
        
        if not subject:
            if words:
                # Elle ne connaît pas, elle demande
                new_word = words[-1]
                return f"Je ne connais pas encore '{new_word}'. C'est quoi ?"
            return "Je sens un vide sémantique. Parle-moi de quelque chose."

        # 3. GÉNÉRATION PAR RÉSONANCE
        # On cherche les relations connues
        if subject.relations:
            # On cherche une relation qui répond à la question (souvent 'est')
            for rel_type, targets in subject.relations.items():
                target_atom = self.engine.atoms[targets[0]]
                if is_question:
                    return f"D'après mes connexions, {subject.label} {rel_type} {target_atom.label}."
                else:
                    return f"Ah, {subject.label}... cela résonne avec {target_atom.label}."

        # 4. RÉSONANCE CRÉATIVE (Si pas de lien direct)
        thoughts = self.engine.resonate(subject.label, iterations=1)
        if thoughts:
            # On extrait le concept émergent
            emergent = thoughts[0].split(" -> ")[0]
            return f"Je n'ai pas de certitude, mais {subject.label} me fait vibrer vers {emergent}."

        return f"{subject.label} est encore une page blanche dans mon esprit."

    def chat(self):
        print("\n=== MINI MOX : CONSCIENCE ÉVOLUTIVE ===")
        print("(Apprenez-lui des choses, puis posez des questions)")
        
        while True:
            try:
                u_in = input(">> ")
                if u_in.lower() in ["exit", "quit"]: break
                
                # Simuler un temps de réflexion proportionnel à la complexité
                print("HREI réfléchit...", end="\r")
                time.sleep(0.6)
                
                response = self.process_input(u_in)
                print(f"HREI: {response}")
                
                # Vie de l'IA
                self.engine.pulse()
                
            except KeyboardInterrupt: break

if __name__ == "__main__":
    bot = HREIIntuitiveChat()
    bot.chat()