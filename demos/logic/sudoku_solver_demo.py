import sys
import os
import time
import math
import random
import copy

# Ajout du chemin racine pour permettre les imports depuis demos/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

class SudokuHREI:
    def __init__(self, size=9):
        self.size = size
        self.block_size = int(math.sqrt(size))
        if self.block_size * self.block_size != self.size:
            raise ValueError("La taille du Sudoku doit être un carré parfait (ex: 9, 16, 25)")
            
        self.grid = [[0] * self.size for _ in range(self.size)]
        self.engine = HREIEngine()
        self.setup_atoms()
        
    def setup_atoms(self):
        """Atomes de logique pure et de perception."""
        # Atomes structurels
        self.coherence_atom = CognitiveAtom("COHERENCE", valence=5.0)
        self.conflict_atom = CognitiveAtom("CONFLIT", valence=-10.0)
        self.completion_atom = CognitiveAtom("COMPLETUDE", valence=2.0)
        
        self.engine.add_atom(self.coherence_atom)
        self.engine.add_atom(self.conflict_atom)
        self.engine.add_atom(self.completion_atom)
        
        # Atomes de valeurs (facultatif mais aide à la visualisation mentale)
        for i in range(1, self.size + 1):
            val_atom = CognitiveAtom(f"VAL_{i}", valence=0.1)
            self.engine.add_atom(val_atom)

    def print_grid(self, grid=None):
        if grid is None: grid = self.grid
        width = len(str(self.size)) + 1
        line_len = (width * self.size) + (self.block_size * 2) + 1
        
        print("\n" + "-" * line_len)
        for r in range(self.size):
            line = ""
            for c in range(self.size):
                val = grid[r][c]
                # Affiche 1-9 normalement, puis A-Z pour >9
                if val == 0: 
                    symb = "."
                elif val < 10: 
                    symb = str(val)
                else: 
                    symb = chr(ord('A') + val - 10)
                
                line += f"{symb:>{width}}"
                if (c + 1) % self.block_size == 0 and c != self.size - 1: 
                    line += " |"
            print(line)
            if (r + 1) % self.block_size == 0 and r != self.size - 1:
                print("-" * line_len)
        print("-" * line_len)

    # --- LOGIQUE SUDOKU (Contraintes) ---
    def get_masks(self, grid):
        """Calcule les masques de bits pour les lignes, colonnes et blocs."""
        rows = [0] * self.size
        cols = [0] * self.size
        blks = [0] * self.size
        
        for r in range(self.size):
            for c in range(self.size):
                val = grid[r][c]
                if val != 0:
                    mask = 1 << val
                    rows[r] |= mask
                    cols[c] |= mask
                    b = (r // self.block_size) * self.block_size + (c // self.block_size)
                    blks[b] |= mask
        return rows, cols, blks

    def get_valid_moves_fast(self, r, c, rows, cols, blks):
        """Retourne les chiffres possibles pour une case (O(1) avec masques pré-calculés)."""
        b = (r // self.block_size) * self.block_size + (c // self.block_size)
        used = rows[r] | cols[c] | blks[b]
        # On inverse les bits utilisés et on masque pour ne garder que les bits 1..size
        available = ~used & ((1 << (self.size + 1)) - 2)
        
        moves = []
        while available:
            # Récupère le bit de poids faible à 1 (valeur possible)
            bit = available & -available
            val = bit.bit_length() - 1
            moves.append(val)
            available ^= bit
        return moves

    def get_valid_moves(self, grid, r, c):
        """Wrapper compatible avec l'ancien code (moins performant car recalcule tout)."""
        if grid[r][c] != 0: return []
        rows, cols, blks = self.get_masks(grid)
        return self.get_valid_moves_fast(r, c, rows, cols, blks)

    def get_possible_values_map_fast(self, grid, rows, cols, blks):
        """Construit une map (r,c) -> [valeurs possibles] pour toute la grille."""
        possibilities = {}
        # On peut optimiser en ne parcourant que les cases vides si on les connaît,
        # mais ici on parcourt la grille.
        for r in range(self.size):
            for c in range(self.size):
                if grid[r][c] == 0:
                    possibilities[(r, c)] = self.get_valid_moves_fast(r, c, rows, cols, blks)
        return possibilities

    def find_hidden_singles_fast(self, grid, possibilities):
        """
        Cherche des 'Hidden Singles' optimisé.
        """
        # On utilise des dictionnaires pour compter les occurrences
        # Lignes
        for r in range(self.size):
            counts = {}
            # On ne regarde que les cases vides de cette ligne
            for c in range(self.size):
                if grid[r][c] == 0 and (r, c) in possibilities:
                    for val in possibilities[(r, c)]:
                        if val not in counts: counts[val] = []
                        counts[val].append(c)
            for val, cols in counts.items():
                if len(cols) == 1:
                    return r, cols[0], val

        # Colonnes
        for c in range(self.size):
            counts = {}
            for r in range(self.size):
                if grid[r][c] == 0 and (r, c) in possibilities:
                    for val in possibilities[(r, c)]:
                        if val not in counts: counts[val] = []
                        counts[val].append(r)
            for val, rows in counts.items():
                if len(rows) == 1:
                    return rows[0], c, val

        # Blocs
        for br in range(0, self.size, self.block_size):
            for bc in range(0, self.size, self.block_size):
                counts = {}
                for i in range(self.block_size):
                    for j in range(self.block_size):
                        r, c = br + i, bc + j
                        if grid[r][c] == 0 and (r, c) in possibilities:
                            for val in possibilities[(r, c)]:
                                if val not in counts: counts[val] = []
                                counts[val].append((r, c))
                for val, cells in counts.items():
                    if len(cells) == 1:
                        return cells[0][0], cells[0][1], val
        return None

    def propagate_fast(self, grid, rows, cols, blks):
        """
        Phase d'Intuition (Naked Singles + Hidden Singles) avec mise à jour incrémentale.
        Retourne True si contradiction détectée.
        """
        changed = True
        while changed:
            changed = False
            
            # 1. Calcul des possibilités actuelles
            possibilities = self.get_possible_values_map_fast(grid, rows, cols, blks)
            
            # Vérif contradiction
            for moves in possibilities.values():
                if len(moves) == 0: return True
            
            # 2. Naked Singles
            naked_found = False
            for (r, c), moves in list(possibilities.items()):
                if len(moves) == 1:
                    val = moves[0]
                    grid[r][c] = val
                    
                    # [HREI] Feedback positif : L'atome correspondant gagne en "confiance"
                    atom = self.engine.get_atom_by_label(f"VAL_{val}")
                    if atom: atom.valence += 0.05

                    # Mise à jour des masques
                    mask = 1 << val
                    rows[r] |= mask
                    cols[c] |= mask
                    b = (r // self.block_size) * self.block_size + (c // self.block_size)
                    blks[b] |= mask
                    
                    changed = True
                    naked_found = True
                    break 
            
            if naked_found: continue

            # 3. Hidden Singles (Si pas de Naked Singles trouvés)
            hidden = self.find_hidden_singles_fast(grid, possibilities)
            if hidden:
                r, c, val = hidden
                grid[r][c] = val
                
                # [HREI] Feedback positif : L'atome correspondant gagne en "confiance"
                atom = self.engine.get_atom_by_label(f"VAL_{val}")
                if atom: atom.valence += 0.1 # Plus fort pour un Hidden Single (plus dur à trouver)

                # Mise à jour des masques
                mask = 1 << val
                rows[r] |= mask
                cols[c] |= mask
                b = (r // self.block_size) * self.block_size + (c // self.block_size)
                blks[b] |= mask
                
                changed = True
                continue

        return False

    def propagate(self, grid):
        """Wrapper compatible ancien code (recalcule tout)."""
        rows, cols, blks = self.get_masks(grid)
        return self.propagate_fast(grid, rows, cols, blks)

    def find_most_constrained_cell_fast(self, grid, rows, cols, blks):
        """
        L'Attention Focalisée de HREI (Heuristique MRV) optimisée.
        """
        min_opts = self.size + 1
        best_cell = None
        best_moves = []

        # Parcours de la grille
        for r in range(self.size):
            for c in range(self.size):
                if grid[r][c] == 0:
                    moves = self.get_valid_moves_fast(r, c, rows, cols, blks)
                    
                    if len(moves) == 0:
                        return None, None, [] # Impasse
                    
                    if len(moves) < min_opts:
                        min_opts = len(moves)
                        best_cell = (r, c)
                        best_moves = moves
                        
                        if min_opts == 1: # Ne devrait pas arriver après propagate, mais sait-on jamais
                            return r, c, moves
        
        if best_cell is None:
            return None, None, None
            
        return best_cell[0], best_cell[1], best_moves

    def find_most_constrained_cell(self, grid):
        """Wrapper compatible ancien code."""
        rows, cols, blks = self.get_masks(grid)
        return self.find_most_constrained_cell_fast(grid, rows, cols, blks)

    # --- INTERFACE HREI CORE ---
    def simulator_interface(self, state, mode):
        """
        State est un tuple de tuples (grid immutable).
        """
        # Conversion tuple -> list pour manipulation locale
        current_grid = [list(row) for row in state]

        if mode == "GET_ACTIONS":
            # 1. Phase d'Intuition (Propagation)
            # On applique les coups évidents sur une copie locale
            contradiction = self.propagate(current_grid)
            if contradiction:
                return []

            # Si la grille est remplie par la propagation
            if sum(row.count(0) for row in current_grid) == 0:
                return ["FINALIZE"]

            # 2. Phase de Réflexion (Branching)
            r, c, moves = self.find_most_constrained_cell(current_grid)
            
            if r is None: return [] # Grille pleine ou bloquée
            
            actions = [f"{r}_{c}_{val}" for val in moves]
            random.shuffle(actions)
            return actions

        elif mode == "GET_CHANCE_OUTCOMES":
            return [] # Pas de hasard

        else: 
            # Simulation d'une action "R_C_VAL"
            if mode == "FINALIZE":
                 return (tuple(tuple(row) for row in current_grid), 100.0, "AGENT")

            parts = mode.split('_')
            r, c, val = int(parts[0]), int(parts[1]), int(parts[2])
            
            current_grid[r][c] = val
            
            # Conversion retour -> tuple
            next_state = tuple(tuple(row) for row in current_grid)
            
            # Récompense : +valence pour avoir posé un chiffre valide
            reward = self.completion_atom.valence
            
            return (next_state, reward, "AGENT")

    def evaluator_interface(self, state):
        """Évalue si la grille est 'belle' (cohérente)."""
        grid = [list(row) for row in state]
        
        # Check complétude
        filled = sum(row.count(0) for row in grid)
        if filled == 0:
            return 1000.0 # VICTOIRE
        
        # Si impasse (on ne peut plus jouer mais la grille n'est pas pleine)
        # Le simulateur renvoie [] donc le Core appelle l'évaluateur.
        return -500.0 # DEAD END

    def solve_loop(self, start_state):
        """
        Boucle de résolution utilisant l'heuristique MRV et la Résonance HREI.
        Optimisée avec propagation de contraintes bitmask.
        """
        # Conversion initiale
        start_grid = [list(row) for row in start_state]
        rows, cols, blks = self.get_masks(start_grid)
        
        # Stack: (grid, rows, cols, blks)
        # On stocke des copies indépendantes
        stack = [(start_grid, rows, cols, blks)]
        
        steps = 0
        max_steps = 1000000 # Augmenté pour 25x25 et cas complexes
        
        print(f"[HREI] Début de la résolution (Optimisée)...")
        
        while stack:
            # On utilise pop() pour DFS (plus mémoire-friendly que BFS pour Sudoku)
            current_grid, r_mask, c_mask, b_mask = stack.pop()
            steps += 1
            
            if steps > max_steps:
                print(f"[HREI] Abandon : Trop d'étapes ({steps}) - Complexité cognitive dépassée.")
                return False

            # Feedback visuel pour l'utilisateur sur les gros calculs
            if steps % 5000 == 0:
                filled = sum(len(row) - row.count(0) for row in current_grid)
                total = self.size * self.size
                print(f"[HREI] Step {steps}, Stack: {len(stack)}, Filled: {filled}/{total} (Exploration en cours...)")
            
            # 1. PROPAGATION (INTUITION)
            contradiction = self.propagate_fast(current_grid, r_mask, c_mask, b_mask)
            
            if contradiction:
                continue 
            
            # Vérif victoire
            if sum(row.count(0) for row in current_grid) == 0:
                print(f"[HREI] Solution trouvée après {steps} étapes de réflexion !")
                self.grid = current_grid
                return True
            
            # 2. ACTIONS (REFLEXION)
            # MRV : On choisit la case la plus contrainte pour réduire l'arbre
            r, c, moves = self.find_most_constrained_cell_fast(current_grid, r_mask, c_mask, b_mask)
            
            if r is None:
                continue # Impasse
            
            # Tri par résonance HREI (Atomes IA)
            # Au lieu de l'aléatoire pur, on utilise la valence des atomes
            # Les atomes qui ont été souvent validés (valence élevée) sont testés en premier.
            # Cela crée une heuristique dynamique basée sur l'expérience de la grille en cours.
            
            move_scores = []
            for val in moves:
                atom = self.engine.get_atom_by_label(f"VAL_{val}")
                # Valence + petit bruit pour casser les égalités et éviter les boucles infinies
                score = (atom.valence if atom else 0) + random.uniform(0, 0.05)
                move_scores.append((score, val))
            
            # Tri décroissant : On tente les atomes "dominants" d'abord
            move_scores.sort(key=lambda x: x[0], reverse=True)
            sorted_moves = [m[1] for m in move_scores]
            
            # On empile les coups (LIFO : le dernier ajouté sera traité en premier)
            # Donc on doit ajouter les MOINS bons en premier pour que les MEILLEURS soient pop() en premier
            # C'est l'inverse de l'ordre d'itération habituel
            for val in reversed(sorted_moves):
                # Création des nouvelles structures (Deep Copy)
                new_grid = [row[:] for row in current_grid]
                new_r = r_mask[:]
                new_c = c_mask[:]
                new_b = b_mask[:]
                
                # Application du coup
                new_grid[r][c] = val
                mask = 1 << val
                new_r[r] |= mask
                new_c[c] |= mask
                b = (r // self.block_size) * self.block_size + (c // self.block_size)
                new_b[b] |= mask
                
                stack.append((new_grid, new_r, new_c, new_b))
                
        return False

    def generate_and_solve(self):
        print(f"=== HREI SUDOKU {self.size}x{self.size} GENERATOR & SOLVER ===")
        print("Initialisation du vide quantique (Grille vierge)...")
        
        # État initial vide
        empty_state = tuple(tuple([0]*self.size) for _ in range(self.size))
        
        print("Génération d'une grille valide par Résonance...")
        t0 = time.time()
        
        # Seed diagonale pour casser la symétrie (accélère grandement la génération)
        temp_grid = [[0]*self.size for _ in range(self.size)]
        for i in range(0, self.size, self.block_size):
            nums = list(range(1, self.size + 1))
            random.shuffle(nums)
            idx = 0
            for r in range(i, i + self.block_size):
                for c in range(i, i + self.block_size):
                    temp_grid[r][c] = nums[idx]
                    idx += 1
        
        seeded_state = tuple(tuple(row) for row in temp_grid)
        self.grid = temp_grid
        print("Seed (Diagonale remplie) :")
        self.print_grid()

        # Génération complète
        success = self.solve_loop(seeded_state)
        
        if success:
            t1 = time.time()
            print(f"\nGrille Complète Générée en {t1-t0:.2f}s !")
            self.print_grid()
            
            # Création du puzzle (On enlève ~40-50% des chiffres)
            print("\nCréation des trous (Entropie)...")
            puzzle_grid = [row[:] for row in self.grid]
            total_cells = self.size * self.size
            to_remove = int(total_cells * 0.5)
            
            attempts = 0
            while to_remove > 0 and attempts < total_cells * 2:
                r, c = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
                if puzzle_grid[r][c] != 0:
                    puzzle_grid[r][c] = 0
                    to_remove -= 1
                attempts += 1
            
            self.grid = puzzle_grid
            print("Puzzle à Résoudre :")
            self.print_grid()
            
            print("\nRésolution du Puzzle par HREI...")
            t2 = time.time()
            puzzle_state = tuple(tuple(row) for row in self.grid)
            solved = self.solve_loop(puzzle_state)
            t3 = time.time()
            
            if solved:
                print(f"PUZZLE RÉSOLU EN {t3-t2:.2f}s !")
                self.print_grid()
            else:
                print("HREI n'a pas trouvé la solution (Impasse complexe).")

if __name__ == "__main__":
    # Par défaut, on lance une démo 9x9 car c'est standard
    # Pour essayer 25x25, changer la taille ici : SudokuHREI(25)
    print("Choisissez la taille du Sudoku :")
    print("1. 9x9 (Standard)")
    print("2. 16x16 (Expert)")
    print("3. 25x25 (Divin - Peut être long)")
    
    # Simple input avec timeout ou défaut si non interactif
    # Comme on est dans un environnement non-interactif souvent, on met un défaut
    try:
        # On simule un choix par défaut si pas d'input (pour les tests auto)
        # Mais ici c'est un script demo, donc on peut hardcoder ou prendre un arg
        if len(sys.argv) > 1:
            choice = sys.argv[1]
        else:
            choice = "1" # Default
    except:
        choice = "1"

    if choice == "2":
        size = 16
    elif choice == "3":
        size = 25
    else:
        size = 9

    game = SudokuHREI(size)
    game.generate_and_solve()
