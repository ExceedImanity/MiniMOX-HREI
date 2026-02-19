import json
import os
import time
import random
import heapq
import numpy as np
import concurrent.futures
from typing import Dict, List, Optional, Any
from atoms.base import CognitiveAtom

class HREIEngine:
    """
    Le Moteur HREI V3 Ultimate.
    - Beam Search (Largeur Variable)
    - Mémoire Épisodique (Abstraction via Hashes)
    - Multi-threading (Parallélisme Cognitif)
    - Résonance Sémantique & Auto-Connection
    """
    def __init__(self, memory_file: str = "memory_episodic.json"):
        self.atoms: Dict[str, CognitiveAtom] = {}
        self.memory_file = memory_file
        self.memory: Dict[str, Any] = {}
        self.load_memory()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

    def __del__(self):
        try:
            self.executor.shutdown(wait=False)
        except:
            pass

    # --- MÉMOIRE ---
    def save_memory(self):
        if self.memory_file is None:
            return
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f)

    def load_memory(self):
        if self.memory_file is None:
            return
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    self.memory = json.load(f)
            except:
                self.memory = {}

    def remember_experience(self, state_key: str, action: str, valence: float):
        if abs(valence) > 50000:
            self.memory[state_key] = {"action": action, "valence": valence, "time": time.time()}
            if len(self.memory) > 5000:
                oldest = min(self.memory.keys(), key=lambda k: self.memory[k].get("time", 0))
                del self.memory[oldest]
            self.save_memory()

    # --- PERSISTANCE DU CERVEAU ---
    def save_state(self, filepath: str):
        """Sauvegarde l'état complet du cerveau (Atomes + Connexions)."""
        state = {
            "atoms": {}
        }
        for atom_id, atom in self.atoms.items():
            state["atoms"][atom_id] = {
                "id": atom.id,
                "label": atom.label,
                "data": atom.data,
                "valence": atom.valence,
                "energy": atom.energy,
                "activation": atom.activation,
                "last_accessed": atom.last_accessed,
                "relations": atom.relations,
                "link_weights": atom.link_weights,
                "embedding": atom.embedding
            }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=4)

    def load_state(self, filepath: str):
        """Charge un état complet du cerveau."""
        if not os.path.exists(filepath):
            return
            
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.atoms = {}
            for atom_id, atom_data in state.get("atoms", {}).items():
                atom = CognitiveAtom(
                    label=atom_data["label"], 
                    data=atom_data.get("data"), 
                    valence=atom_data.get("valence", 0.0)
                )
                atom.id = atom_data.get("id", atom_id)
                atom.energy = atom_data.get("energy", 1.0)
                atom.activation = atom_data.get("activation", 0.0)
                atom.last_accessed = atom_data.get("last_accessed", time.time())
                atom.relations = atom_data.get("relations", {})
                atom.link_weights = atom_data.get("link_weights", {})
                atom.embedding = atom_data.get("embedding")
                
                self.atoms[atom.id] = atom
                
        except Exception as e:
            print(f"[HREI] Erreur lors du chargement de l'état : {e}")
            # On continue avec un cerveau vide ou partiellement chargé

    # --- CYCLE DE VIE ---
    def pulse(self):
        """Simule le métabolisme de l'IA (Déclin et Oubli)."""
        for atom in list(self.atoms.values()):
            atom.decay(rate=0.005)
            if atom.energy < 0.01 and not atom.link_weights:
                if atom.id in self.atoms:
                    del self.atoms[atom.id]

    # --- GESTION DES ATOMES ---
    def add_atom(self, atom: CognitiveAtom):
        if atom.embedding is None:
            atom.embedding = np.random.rand(64).tolist()
        self.atoms[atom.id] = atom
        return atom.id

    def get_atom_by_label(self, label: str) -> Optional[CognitiveAtom]:
        for atom in self.atoms.values():
            if atom.label == label:
                return atom
        return None

    # --- ANALYSE SÉMANTIQUE ---
    def _cosine_similarity(self, vec1, vec2):
        if vec1 is None or vec2 is None: return 0.0
        v1, v2 = np.array(vec1), np.array(vec2)
        norm1, norm2 = np.linalg.norm(v1), np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0: return 0.0
        return float(np.dot(v1, v2) / (norm1 * norm2))

    def auto_connect_by_similarity(self, threshold: float = 0.8):
        """Crée des liens automatiques basés sur la similarité vectorielle."""
        count = 0
        atoms_list = list(self.atoms.values())
        for i in range(len(atoms_list)):
            for j in range(i + 1, len(atoms_list)):
                a1, a2 = atoms_list[i], atoms_list[j]
                sim = self._cosine_similarity(a1.embedding, a2.embedding)
                if sim > threshold:
                    a1.relate_to(a2.id, "semantic_similarity", weight=sim)
                    a2.relate_to(a1.id, "semantic_similarity", weight=sim)
                    count += 1
        return f"Auto-Connect: {count} nouveaux liens sémantiques."

    # --- RÉSONANCE CONCEPTUELLE (Backward Chaining) ---
    def resonate_bidirectional(self, start_label: str, end_label: str, max_depth: int = 5):
        """
        Recherche un chemin entre deux concepts en utilisant une recherche bidirectionnelle.
        """
        start_atom = self.get_atom_by_label(start_label)
        end_atom = self.get_atom_by_label(end_label)
        
        if not start_atom or not end_atom:
            return "Chemin impossible : atomes inconnus."
            
        # Files d'attente pour BFS : (id_atome, chemin_parcouru_labels)
        # Chemin avant : [Start, ..., Current]
        queue_fwd = [(start_atom.id, [start_atom.label])]
        visited_fwd = {start_atom.id: [start_atom.label]}
        
        # Chemin arrière : [End, ..., Current] (sens inverse des flèches)
        queue_bwd = [(end_atom.id, [end_atom.label])]
        visited_bwd = {end_atom.id: [end_atom.label]}
        
        for _ in range(max_depth):
            # --- Expansion Avant ---
            next_queue_fwd = []
            for curr_id, path in queue_fwd:
                curr_atom = self.atoms.get(curr_id)
                if not curr_atom: continue
                
                # Voisins sortants
                outgoing = []
                for target_ids in curr_atom.relations.values():
                    outgoing.extend(target_ids)
                
                for neighbor_id in outgoing:
                    if neighbor_id in visited_bwd:
                        # Intersection trouvée !
                        path_end = visited_bwd[neighbor_id] # [End, ..., Neighbor]
                        full_path = path + path_end[::-1]
                        return " -> ".join(full_path)
                    
                    if neighbor_id not in visited_fwd:
                        if neighbor_id in self.atoms:
                            new_path = path + [self.atoms[neighbor_id].label]
                            visited_fwd[neighbor_id] = new_path
                            next_queue_fwd.append((neighbor_id, new_path))
            queue_fwd = next_queue_fwd

            # --- Expansion Arrière ---
            next_queue_bwd = []
            for curr_id, path in queue_bwd:
                # Voisins entrants (ceux qui pointent vers curr_id)
                incoming = []
                for a in self.atoms.values():
                    for target_ids in a.relations.values():
                        if curr_id in target_ids:
                            incoming.append(a.id)
                
                for neighbor_id in incoming:
                    if neighbor_id in visited_fwd:
                        # Intersection trouvée !
                        path_start = visited_fwd[neighbor_id] # [Start, ..., Neighbor]
                        full_path = path_start + path[::-1]
                        return " -> ".join(full_path)

                    if neighbor_id not in visited_bwd:
                        if neighbor_id in self.atoms:
                            new_path = path + [self.atoms[neighbor_id].label]
                            visited_bwd[neighbor_id] = new_path
                            next_queue_bwd.append((neighbor_id, new_path))
            queue_bwd = next_queue_bwd
            
        return "Aucun chemin trouvé."

    def reinforce_path(self, path_labels: List[str], reward: float = 1.0):
        """Renforce les connexions entre une séquence d'atomes."""
        atoms = []
        for label in path_labels:
            atom = self.get_atom_by_label(label)
            if atom:
                atoms.append(atom)
        
        if len(atoms) < 2:
            return

        for i in range(len(atoms) - 1):
            source = atoms[i]
            target = atoms[i+1]
            
            # Renforcement Hebbien
            source.stimulate(reward * 0.01)
            target.stimulate(reward * 0.01)
            
            # Renforce le lien existant ou en crée un nouveau
            # On normalise l'impact pour ne pas saturer instantanément (max 5.0)
            weight_inc = min(3.0, reward * 0.2)
            source.relate_to(target.id, "reinforced_sequence", weight=weight_inc)

    def resonate(self, goal_label: str, iterations: int = 5):
        """Fait vibrer le réseau à partir d'un concept."""
        goal_atom = self.get_atom_by_label(goal_label)
        if not goal_atom: return []
        
        goal_atom.stimulate(0.5)
        results = []
        for _ in range(iterations):
            path_atoms = [goal_atom]
            current = goal_atom
            for _ in range(5): # Profondeur de pensée
                sources = [a for a in self.atoms.values() if any(current.id in t for t in a.relations.values())]
                if not sources: break
                
                weights = []
                for s in sources:
                    w = s.energy * (1.0 + s.activation)
                    w *= s.link_weights.get(current.id, 1.0)
                    sim = self._cosine_similarity(s.embedding, current.embedding)
                    w *= (1.0 + sim)
                    weights.append(max(0.001, w))
                
                next_atom = random.choices(sources, weights=weights)[0]
                next_atom.stimulate(0.2)
                current = next_atom
                path_atoms.append(current)
            
            path_str = " -> ".join(reversed([a.label for a in path_atoms]))
            total_valence = sum(a.valence for a in path_atoms)
            results.append({
                'path': path_str,
                'valence_totale': total_valence
            })
        return results

    # --- RECHERCHE HYBRIDE (Moteur Décisionnel) ---
    def predict_best_action(self, initial_state: Any, simulator_func, 
                            evaluator_func, depth: int, precise_threshold: int = 4, 
                            beam_width: Optional[int] = None, parallel: bool = True):
        """
        Détermine la meilleure action à entreprendre en utilisant la résonance.
        Retourne : (best_action, expected_valence)
        """
        actions = simulator_func(initial_state, "GET_ACTIONS")
        if not actions: return None, 0.0
        
        best_action = None
        max_val = -float('inf')
        
        cache = {}
        for action in actions:
            next_state, reward, next_turn = simulator_func(initial_state, action)
            val = self.hybrid_resonance_search(
                next_state, simulator_func, evaluator_func, 
                depth - 1, precise_threshold, next_turn, cache, 
                parallel=parallel, beam_width=beam_width
            )
            total_val = reward + 0.95 * val
            if total_val > max_val:
                max_val = total_val
                best_action = action
                
        return best_action, max_val

    def hybrid_resonance_search(self, initial_state: Any, simulator_func, 
                               evaluator_func, depth: int, precise_threshold: int = 4, 
                               turn: str = "AGENT", cache: Optional[Dict] = None, 
                               parallel: bool = True, beam_width: Optional[int] = None):
        if cache is None: cache = {}
        
        if hasattr(initial_state, "to_hash"):
            state_key = initial_state.to_hash()
        else:
            state_key = str(initial_state)

        if state_key in self.memory and depth < 4:
            mem = self.memory[state_key]
            if mem["valence"] > 100000: return mem["valence"]

        current_val = evaluator_func(initial_state)
        if current_val < -500000: return current_val 
        if depth == 0: return current_val

        if turn == "AGENT":
            actions = simulator_func(initial_state, "GET_ACTIONS")
            if not actions: return current_val

            candidates = []
            for action in actions:
                next_state, reward, next_turn = simulator_func(initial_state, action)
                score = evaluator_func(next_state) + reward + random.uniform(0, 0.1)
                candidates.append((score, action, next_state, reward, next_turn))
            
            width = beam_width if beam_width is not None else len(candidates)
            top_candidates = heapq.nlargest(width, candidates, key=lambda x: x[0])
            
            results = []
            if parallel and depth > 3:
                futures = []
                for _, action, next_state, reward, next_turn in top_candidates:
                    f = self.executor.submit(
                        self.hybrid_resonance_search,
                        next_state, simulator_func, evaluator_func, 
                        depth - 1, precise_threshold, next_turn, {}, False, beam_width
                    )
                    futures.append((f, reward))
                for f, r in futures:
                    try:
                        results.append(r + 0.95 * f.result())
                    except Exception as e:
                        print(f"Error in thread: {e}")
                        results.append(-1000000)
            else:
                for _, action, next_state, reward, next_turn in top_candidates:
                    val = self.hybrid_resonance_search(
                        next_state, simulator_func, evaluator_func, 
                        depth - 1, precise_threshold, next_turn, cache, False, beam_width
                    )
                    results.append(reward + 0.95 * val)
            
            best_final_val = max(results) if results else -float('inf')
            
            if best_final_val > 50000 or best_final_val < -50000:
                try:
                    best_idx = results.index(best_final_val)
                    best_act = top_candidates[best_idx][1]
                    self.remember_experience(state_key, best_act, best_final_val)
                except: pass
            
            return best_final_val

        elif turn == "OPPONENT":
            # L'adversaire joue pour gagner (Minimiser notre score ou Maximiser le sien)
            # Dans un jeu à somme nulle (HREI vs Minimax), l'adversaire minimise notre valence.
            actions = simulator_func(initial_state, "GET_ACTIONS")
            if not actions: return current_val
            
            min_val = float('inf')
            
            for action in actions:
                next_state, reward, next_turn = simulator_func(initial_state, action)
                # On récursive pour obtenir la valeur du futur état
                val = self.hybrid_resonance_search(
                    next_state, simulator_func, evaluator_func, 
                    depth - 1, precise_threshold, next_turn, cache, False, beam_width
                )
                
                # Le score total est la récompense (souvent négative si l'adversaire gagne) + valeur future
                # Si l'adversaire joue 'action', cela nous donne 'reward' (ex: -1000 si défaite)
                current_score = reward + 0.95 * val
                
                if current_score < min_val:
                    min_val = current_score
            
            return min_val

        elif turn == "CHANCE":
            outcomes = simulator_func(initial_state, "GET_CHANCE_OUTCOMES")
            if not outcomes: return current_val
            total_val, total_prob = 0.0, 0.0
            significant = [(s, p) for s, p in outcomes if p > 0.05] or outcomes
            for next_state, prob in significant:
                val = self.hybrid_resonance_search(
                    next_state, simulator_func, evaluator_func, depth - 1, 
                    precise_threshold, "AGENT", cache, False, beam_width
                )
                total_val += val * prob
                total_prob += prob
            return total_val / total_prob if total_prob > 0 else 0

        return current_val
