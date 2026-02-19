import sys
import os
import random
import time

# Ajout du chemin racine pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

class TicTacToeHREI:
    def __init__(self):
        self.engine = HREIEngine()
        self.board = [" " for _ in range(9)]
        self.hrei_mark = "O"
        self.minimax_mark = "X"
        self.setup_hrei()

    def setup_hrei(self):
        # Atomes de victoire et défaite
        self.victoire = CognitiveAtom("VICTOIRE", valence=1.0)
        self.defaite = CognitiveAtom("DEFAITE", valence=-1.0)
        self.engine.add_atom(self.victoire)
        self.engine.add_atom(self.defaite)
        
        # Atomes pour chaque case (0-8)
        self.cell_atoms = []
        for i in range(9):
            atom = CognitiveAtom(f"Case_{i}", valence=0.1)
            self.engine.add_atom(atom)
            self.cell_atoms.append(atom)

    def print_board(self):
        print("\n")
        for i in range(0, 9, 3):
            print(f" {self.board[i]} | {self.board[i+1]} | {self.board[i+2]} ")
            if i < 6:
                print("-----------")
        print("\n")

    def check_winner(self, board):
        win_coords = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for a, b, c in win_coords:
            if board[a] == board[b] == board[c] != " ":
                return board[a]
        if " " not in board:
            return "Draw"
        return None

    # --- LOGIQUE HREI ---
    def simulator_interface(self, state, mode):
        """Interface pour le moteur HREI."""
        # state est la liste board
        if mode == "GET_ACTIONS":
            return [i for i, v in enumerate(state) if v == " "]
        
        # Mode Simulation
        # action est l'index du coup
        move = mode
        next_board = list(state)
        # On doit savoir à qui c'est le tour.
        x_count = state.count("X")
        o_count = state.count("O")
        
        # X commence toujours
        if x_count == o_count:
            current_mark = "X" # C'est à X (Minimax/Opponent) de jouer
            next_turn_type = "AGENT" # Après X, c'est à O (HREI)
        else:
            current_mark = "O" # C'est à O (HREI/Agent) de jouer
            next_turn_type = "OPPONENT" # Après O, c'est à X
        
        next_board[move] = current_mark
        
        # Récompense immédiate ?
        winner = self.check_winner(next_board)
        reward = 0.0
        
        if winner == self.hrei_mark: # HREI gagne
            reward = self.victoire.valence * 100
            next_turn = "TERMINAL"
        elif winner == self.minimax_mark: # HREI perd
            reward = self.defaite.valence * 100
            next_turn = "TERMINAL"
        elif " " not in next_board: # Match nul
            reward = 0.0
            next_turn = "TERMINAL"
        else:
            next_turn = next_turn_type
            
        return next_board, reward, next_turn

    def evaluator_interface(self, state):
        """Évaluation statique de l'état (Valence)."""
        winner = self.check_winner(state)
        if winner == self.hrei_mark: return self.victoire.valence * 100
        if winner == self.minimax_mark: return self.defaite.valence * 100
        if winner == "Draw": return 0.0
        
        # Heuristique légère pour guider la recherche non-terminale
        valence = 0.0
        
        # Centre
        if state[4] == self.hrei_mark: valence += 0.5
        elif state[4] == self.minimax_mark: valence -= 0.5
        
        # Coins
        for i in [0, 2, 6, 8]:
            if state[i] == self.hrei_mark: valence += 0.2
            elif state[i] == self.minimax_mark: valence -= 0.2
            
        return valence

    def hrei_move(self):
        print("[HREI] Analyse par résonance cognitive...")
        best_move = -1
        max_resonance = -float('inf')
        
        available_moves = [i for i, v in enumerate(self.board) if v == " "]
        cache = {}
        
        for move in available_moves:
            # Simulation du premier coup (HREI joue)
            next_board = list(self.board)
            next_board[move] = self.hrei_mark
            
            # Si victoire immédiate, on prend direct
            if self.check_winner(next_board) == self.hrei_mark:
                best_move = move
                max_resonance = 999.0
                break
                
            # Sinon, on lance la recherche hybride pour voir la réponse de l'adversaire
            resonance = self.engine.hybrid_resonance_search(
                initial_state=next_board,
                simulator_func=self.simulator_interface,
                evaluator_func=self.evaluator_interface,
                depth=4, # Profondeur suffisante pour TicTacToe
                precise_threshold=2,
                turn="OPPONENT", # C'est à l'adversaire de jouer ensuite
                cache=cache
            )
            
            print(f"  Option {move}: Résonance {resonance:.2f}")
            
            if resonance > max_resonance:
                max_resonance = resonance
                best_move = move
        
        self.board[best_move] = self.hrei_mark
        print(f"  > HREI (MiniMOX) choisit {best_move} (Valence prédite: {max_resonance:.2f})")

    # --- LOGIQUE MINIMAX ---
    def minimax(self, board, depth, is_maximizing):
        winner = self.check_winner(board)
        if winner == self.minimax_mark: return 10 - depth
        if winner == self.hrei_mark: return depth - 10
        if winner == "Draw": return 0

        if is_maximizing:
            best_score = -float('inf')
            for i in range(9):
                if board[i] == " ":
                    board[i] = self.minimax_mark
                    score = self.minimax(board, depth + 1, False)
                    board[i] = " "
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(9):
                if board[i] == " ":
                    board[i] = self.hrei_mark
                    score = self.minimax(board, depth + 1, True)
                    board[i] = " "
                    best_score = min(score, best_score)
            return best_score

    def minimax_move(self):
        print("[MINIMAX] Calcul de l'arbre de décision...")
        best_score = -float('inf')
        best_move = -1
        for i in range(9):
            if self.board[i] == " ":
                self.board[i] = self.minimax_mark
                score = self.minimax(self.board, 0, False)
                self.board[i] = " "
                if score > best_score:
                    best_score = score
                    best_move = i
        self.board[best_move] = self.minimax_mark
        print(f"  > Minimax choisit {best_move}")

    def play_duel(self):
        print("\n" + "="*40)
        print("      DUEL HREI (MiniMOX) vs MINIMAX")
        print("="*40)
        print("HREI : O")
        print("Minimax : X")
        
        turn = "X" # Minimax commence
        
        while True:
            self.print_board()
            winner = self.check_winner(self.board)
            if winner:
                if winner == "Draw": 
                    print("--- MATCH NUL ---")
                    print("L'équilibre est maintenu entre la logique et la résonance.")
                else:
                    gagnant = "HREI (MiniMOX)" if winner == "O" else "Minimax"
                    print(f"--- VICTOIRE : {gagnant} ---")
                break
            
            if turn == "X":
                self.minimax_move()
                turn = "O"
            else:
                time.sleep(1) # Pour la lisibilité
                self.hrei_move()
                turn = "X"

    def play_human(self):
        print("--- BIENVENUE DANS LE MORPION HREI (MiniMOX) ---")
        self.minimax_mark = "X"
        self.hrei_mark = "O"
        print("Vous êtes les 'X', HREI est les 'O'.")
        
        while True:
            self.print_board()
            winner = self.check_winner(self.board)
            if winner:
                if winner == "Draw": print("Match nul !"); break
                print(f"Félicitations ! {'Vous' if winner == 'X' else 'HREI'} gagne !"); break
            
            try:
                move = int(input("Votre coup (0-8) : "))
                if self.board[move] != " ": print("Case occupée !"); continue
                self.board[move] = "X"
            except: print("Coup invalide !"); continue
            
            if self.check_winner(self.board): continue
            self.hrei_move()

if __name__ == "__main__":
    game = TicTacToeHREI()
    print("Choisissez le mode :")
    print("1. Humain vs HREI")
    print("2. Minimax vs HREI (Duel IA)")
    
    choice = input("> ")
    if choice == "2":
        game.play_duel()
    else:
        game.play_human()