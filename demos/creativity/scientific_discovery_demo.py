import sys
import os
import time
import random
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

# --- LA CHIMIE VIRTUELLE ---
PERIODIC_TABLE = {
    "H": {"bonds": 1, "weight": 1.0},
    "O": {"bonds": 2, "weight": 16.0},
    "N": {"bonds": 3, "weight": 14.0},
    "C": {"bonds": 4, "weight": 12.0}
    # On retire Cl et S pour simplifier l'espace et forcer les bases
}

class MoleculeState:
    def __init__(self):
        self.atoms = [] 
        self.bonds = [] 
        self.open_bonds = {} 
        self.next_id = 0

    def add_atom(self, symbol):
        uid = self.next_id
        self.next_id += 1
        self.atoms.append((symbol, uid))
        self.open_bonds[uid] = PERIODIC_TABLE[symbol]["bonds"]
        return uid

    def bond(self, id1, id2):
        if self.open_bonds[id1] > 0 and self.open_bonds[id2] > 0:
            # Vérifier qu'ils ne sont pas déjà liés
            if (id1, id2) in self.bonds or (id2, id1) in self.bonds: return False
            
            self.bonds.append((id1, id2))
            self.open_bonds[id1] -= 1
            self.open_bonds[id2] -= 1
            return True
        return False

    def clone(self):
        new = MoleculeState()
        new.atoms = list(self.atoms); new.bonds = list(self.bonds)
        new.open_bonds = self.open_bonds.copy(); new.next_id = self.next_id
        return new

    def get_formula(self):
        if not self.atoms: return "Vide"
        counts = {}
        for sym, _ in self.atoms:
            counts[sym] = counts.get(sym, 0) + 1
        
        res = ""
        if "C" in counts: res += "C" + (str(counts["C"]) if counts["C"] > 1 else ""); del counts["C"]
        if "H" in counts: res += "H" + (str(counts["H"]) if counts["H"] > 1 else ""); del counts["H"]
        for sym in sorted(counts.keys()):
            res += sym + (str(counts[sym]) if counts[sym] > 1 else "")
        return res

    def to_hash(self): return f"{self.get_formula()}_{sum(self.open_bonds.values())}"

class AutomatedLab:
    def __init__(self, memory_file="ultimate_chem.json"):
        if os.path.exists(memory_file): os.remove(memory_file)
        self.engine = HREIEngine(memory_file=memory_file)
        self.discovered = set()
        self.setup_cognitive_elements()

    def setup_cognitive_elements(self):
        """Initialise les atomes cognitifs pour chaque élément chimique."""
        print("[HREI] Initialisation de la connaissance chimique...")
        
        # Création des atomes éléments avec des propriétés "émotionnelles" (stabilité)
        # Valence élevée = Élément noble/stable (pas le cas ici, ils veulent tous réagir)
        # Valence basse = Élément réactif
        self.atom_h = CognitiveAtom("H", valence=1.0) # Hydrogène aime se lier
        self.atom_o = CognitiveAtom("O", valence=2.0) # Oxygène très social
        self.atom_n = CognitiveAtom("N", valence=3.0) 
        self.atom_c = CognitiveAtom("C", valence=4.0) # Carbone, le constructeur
        
        for atom in [self.atom_h, self.atom_o, self.atom_n, self.atom_c]:
            self.engine.add_atom(atom)
            
        # Définition des affinités chimiques initiales (Connaissance a priori)
        # H aime O (Eau)
        self.atom_h.relate_to(self.atom_o.id, "affinity", weight=2.0)
        self.atom_o.relate_to(self.atom_h.id, "affinity", weight=2.0)
        
        # C aime H (Organique)
        self.atom_c.relate_to(self.atom_h.id, "affinity", weight=1.5)
        self.atom_h.relate_to(self.atom_c.id, "affinity", weight=1.5)

    def simulator_interface(self, state, mode):
        if mode == "GET_ACTIONS":
            actions = []
            # 1. AJOUTER (Limité pour éviter les monstres)
            if len(state.atoms) < 6: 
                for sym in PERIODIC_TABLE.keys(): actions.append(f"ADD_{sym}")
            
            # 2. LIER (Liberté Totale)
            open_ids = [uid for uid, open_b in state.open_bonds.items() if open_b > 0]
            # On teste toutes les paires possibles
            for i in range(len(open_ids)):
                for j in range(i + 1, len(open_ids)):
                    uid1, uid2 = open_ids[i], open_ids[j]
                    # On évite de lier un atome à lui-même
                    if (uid1, uid2) not in state.bonds and (uid2, uid1) not in state.bonds:
                        actions.append(f"BOND_{uid1}_{uid2}")
            
            # --- INTELLIGENCE COGNITIVE (HREI) ---
            # On trie les actions non pas au hasard, mais par "Désir Chimique"
            # Les atomes qui ont une forte affinité (lien synaptique fort) sont priorisés
            def cognitive_sort(action):
                if action.startswith("BOND_"):
                    parts = action.split("_")
                    u1, u2 = int(parts[1]), int(parts[2])
                    # On retrouve les symboles des atomes
                    sym1 = state.atoms[u1][0]
                    sym2 = state.atoms[u2][0]
                    
                    # On interroge le moteur : quelle est la force du lien entre ces deux concepts ?
                    a1 = self.engine.get_atom_by_label(sym1)
                    if a1:
                        # On cherche le poids dans link_weights
                        # Attention: HREI stocke les poids par ID (label)
                        weight = a1.link_weights.get(sym2, 0.0)
                        return -weight # Négatif pour trier décroissant
                return 0 # Pas de préférence

            actions.sort(key=cognitive_sort)
            return actions or ["WAIT"]
        else:
            new_state = state.clone(); reward = -0.1
            if mode.startswith("ADD_"): new_state.add_atom(mode.split("_")[1])
            elif mode.startswith("BOND_"):
                parts = mode.split("_")
                if new_state.bond(int(parts[1]), int(parts[2])):
                    reward += 0.5
                else:
                    reward -= 0.5 # Pénalité pour action invalide
            return (new_state, reward, "AGENT")

    def evaluator_interface(self, state):
        formula = state.get_formula()
        if formula in self.discovered: return -5000.0
        
        total_open = sum(state.open_bonds.values())
        if total_open == 0 and len(state.atoms) > 1:
            # VICTOIRE
            return 2000.0
        
        # Guide vers la stabilité
        return -total_open * 50.0

    def run_discovery_loop(self, duration=60):
        print(f"=== HREI ULTIMATE LAB : CHIMIE ORGANIQUE (Timer: {duration}s) ===")
        t_start = time.time()
        
        # On force les départs sur O, N, C pour voir H2O, NH3, CH4
        starters = ["O", "N", "C"]
        idx = 0
        
        while time.time() - t_start < duration:
            current_state = MoleculeState()
            current_state.add_atom(starters[idx % 3])
            idx += 1
            
            for _ in range(20): 
                action, _ = self.engine.predict_best_action(
                    current_state, self.simulator_interface, self.evaluator_interface,
                    depth=5, precise_threshold=5, beam_width=20, parallel=False
                )
                if not action or action == "WAIT": break
                current_state, _, _ = self.simulator_interface(current_state, action)
                
                if sum(current_state.open_bonds.values()) == 0 and len(current_state.atoms) > 1:
                    formula = current_state.get_formula()
                    if formula not in self.discovered:
                        print(f" [+] DÉCOUVERTE : {formula}")
                        self.discovered.add(formula)
                        
                        # --- APPRENTISSAGE HEBBIEN ---
                        # Le moteur renforce les liens entre les atomes qui ont formé une molécule stable
                        print("     [Cerveau] La molécule est stable. Renforcement des liens synaptiques...")
                        for id1, id2 in current_state.bonds:
                            sym1 = current_state.atoms[id1][0]
                            sym2 = current_state.atoms[id2][0]
                            
                            # On utilise le moteur pour renforcer le chemin
                            # Cela rendra la formation de ce type de liaison plus probable à l'avenir
                            self.engine.reinforce_path([sym1, sym2], reward=2.0)
                    break
            
        print(f"\n--- SESSION TERMINÉE ---")
        print(f"Catalogue : {', '.join(sorted(list(self.discovered)))}")

if __name__ == "__main__":
    lab = AutomatedLab()
    lab.run_discovery_loop(60)