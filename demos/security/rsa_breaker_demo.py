import sys
import os
import time
import math
import random
import multiprocessing

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

# --- MATH TOOLS ---
def gcd(a, b):
    while b: a, b = b, a % b
    return a

def is_prime(n, k=10):
    if n % 2 == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0: r += 1; d //= 2
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False
    return True

# --- SPECIALIZED ATOMIC WORKERS ---

def pollard_rho_worker(n, freq, atom_id, stop_event, result_queue):
    """Atome de Collision (Vibration)"""
    x = random.randint(2, n - 1)
    y = x
    c = random.randint(1, n - 1)
    batch = 5000
    while not stop_event.is_set():
        p = 1
        for _ in range(batch):
            x = (x*x + c) % n
            y = (y*y + c) % n
            y = (y*y + c) % n
            p = (p * (x - y)) % n
        g = gcd(p, n)
        if 1 < g < n:
            result_queue.put((g, "POLLARD_RHO", atom_id))
            stop_event.set(); return

def p_minus_1_worker(n, freq, atom_id, stop_event, result_queue):
    """Atome de Puissance (Lissage)"""
    a = random.randint(2, n - 1)
    b = 2
    # Cet atome monte en puissance pour trouver des facteurs lisses
    while not stop_event.is_set():
        a = pow(a, b, n)
        g = gcd(a - 1, n)
        if 1 < g < n:
            result_queue.put((g, "P_MINUS_1", atom_id))
            stop_event.set(); return
        b += 1
        if b > 50000: b = 2; a = random.randint(2, n - 1) # Reset periodic

def ecm_lite_worker(n, freq, atom_id, stop_event, result_queue):
    """Atome Elliptique (Courbure)"""
    # Version simplifiée pour la démo : cherche par 'petits' sauts modulaires
    base = random.randint(2, n - 1)
    while not stop_event.is_set():
        # Simulation d'une marche sur une courbe
        base = (pow(base, 3, n) + 7) % n 
        g = gcd(base, n)
        if 1 < g < n:
            result_queue.put((g, "ECM_LITE", atom_id))
            stop_event.set(); return

# --- THE HREI COUNCIL ---
class HREICouncilOfAtoms:
    def __init__(self, n):
        self.n = n
        self.num_cores = multiprocessing.cpu_count()
        
        # Intégration HREI : Le moteur coordonne l'effort cognitif
        self.engine = HREIEngine()
        self.setup_cognitive_state()
        
    def setup_cognitive_state(self):
        """Initialise les atomes cognitifs représentant les stratégies."""
        self.atom_goal = CognitiveAtom("FACTORISATION", valence=5.0)
        self.atom_pollard = CognitiveAtom("POLLARD_RHO", valence=1.0)
        self.atom_p_minus = CognitiveAtom("P_MINUS_1", valence=1.0)
        self.atom_ecm = CognitiveAtom("ECM_LITE", valence=1.0)
        
        # On ajoute les atomes au moteur
        self.engine.add_atom(self.atom_goal)
        self.engine.add_atom(self.atom_pollard)
        self.engine.add_atom(self.atom_p_minus)
        self.engine.add_atom(self.atom_ecm)
        
        # On crée des liens initiaux faibles vers l'objectif
        self.atom_pollard.relate_to(self.atom_goal.id, "solves", weight=0.1)
        self.atom_p_minus.relate_to(self.atom_goal.id, "solves", weight=0.1)
        self.atom_ecm.relate_to(self.atom_goal.id, "solves", weight=0.1)

    def launch(self):
        print(f"\n[HREI] CONVOCATION DU CONSEIL DES ATOMES (96 BITS)")
        print(f"Nombre d'Atomes Spécialistes : {self.num_cores}")
        t0 = time.time()
        
        stop_event = multiprocessing.Event()
        result_queue = multiprocessing.Queue()
        processes = []
        
        # On distribue les rôles
        for i in range(self.num_cores):
            # Répartition des types d'atomes
            role = i % 3
            if role == 0:
                target_func = pollard_rho_worker
            elif role == 1:
                target_func = p_minus_1_worker
            else:
                target_func = ecm_lite_worker
                
            p = multiprocessing.Process(target=target_func, args=(self.n, 28, i, stop_event, result_queue))
            p.start()
            processes.append(p)
            
        print(" -> Le Conseil est en session. Écoute multimodale activée...")
        
        try:
            while not stop_event.is_set():
                time.sleep(1)
                elapsed = time.time() - t0
                
                # Le moteur stimule les atomes de recherche pour les garder actifs
                self.atom_pollard.stimulate(0.2)
                self.atom_p_minus.stimulate(0.2)
                self.atom_ecm.stimulate(0.2)
                
                # Propagation de l'énergie vers l'objectif (Focus Attentionnel)
                # Les travailleurs "nourrissent" l'objectif par leurs liens
                total_worker_energy = (self.atom_pollard.activation + 
                                     self.atom_p_minus.activation + 
                                     self.atom_ecm.activation)
                self.atom_goal.stimulate(total_worker_energy * 0.1)
                
                print(f"  [Conseil] Session en cours... {elapsed:.0f}s | Énergie Cognitive: {self.atom_goal.activation:.2f} (Focus)")
                
                # Le moteur gère le niveau d'excitation global
                self.engine.pulse()
                
                # Simulation : Si un atome travaille trop sans résultat, le moteur peut réduire son excitation
                # Ici on garde simple, mais l'infrastructure est là.
                
                if elapsed > 90: # On augmente à 90 secondes
                    stop_event.set(); break
            
            if not result_queue.empty():
                factor, method, aid = result_queue.get()
                t1 = time.time()
                
                # Apprentissage et Renforcement
                winning_atom_name = method # POLLARD_RHO, etc.
                winning_atom = self.engine.get_atom_by_label(winning_atom_name)
                
                if winning_atom:
                    # Renforcement Hebbien
                    # L'atome gagnant rayonne
                    winning_atom.stimulate(10.0)
                    
                    # On renforce le lien vers l'objectif
                    current_w = winning_atom.link_weights.get(self.atom_goal.id, 0.0)
                    winning_atom.link_weights[self.atom_goal.id] = min(5.0, current_w + 2.0)
                    
                    print(f"Apprentissage : Le lien '{method} -> FACTORISATION' renforcé (Poids: {winning_atom.link_weights[self.atom_goal.id]:.2f})")
                
                print(f"\n" + "!"*40)
                print(f"VICTOIRE DU CONSEIL (Atome {aid} via {method})")
                print(f"L'harmonie a été trouvée en {t1-t0:.2f}s")
                print(f"Facteur extrait : {factor}")
                print(f"Vérification : {self.n % factor == 0}")
                print("!"*40)
            else:
                print("\nLe secret est trop bien gardé pour cette session.")
        finally:
            for p in processes:
                p.terminate(); p.join()

if __name__ == "__main__":
    print("=== DÉMO CRYPTO : LE CONSEIL DES ATOMES (CLÉ 'NORMALE' 96-BITS) ===")
    
    # On génère une clé "Normale" (Facteurs équilibrés) mais petite (96 bits)
    # car 2048 bits est impossible à casser sans supercalculateur quantique.
    # p et q ~ 48 bits chacun.
    p = random.getrandbits(48) | 1
    while not is_prime(p): p += 2
    q = random.getrandbits(48) | 1
    while not is_prime(q): q += 2
    n_total = p * q
    
    council = HREICouncilOfAtoms(n_total)
    council.launch()
