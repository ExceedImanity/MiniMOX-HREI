import sys
import os
import time
import string
import itertools
import random

# Ajout du chemin racine pour importer le moteur
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

# --- DATA ---
# Un texte secret (Citation de Alan Turing)
SECRET_MESSAGE = """
WE CAN ONLY SEE A SHORT DISTANCE AHEAD BUT WE CAN SEE PLENTY THERE THAT NEEDS TO BE DONE
"""
KEY_TARGET = "HREI" # La clé secrète

# Fréquences standard des lettres en Anglais (pour la résonance)
ENGLISH_FREQS = {
    'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0, 'N': 6.7, 'S': 6.3,
    'H': 6.1, 'R': 6.0, 'D': 4.3, 'L': 4.0, 'C': 2.8, 'U': 2.8, 'M': 2.4,
    'W': 2.4, 'F': 2.2, 'G': 2.0, 'Y': 2.0, 'P': 1.9, 'B': 1.5, 'V': 1.0,
    'K': 0.8, 'J': 0.15, 'X': 0.15, 'Q': 0.10, 'Z': 0.07
}

# Bigrammes les plus fréquents en Anglais
ENGLISH_BIGRAMS = ["TH", "HE", "IN", "ER", "AN", "RE", "ED", "ON", "ES", "ST", "EN", "AT", "TO", "NT", "HA"]

class VigenereCipher:
    """Outils cryptographiques de base."""
    
    @staticmethod
    def clean(text):
        return "".join([c for c in text.upper() if c in string.ascii_uppercase])

    @staticmethod
    def encrypt(plaintext, key):
        plaintext = VigenereCipher.clean(plaintext)
        key = VigenereCipher.clean(key)
        ciphertext = []
        for i, char in enumerate(plaintext):
            shift = ord(key[i % len(key)]) - ord('A')
            encrypted = chr(((ord(char) - ord('A') + shift) % 26) + ord('A'))
            ciphertext.append(encrypted)
        return "".join(ciphertext)

    @staticmethod
    def decrypt(ciphertext, key):
        key = VigenereCipher.clean(key)
        plaintext = []
        for i, char in enumerate(ciphertext):
            shift = ord(key[i % len(key)]) - ord('A')
            decrypted = chr(((ord(char) - ord('A') - shift) % 26) + ord('A'))
            plaintext.append(decrypted)
        return "".join(plaintext)

    @staticmethod
    def score_text(text):
        """Calcule la 'Résonance Linguistique' améliorée."""
        if not text: return -1000
        score = 0
        
        # 1. Fréquence des lettres (Unigrammes)
        counts = {c: 0 for c in string.ascii_uppercase}
        for c in text: counts[c] += 1
        total = len(text)
        for char, count in counts.items():
            observed = (count / total) * 100
            expected = ENGLISH_FREQS.get(char, 0)
            score -= abs(observed - expected) * 2 # Pénalité linéaire
            
        # 2. Résonance des Bigrammes (Structure profonde)
        for i in range(len(text) - 1):
            bigram = text[i:i+2]
            if bigram in ENGLISH_BIGRAMS:
                score += 15 # Récompense la structure
                
        # 3. Bonus pour les Atomes de Vocabulaire
        common_words = ["THE", "AND", "THAT", "CAN", "SEE", "BUT", "ARE", "FOR", "NOT", "WE", "YOU", "ALL", "ANY", "HER", "HIS", "ONE", "OUT"]
        for word in common_words:
            if word in text:
                score += 150 # Très forte résonance
                
        return score

class HREICryptoBreaker:
    def __init__(self, ciphertext, key_length):
        self.ciphertext = VigenereCipher.clean(ciphertext)
        self.key_length = key_length
        self.engine = HREIEngine()
        self.setup_atoms()

    def setup_atoms(self):
        """Initialise les concepts de cryptanalyse."""
        self.freq_atom = CognitiveAtom("FREQUENCE", valence=1.0)
        self.vocab_atom = CognitiveAtom("VOCABULAIRE", valence=2.0)
        self.engine.add_atom(self.freq_atom)
        self.engine.add_atom(self.vocab_atom)

    # --- INTERFACE POUR LE CORE ENGINE ---
    
    def simulator_interface(self, state, mode):
        """
        State: (current_key_partial_string)
        Ex: "A" -> "AB", "AC"...
        """
        current_key = state
        
        if mode == "GET_ACTIONS":
            # Si on a atteint la longueur cible, pas d'actions (feuille)
            if len(current_key) >= self.key_length:
                return []
            # Sinon, on tente les 26 lettres
            return list(string.ascii_uppercase)
            
        elif mode == "GET_CHANCE_OUTCOMES":
            # Pas de hasard ici, c'est déterministe
            return []
            
        else: # Simulation d'une action (Ajouter une lettre à la clé)
            # mode est la lettre à ajouter (ex: 'B')
            next_key = current_key + mode
            
            # Évaluation immédiate :
            # On déchiffre partiellement avec cette clé pour voir si ça "sonne" bien
            # Astuce : On ne déchiffre que les lettres correspondant aux positions de cette nouvelle lettre de clé
            # Pour simplifier, on déchiffre tout avec la clé partielle répétée
            
            # On retourne (next_state, reward, next_turn)
            # Reward est 0 car on juge l'état final surtout
            return (next_key, 0, "AGENT")

    def evaluator_interface(self, state):
        """
        Évalue la qualité d'une clé partielle ou complète.
        """
        key = state
        if len(key) == 0: return -1000
        
        # Pour évaluer une clé partielle (ex: "AB" pour longueur 4),
        # On doit être malin. On évalue la cohérence des colonnes déchiffrées.
        # Ou alors, on cycle la clé partielle ("AB" -> "ABABAB")
        
        decrypted = VigenereCipher.decrypt(self.ciphertext, key)
        resonance = VigenereCipher.score_text(decrypted)
        
        # Normalisation par la Valence des atomes
        return resonance * self.freq_atom.valence

    def break_it(self):
        print(f"\n[HREI] Lancement de la 'Résonance Cryptographique'...")
        print(f"Message Chiffré (extrait): {self.ciphertext[:40]}...")
        print(f"Longueur Clé Cible: {self.key_length}")
        
        start_time = time.time()
        
        # Le Core va construire l'arbre des clés
        # Profondeur = Longueur de la clé (4)
        # Threshold = 2 (Pour être hybride : précis au début, intuitif à la fin)
        
        best_key = ""
        # Comme le Core évalue des états complets, on va ruser.
        # On va utiliser le Core pour choisir chaque lettre séquentiellement en regardant le futur.
        
        current_key = ""
        
        # On construit la clé lettre par lettre en utilisant la puissance du Core
        for i in range(self.key_length):
            print(f" -> Analyse de la lettre {i+1}/{self.key_length}...")
            best_letter = None
            max_val = -float('inf')
            
            # On teste les 26 lettres pour cette position
            # Mais pour chaque lettre, on demande au Core : "Si je choisis ça, quel est le potentiel futur ?"
            
            candidates = list(string.ascii_uppercase)
            
            # Optimisation HREI : On ne fait pas de pré-filtrage de profondeur 0 car il est trompeur
            # (le texte partiellement déchiffré est trop bruité).
            # On laisse le Beam Search élaguer intelligemment avec un faisceau étroit.
            
            for letter in candidates:
                temp_key = current_key + letter
                
                # On lance une recherche hybride à partir de là
                remaining_depth = self.key_length - (i + 1)
                
                if remaining_depth == 0:
                    val = self.evaluator_interface(temp_key)
                else:
                    # On demande au Core de projeter
                    # OPTIMISATION : On limite le faisceau (beam_width) et on désactive le thread (parallel=False)
                    # pour éviter l'overhead sur une tâche CPU-bound simple.
                    val = self.engine.hybrid_resonance_search(
                        initial_state=temp_key,
                        simulator_func=self.simulator_interface,
                        evaluator_func=self.evaluator_interface,
                        depth=remaining_depth, # Regarder jusqu'à la fin de la clé
                        precise_threshold=1,   # Très intuitif
                        turn="AGENT",
                        beam_width=3,          # Faisceau suffisant pour ne pas rater la bonne branche
                        parallel=False         # Éviter l'overhead thread
                    )
                
                if val > max_val:
                    max_val = val
                    best_letter = letter
            
            current_key += best_letter
            print(f"    -> Résonance trouvée : '{best_letter}' (Score: {max_val:.1f})")
            print(f"    -> Clé actuelle : {current_key}")

        duration = time.time() - start_time
        
        full_text = VigenereCipher.decrypt(self.ciphertext, current_key)
        return current_key, full_text, duration

def brute_force_attack(ciphertext, key_len):
    print(f"\n[BRUTE FORCE] Lancement de l'attaque exhaustive...")
    start = time.time()
    attempts = 0
    
    # Générateur de clés AAAA...ZZZZ
    chars = string.ascii_uppercase
    for key_tuple in itertools.product(chars, repeat=key_len):
        key = "".join(key_tuple)
        attempts += 1
        
        # Test stupide : est-ce que ça ressemble à de l'anglais ?
        decrypted = VigenereCipher.decrypt(ciphertext, key)
        if "THE" in decrypted and "THAT" in decrypted: # Critère simple
             duration = time.time() - start
             return key, decrypted, duration, attempts
             
        if attempts % 50000 == 0:
            print(f" -> {attempts} clés testées...")
            
    return None, None, time.time() - start, attempts

if __name__ == "__main__":
    print("=== DÉMO SÉCURITÉ : HREI vs BRUTE FORCE ===")
    
    # 1. Chiffrement
    clean_msg = VigenereCipher.clean(SECRET_MESSAGE)
    encrypted_msg = VigenereCipher.encrypt(clean_msg, KEY_TARGET)
    
    print(f"Clé Secrète : {KEY_TARGET}")
    print(f"Message Clair : {clean_msg[:40]}...")
    print(f"Message Crypté : {encrypted_msg[:40]}...")
    
    # 2. Attaque HREI (Intelligente)
    hrei = HREICryptoBreaker(encrypted_msg, len(KEY_TARGET))
    hrei_key, hrei_text, hrei_time = hrei.break_it()
    
    print(f"\n[RÉSULTAT HREI]")
    print(f"Clé trouvée : {hrei_key}")
    print(f"Temps : {hrei_time:.4f} secondes")
    print(f"Texte : {hrei_text[:60]}...")
    
    # 3. Attaque Brute Force (Stupide)
    # Attention, si la clé est longue (>4), ça va être très long.
    # Ici clé de 4 lettres = 456,976 possibilités. Rapide pour un PC moderne, mais instructif.
    bf_key, bf_text, bf_time, bf_count = brute_force_attack(encrypted_msg, len(KEY_TARGET))
    
    print(f"\n[RÉSULTAT BRUTE FORCE]")
    print(f"Clé trouvée : {bf_key}")
    print(f"Temps : {bf_time:.4f} secondes")
    print(f"Clés testées : {bf_count}")
    
    print("\n--- CONCLUSION ---")
    if hrei_key == KEY_TARGET:
        ratio = bf_time / hrei_time if hrei_time > 0 else 0
        print(f"HREI a réussi ! Elle a été {ratio:.1f}x plus rapide (conceptuellement).")
        print("Note: En Python pur, HREI est ralentie par l'overhead des objets, mais l'algo explore beaucoup moins de branches.")
    else:
        print("HREI a échoué (La résonance n'a pas suffi).")