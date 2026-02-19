import sys
import os
import random
import time
import math

# Ajout du chemin racine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

class Game2048HREI:
    def __init__(self):
        self.engine = HREIEngine()
        self.grid = [[0] * 4 for _ in range(4)]
        self.score = 0
        self.move_count = 0
        self.setup_hrei()
        
        # Initialisation du plateau
        self.add_random_tile()
        self.add_random_tile()

    def setup_hrei(self):
        """Initialise le 'cerveau' de l'IA pour 2048 (Version Mathématique)."""
        # Concepts stratégiques (Poids ajustés pour la stratégie "Snake")
        self.monotony_atom = CognitiveAtom("MONOTONIE", valence=4.0) # Augmenté : Vital pour le serpent
        self.smoothness_atom = CognitiveAtom("LISSIBILITÉ", valence=0.5) 
        self.free_cells_atom = CognitiveAtom("ESPACE_VITAL", valence=2.5) 
        self.max_corner_atom = CognitiveAtom("ANCRAGE_COIN", valence=15.0) # Massif : Le Roi ne doit jamais bouger
        self.merge_atom = CognitiveAtom("FUSION", valence=1.0) 
        
        # Ajout au moteur
        for a in [self.monotony_atom, self.smoothness_atom, self.free_cells_atom, 
                 self.max_corner_atom, self.merge_atom]:
            self.engine.add_atom(a)

    def add_random_tile(self):
        empty_cells = [(r, c) for r in range(4) for c in range(4) if self.grid[r][c] == 0]
        if not empty_cells: return
        r, c = random.choice(empty_cells)
        self.grid[r][c] = 2 if random.random() < 0.9 else 4

    # --- LOGIQUE DU JEU ---
    def compress(self, grid):
        new_grid = [[0] * 4 for _ in range(4)]
        for r in range(4):
            pos = 0
            for c in range(4):
                if grid[r][c] != 0:
                    new_grid[r][pos] = grid[r][c]
                    pos += 1
        return new_grid

    def merge(self, grid):
        score_gain = 0
        for r in range(4):
            for c in range(3):
                if grid[r][c] != 0 and grid[r][c] == grid[r][c+1]:
                    grid[r][c] *= 2
                    score_gain += grid[r][c]
                    grid[r][c+1] = 0
        return grid, score_gain

    def reverse(self, grid):
        new_grid = []
        for r in range(4):
            new_grid.append(list(reversed(grid[r])))
        return new_grid

    def transpose(self, grid):
        new_grid = [[0] * 4 for _ in range(4)]
        for r in range(4):
            for c in range(4):
                new_grid[r][c] = grid[c][r]
        return new_grid

    def simulate_move(self, grid, direction):
        """Simule un mouvement et retourne (nouvelle_grille, score_gain, a_bougé)."""
        temp_grid = [row[:] for row in grid]
        moved = False
        score = 0
        
        if direction == 'Left':
            temp_grid = self.compress(temp_grid)
            temp_grid, s = self.merge(temp_grid)
            score += s
            temp_grid = self.compress(temp_grid)
        elif direction == 'Right':
            temp_grid = self.reverse(temp_grid)
            temp_grid = self.compress(temp_grid)
            temp_grid, s = self.merge(temp_grid)
            score += s
            temp_grid = self.compress(temp_grid)
            temp_grid = self.reverse(temp_grid)
        elif direction == 'Up':
            temp_grid = self.transpose(temp_grid)
            temp_grid = self.compress(temp_grid)
            temp_grid, s = self.merge(temp_grid)
            score += s
            temp_grid = self.compress(temp_grid)
            temp_grid = self.transpose(temp_grid)
        elif direction == 'Down':
            temp_grid = self.transpose(temp_grid)
            temp_grid = self.reverse(temp_grid)
            temp_grid = self.compress(temp_grid)
            temp_grid, s = self.merge(temp_grid)
            score += s
            temp_grid = self.compress(temp_grid)
            temp_grid = self.reverse(temp_grid)
            temp_grid = self.transpose(temp_grid)

        if temp_grid != grid:
            moved = True
            
        return temp_grid, score, moved

    # --- INTELLIGENCE HREI ---
    def evaluate_state_resonance(self, grid):
        """Calcule la 'beauté' (Valence Totale) d'un état du plateau."""
        valence = 0.0
        
        # 1. ESPACE VITAL (Cases vides)
        empty_count = sum([row.count(0) for row in grid])
        valence += math.log(empty_count + 1) * self.free_cells_atom.valence * 10
        
        # 2. ANCRAGE COIN (Le plus gros chiffre dans un coin)
        max_val = max([max(row) for row in grid])
        corners = [grid[0][0], grid[0][3], grid[3][0], grid[3][3]]
        if max_val in corners:
            valence += math.log(max_val) * self.max_corner_atom.valence
        else:
            valence -= math.log(max_val) * self.max_corner_atom.valence # Pénalité sévère

        # 3. MONOTONIE (Serpentin)
        # On veut que les chiffres décroissent dans une direction (gauche/droite haut/bas)
        # Simplification : on regarde juste les lignes et colonnes
        monotony_score = 0
        for r in range(4):
            current = 0
            next_val = 0
            for c in range(3):
                current = grid[r][c] if grid[r][c] > 0 else 0
                next_val = grid[r][c+1] if grid[r][c+1] > 0 else 0
                if current >= next_val: monotony_score += 1
                if current <= next_val: monotony_score += 1 # On accepte les deux sens
        
        for c in range(4):
            for r in range(3):
                current = grid[r][c] if grid[r][c] > 0 else 0
                next_val = grid[r+1][c] if grid[r+1][c] > 0 else 0
                if current >= next_val: monotony_score += 1
                if current <= next_val: monotony_score += 1

        valence += monotony_score * self.monotony_atom.valence

        # 4. LISSIBILITÉ (Smoothness)
        # Pénalité si des voisins ont des valeurs très éloignées (ex: 1024 à côté de 2)
        smoothness_penalty = 0
        for r in range(4):
            for c in range(4):
                if grid[r][c] > 0:
                    val = math.log(grid[r][c], 2)
                    # Voisin droite
                    if c < 3 and grid[r][c+1] > 0:
                        neighbor = math.log(grid[r][c+1], 2)
                        smoothness_penalty += abs(val - neighbor)
                    # Voisin bas
                    if r < 3 and grid[r+1][c] > 0:
                        neighbor = math.log(grid[r+1][c], 2)
                        smoothness_penalty += abs(val - neighbor)
        
        valence -= smoothness_penalty * self.smoothness_atom.valence

        return valence

    # --- INTERFACE HREI CORE ---
    def simulator_interface(self, state, mode):
        """Adapteur pour le moteur HREI générique."""
        # state est un tuple de tuples (grid)
        grid = [list(row) for row in state]
        
        if mode == "GET_ACTIONS":
            actions = []
            for m in ['Up', 'Down', 'Left', 'Right']:
                _, _, moved = self.simulate_move(grid, m)
                if moved: actions.append(m)
            return actions
            
        elif mode == "GET_CHANCE_OUTCOMES":
            # Retourne liste de (next_state, probability)
            outcomes = []
            empty_cells = [(r, c) for r in range(4) for c in range(4) if grid[r][c] == 0]
            if not empty_cells: return []
            
            # Optimisation: Sampling si trop de cases vides (comme avant)
            cells_to_test = empty_cells if len(empty_cells) <= 6 else random.sample(empty_cells, 6)
            prob_factor = 1.0 / len(cells_to_test)
            
            for r, c in cells_to_test:
                # 2 (90%)
                grid[r][c] = 2
                outcomes.append((tuple(tuple(row) for row in grid), 0.9 * prob_factor))
                # 4 (10%)
                grid[r][c] = 4
                outcomes.append((tuple(tuple(row) for row in grid), 0.1 * prob_factor))
                grid[r][c] = 0 # Backtrack
            return outcomes
            
        else: # Simulation d'une action
            # mode est une action (ex: 'Up')
            new_grid, score, _ = self.simulate_move(grid, mode)
            # Retourne (next_state, reward, next_turn_type)
            # La récompense immédiate est le score * valence fusion
            reward = score * self.merge_atom.valence
            return (tuple(tuple(row) for row in new_grid), reward, "CHANCE")

    def evaluator_interface(self, state):
        """Adapteur pour l'évaluation."""
        grid = [list(row) for row in state]
        return self.evaluate_state_resonance(grid)

    def hrei_decide(self):
        """HREI utilise le moteur générique (Core) avec une profondeur équilibrée (6)."""
        best_move = None
        max_resonance = -float('inf')
        
        # Le "Juste Milieu" pour 4096
        depth = 6
        threshold = 3 # 3 niveaux précis, 3 niveaux intuitifs
        cache = {}
        
        start_time = time.time()
        
        moves = ['Up', 'Down', 'Left', 'Right']
        for move in moves:
            grid_after, score_gain, valid = self.simulate_move(self.grid, move)
            if not valid: continue
            
            state_after = tuple(tuple(row) for row in grid_after)
            immediate_reward = score_gain * self.merge_atom.valence
            
            future_val = self.engine.hybrid_resonance_search(
                initial_state=state_after,
                simulator_func=self.simulator_interface,
                evaluator_func=self.evaluator_interface,
                depth=depth - 1,
                precise_threshold=threshold,
                turn="CHANCE",
                cache=cache
            )
            
            resonance = immediate_reward + 0.95 * future_val
            
            if resonance > max_resonance:
                max_resonance = resonance
                best_move = move
        
        duration = time.time() - start_time
        return best_move, max_resonance, duration

    def play(self, stop_at_2048=False, stop_at_4096=False):
        print(f"--- 2048 HREI (Core Engine: Hybrid Depth 10, Stop4096={stop_at_4096}) ---")
        self.print_grid()
        
        while True:
            move, resonance, duration = self.hrei_decide()
            
            if not move:
                print("\nGAME OVER !")
                print(f"Score Final : {self.score}")
                print(f"Plus gros bloc : {max([max(row) for row in self.grid])}")
                break
                
            print(f"\n[Tour {self.move_count}] HREI choisit : {move.upper()} (Resonance: {resonance:.1f}, Pensée: {duration:.3f}s)")
            
            self.grid, score_gain, _ = self.simulate_move(self.grid, move)
            self.score += score_gain
            self.move_count += 1
            self.add_random_tile()
            self.print_grid()

            if any(2048 in row for row in self.grid):
                print("\n VICTOIRE ! TUILE 2048 ATTEINTE !")
                if stop_at_2048:
                    break
            
            if any(4096 in row for row in self.grid):
                print("\n LÉGENDAIRE ! TUILE 4096 ATTEINTE !")
                if stop_at_4096:
                    break

    def print_grid(self):
        print(f"Score: {self.score}")
        print("-" * 25)
        for row in self.grid:
            print("| " + " | ".join(f"{x:4}" if x > 0 else "    " for x in row) + " |")
            print("-" * 25)

if __name__ == "__main__":
    stop_2048 = "--end" in sys.argv
    stop_4096 = "--end2" in sys.argv
    game = Game2048HREI()
    game.play(stop_at_2048=stop_2048, stop_at_4096=stop_4096)
