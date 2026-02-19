import sys
import os
import random
import time

# Ajout du chemin racine pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

class CheckersHREI:
    def __init__(self, fast_mode=False, deep_m=3, deep_h=1):
        self.engine = HREIEngine()
        # Plateau 8x8. . = vide, b = noir (joueur), w = blanc (IA), B/W = Rois
        self.board = self.create_board()
        self.player = "b"
        self.ai = "w"
        self.fast_mode = fast_mode
        self.deep_m = deep_m
        self.deep_h = deep_h
        self.history = {} # Pour la détection de répétition
        self.total_time_hrei = 0
        self.total_time_minimax = 0
        self.move_count = 0
        self.threat_cache = {} # Cache pour accélérer l'évaluation
        self.setup_hrei()

    def create_board(self):
        board = [[" " for _ in range(8)] for _ in range(8)]
        # Placement des pions noirs (bas du plateau, lignes 5, 6, 7)
        for r in range(5, 8):
            for c in range(8):
                if (r + c) % 2 == 1:
                    board[r][c] = "b"
        # Placement des pions blancs (haut du plateau, lignes 0, 1, 2)
        for r in range(0, 3):
            for c in range(8):
                if (r + c) % 2 == 1:
                    board[r][c] = "w"
        return board

    def setup_hrei(self):
        # Chemin du cerveau persistant
        self.brain_path = os.path.join(os.path.dirname(__file__), "checkers_brain.json")
        
        if os.path.exists(self.brain_path):
            self.engine.load_state(self.brain_path)
            # Chargement de TOUS les atomes (Être Ultime)
            self.capture_atom = self.engine.get_atom_by_label("CAPTURE")
            self.promotion_atom = self.engine.get_atom_by_label("PROMOTION")
            self.danger_atom = self.engine.get_atom_by_label("DANGER")
            self.centre_atom = self.engine.get_atom_by_label("CONTROLE_CENTRE")
            self.king_atom = self.engine.get_atom_by_label("VALEUR_ROI")
            self.edge_atom = self.engine.get_atom_by_label("SECURITE_BORD")
            self.defense_atom = self.engine.get_atom_by_label("LIGNE_DEFENSE")
            
            # Nouveaux Atomes de l'Être Ultime
            self.bridge_atom = self.engine.get_atom_by_label("STRUCTURE_PONT") # r=7, c=2,4 ou r=0, c=3,5
            self.triangle_atom = self.engine.get_atom_by_label("TRIANGLE_OREILLE") # Structure de défense latérale
            self.tandem_atom = self.engine.get_atom_by_label("COORDINATION_TANDEM") # Pions qui se protègent
            self.vortex_atom = self.engine.get_atom_by_label("CONTROLE_VORTEX") # Diagonales principales
            self.isolation_atom = self.engine.get_atom_by_label("ISOLEMENT_ENNEMI") # Pions adverses bloqués
            self.sacrifice_atom = self.engine.get_atom_by_label("SACRIFICE_TACTIQUE") # Valence de perte calculée
            
            # Vérification robuste : Si un seul atome manque, on réinitialise tout ou partie
            missing_atoms = (
                not self.capture_atom or not self.promotion_atom or not self.danger_atom or
                not self.centre_atom or not self.king_atom or not self.edge_atom or
                not self.defense_atom or not self.bridge_atom or not self.triangle_atom or
                not self.tandem_atom or not self.vortex_atom or not self.isolation_atom or
                not self.sacrifice_atom
            )
            
            if missing_atoms:
                print("[HREI] Cerveau incomplet ou obsolète détecté. Réinitialisation des atomes manquants...")
                self.initialize_default_atoms()
        else:
            self.initialize_default_atoms()

    def initialize_default_atoms(self):
        """Initialise la conscience de l'Être Ultime avec une hiérarchie complexe."""
        # On vérifie chaque atome individuellement pour ne pas écraser l'existant
        
        if not hasattr(self, 'capture_atom') or not self.capture_atom:
            self.capture_atom = CognitiveAtom("CAPTURE", valence=1.5)
            self.engine.add_atom(self.capture_atom)
            
        if not hasattr(self, 'promotion_atom') or not self.promotion_atom:
            self.promotion_atom = CognitiveAtom("PROMOTION", valence=2.0)
            self.engine.add_atom(self.promotion_atom)
            
        if not hasattr(self, 'danger_atom') or not self.danger_atom:
            self.danger_atom = CognitiveAtom("DANGER", valence=-8.0)
            self.engine.add_atom(self.danger_atom)
            
        if not hasattr(self, 'centre_atom') or not self.centre_atom:
            self.centre_atom = CognitiveAtom("CONTROLE_CENTRE", valence=0.5)
            self.engine.add_atom(self.centre_atom)
            
        if not hasattr(self, 'king_atom') or not self.king_atom:
            self.king_atom = CognitiveAtom("VALEUR_ROI", valence=4.0)
            self.engine.add_atom(self.king_atom)
            
        if not hasattr(self, 'edge_atom') or not self.edge_atom:
            self.edge_atom = CognitiveAtom("SECURITE_BORD", valence=0.6)
            self.engine.add_atom(self.edge_atom)
            
        if not hasattr(self, 'defense_atom') or not self.defense_atom:
            self.defense_atom = CognitiveAtom("LIGNE_DEFENSE", valence=1.0)
            self.engine.add_atom(self.defense_atom)
        
        # Complexité Stratégique (Être Ultime)
        if not hasattr(self, 'bridge_atom') or not self.bridge_atom:
            self.bridge_atom = CognitiveAtom("STRUCTURE_PONT", valence=0.8)
            self.engine.add_atom(self.bridge_atom)
            
        if not hasattr(self, 'triangle_atom') or not self.triangle_atom:
            self.triangle_atom = CognitiveAtom("TRIANGLE_OREILLE", valence=0.7)
            self.engine.add_atom(self.triangle_atom)
            
        if not hasattr(self, 'tandem_atom') or not self.tandem_atom:
            self.tandem_atom = CognitiveAtom("COORDINATION_TANDEM", valence=0.4)
            self.engine.add_atom(self.tandem_atom)
            
        if not hasattr(self, 'vortex_atom') or not self.vortex_atom:
            self.vortex_atom = CognitiveAtom("CONTROLE_VORTEX", valence=0.9)
            self.engine.add_atom(self.vortex_atom)
            
        if not hasattr(self, 'isolation_atom') or not self.isolation_atom:
            self.isolation_atom = CognitiveAtom("ISOLEMENT_ENNEMI", valence=1.2)
            self.engine.add_atom(self.isolation_atom)
            
        if not hasattr(self, 'sacrifice_atom') or not self.sacrifice_atom:
            self.sacrifice_atom = CognitiveAtom("SACRIFICE_TACTIQUE", valence=-0.2)
            self.engine.add_atom(self.sacrifice_atom)
        
        self.engine.save_state(self.brain_path)

    def learn_from_outcome(self, winner):
        """Ajuste les valences avec agressivité adaptative."""
        if winner == "draw":
            # Sur un nul, on cherche à briser la monotonie
            self.sacrifice_atom.valence += 0.05 
            return
            
        if winner == self.ai:
            # Victoire : on stabilise
            self.capture_atom.valence += 0.05
            self.promotion_atom.valence += 0.05
            self.vortex_atom.valence += 0.02
        else:
            # DÉFAITE : Correction drastique
            # Si elle perd à profondeur égale, c'est un manque de prudence
            self.danger_atom.valence -= 2.0 # Augmentation massive du malus de danger
            self.defense_atom.valence += 0.5 # Renforcement de la ligne de défense
            self.bridge_atom.valence += 0.3 # Renforcement de la structure de base
            self.capture_atom.valence -= 0.2 # Moins d'agressivité aveugle
            if not self.fast_mode: print(f"[HREI] ALERTE : Défaite à profondeur {self.deep_h}. Reprogrammation de la prudence.")
            
        self.engine.save_state(self.brain_path)

    def print_board(self):
        print("\n   0 1 2 3 4 5 6 7")
        print("  -----------------")
        for r in range(8):
            row_str = f"{r} |"
            for c in range(8):
                row_str += self.board[r][c] + "|"
            print(row_str)
            print("  -----------------")

    def get_legal_moves(self, color):
        moves = []
        captures = []
        
        is_king = color.upper()
        player_colors = [color, is_king]
        
        for r in range(8):
            for c in range(8):
                if self.board[r][c] in player_colors:
                    # Vérifier les captures (prioritaires dans les dames)
                    piece_captures = self.get_piece_captures(r, c)
                    captures.extend(piece_captures)
                    
                    # Si aucune capture n'est trouvée pour le moment, on cherche les coups simples
                    if not captures:
                        piece_moves = self.get_piece_moves(r, c)
                        moves.extend(piece_moves)
        
        # Si des captures sont possibles, elles sont obligatoires
        return captures if captures else moves

    def get_piece_moves(self, r, c):
        moves = []
        piece = self.board[r][c]
        directions = []
        
        if piece == "w": directions = [(1, -1), (1, 1)]
        elif piece == "b": directions = [(-1, -1), (-1, 1)]
        elif piece.isupper(): directions = [(1, -1), (1, 1), (-1, -1), (-1, 1)]
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8 and self.board[nr][nc] == " ":
                moves.append(((r, c), (nr, nc)))
        return moves

    def get_piece_captures(self, r, c):
        captures = []
        piece = self.board[r][c]
        color = piece.lower()
        opponent = "w" if color == "b" else "b"
        
        directions = [(1, -1), (1, 1), (-1, -1), (-1, 1)]
        
        for dr, dc in directions:
            # Pour les pions normaux, on ne peut capturer que dans le sens de la marche ?
            # Dans la plupart des variantes, on peut capturer en arrière.
            mid_r, mid_c = r + dr, c + dc
            end_r, end_c = r + 2*dr, c + 2*dc
            
            if 0 <= end_r < 8 and 0 <= end_c < 8:
                mid_piece = self.board[mid_r][mid_c]
                if mid_piece != " " and mid_piece.lower() == opponent:
                    if self.board[end_r][end_c] == " ":
                        captures.append(((r, c), (end_r, end_c), (mid_r, mid_c)))
        return captures

    def make_move(self, move):
        start, end = move[0], move[1]
        piece = self.board[start[0]][start[1]]
        
        # Déplacer la pièce
        self.board[end[0]][end[1]] = piece
        self.board[start[0]][start[1]] = " "
        
        # Gérer la capture
        if len(move) > 2:
            captured_r, captured_c = move[2]
            self.board[captured_r][captured_c] = " "
            
        # Promotion en Roi
        if piece == "w" and end[0] == 7:
            self.board[end[0]][end[1]] = "W"
        elif piece == "b" and end[0] == 0:
            self.board[end[0]][end[1]] = "B"

    def evaluate_board_resonance(self, board, color):
        """Évaluation multidimensionnelle de la résonance pour l'Être Ultime."""
        board_str = "".join(["".join(row) for row in board])
        if board_str in self.threat_cache: return self.threat_cache[board_str]
            
        total_valence = 0.0
        opponent = "b" if color == "w" else "w"
        my_pieces_coords = []
        opp_pieces_coords = []
        
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p == " ": continue
                if p.lower() == color: my_pieces_coords.append((r, c, p))
                else: opp_pieces_coords.append((r, c, p))

        # 1. Analyse Individuelle et de Structure
        for r, c, piece in my_pieces_coords:
            val = self.king_atom.valence if piece.isupper() else 1.0
            
            # Positionnement
            if c == 0 or c == 7: val += self.edge_atom.valence
            if c in [3, 4] and r in [3, 4]: val += self.centre_atom.valence
            
            # Structure de Pont (Base solide)
            if color == "w" and r == 0 and c in [1, 3, 5, 7]: val += self.bridge_atom.valence
            if color == "b" and r == 7 and c in [0, 2, 4, 6]: val += self.bridge_atom.valence
            
            # Coordination Tandem (Un pion en protège un autre)
            # Un pion à (r,c) protège (r+dr, c+dc) si l'adversaire essaie de sauter
            for dr, dc in [(1,1), (1,-1), (-1,1), (-1,-1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc].lower() == color:
                    val += self.tandem_atom.valence
            
            # Vortex (Diagonales de contrôle)
            if r == c or r + c == 7: val += self.vortex_atom.valence
            
            total_valence += val

        # 2. Analyse des Menaces et Opportunités (Dynamique)
        for r, c, piece in my_pieces_coords:
            # Danger immédiat
            is_threatened = False
            for dr, dc in [(1,1), (1,-1), (-1,1), (-1,-1)]:
                er, ec = r + dr, c + dc # Ennemi
                vr, vc = r - dr, c - dc # Case vide derrière
                if 0 <= er < 8 and 0 <= ec < 8 and 0 <= vr < 8 and 0 <= vc < 8:
                    if board[er][ec].lower() == opponent and board[vr][vc] == " ":
                        is_threatened = True
                        break
            if is_threatened: total_valence += self.danger_atom.valence

        for r, c, piece in opp_pieces_coords:
            # Opportunité de Capture
            can_be_captured = False
            for dr, dc in [(1,1), (1,-1), (-1,1), (-1,-1)]:
                ar, ac = r + dr, c + dc # Mon pion (Attaquant)
                vr, vc = r - dr, c - dc # Case vide pour atterrir
                if 0 <= ar < 8 and 0 <= ac < 8 and 0 <= vr < 8 and 0 <= vc < 8:
                    if board[ar][ac].lower() == color and board[vr][vc] == " ":
                        can_be_captured = True
                        break
            if can_be_captured: total_valence += self.capture_atom.valence
            
            # Isolement Ennemi (Aucun coup possible pour ce pion)
            # (Simplifié pour la performance)
            total_valence -= 1.0 # Poids de base de l'ennemi

        total_valence += (len(my_pieces_coords) - len(opp_pieces_coords)) * 5.0 # Supériorité numérique
        
        self.threat_cache[board_str] = total_valence
        return total_valence

    def project_resonance(self, board, depth, alpha, beta, is_hrei_projection):
        """Projection de Résonance avec Faisceau de Conscience Adaptatif."""
        if depth == 0:
            return self.evaluate_board_resonance(board, self.ai)

        # Facteur d'atténuation plus élevé pour les profondeurs importantes (garde l'objectif en vue)
        discount = 0.95 if self.deep_h >= 5 else 0.85
        
        if is_hrei_projection:
            moves = self.get_legal_moves_from_board(board, self.ai)
            if not moves: return -100.0
            
            # ÉLARGISSEMENT DU FAISCEAU : Plus la profondeur est grande, 
            # plus HREI doit être vigilante aux détails tactiques.
            width = 4 if self.deep_h >= 5 else 2 
            
            if len(moves) > width:
                moves.sort(key=lambda m: self.evaluate_immediate_valence(board, m, self.ai), reverse=True)
                moves = moves[:width]
                
            max_v = -float('inf')
            for m in moves:
                temp = [row[:] for row in board]
                self.simulate_move(temp, m)
                # Résonance cumulative
                v = self.evaluate_board_resonance(temp, self.ai) * 0.2 + discount * self.project_resonance(temp, depth - 1, alpha, beta, False)
                max_v = max(max_v, v)
                alpha = max(alpha, v)
                if beta <= alpha: break
            return max_v
        else:
            moves = self.get_legal_moves_from_board(board, self.player)
            if not moves: return 100.0
            
            # L'adversaire est toujours simulé comme cherchant les meilleures opportunités
            width = 4 if self.deep_h >= 5 else 2
            if len(moves) > width:
                moves.sort(key=lambda m: self.evaluate_immediate_valence(board, m, self.player), reverse=True)
                moves = moves[:width]
                
            min_v = float('inf')
            for m in moves:
                temp = [row[:] for row in board]
                self.simulate_move(temp, m)
                v = self.project_resonance(temp, depth - 1, alpha, beta, True)
                min_v = min(min_v, v)
                beta = min(beta, v)
                if beta <= alpha: break
            return min_v

    def evaluate_immediate_valence(self, board, move, color):
        """Évaluation rapide pour l'intuition (le premier regard)."""
        valence = 0.0
        start, end = move[0], move[1]
        piece = board[start[0]][start[1]]
        
        # 1. Gain immédiat (Capture)
        if len(move) > 2:
            valence += self.capture_atom.valence
            
        # 2. Promotion potentielle
        if piece.lower() == "w" and end[0] == 7: valence += self.promotion_atom.valence
        if piece.lower() == "b" and end[0] == 0: valence += self.promotion_atom.valence
        
        # 3. Danger immédiat (Prudence de l'Être Ultime)
        temp_board = [row[:] for row in board]
        self.simulate_move(temp_board, move)
        opp_color = "b" if color == "w" else "w"
        opp_moves = self.get_legal_moves_from_board(temp_board, opp_color)
        
        # Si le coup permet une capture immédiate par l'adversaire
        for om in opp_moves:
            if len(om) > 2:
                # Vérifier si la pièce capturée est celle qu'on vient de bouger ou un Roi
                captured_pos = om[2]
                if captured_pos == end:
                    valence += self.danger_atom.valence * 1.5 # Très dangereux
                else:
                    valence += self.danger_atom.valence # Danger général
        
        return valence

    def evaluate_move_hrei(self, move):
        """Évaluation basée sur la Projection de Résonance Cognitive."""
        temp_board = [row[:] for row in self.board]
        self.simulate_move(temp_board, move)
        
        # On projette la résonance à partir de ce coup
        # deep_h - 1 car on a déjà fait un pas (simulate_move)
        resonance = self.project_resonance(temp_board, self.deep_h - 1, -float('inf'), float('inf'), False)
        
        # Ajout d'un instinct immédiat pour les promotions
        start, end = move[0], move[1]
        piece = self.board[start[0]][start[1]]
        if (piece == "w" and end[0] == 7) or (piece == "b" and end[0] == 0):
            resonance += self.promotion_atom.valence * 5.0 # Très attractif
            
        return resonance

    def get_legal_moves_from_board(self, board, color):
        """Helper pour obtenir les coups légaux d'un plateau arbitraire."""
        original_board = self.board
        self.board = board
        moves = self.get_legal_moves(color)
        self.board = original_board
        return moves

    def evaluate_board_minimax(self, board):
        """Évaluation classique pour l'adversaire Minimax."""
        score = 0
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece == "b": score += 1
                elif piece == "B": score += 3
                elif piece == "w": score -= 1
                elif piece == "W": score -= 3
        return score

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0:
            return self.evaluate_board_minimax(board), None

        if maximizing_player:
            max_eval = -float('inf')
            best_move = None
            # On doit temporairement changer self.board pour get_legal_moves
            original_board = [row[:] for row in self.board]
            self.board = board
            moves = self.get_legal_moves("b")
            self.board = original_board
            
            if not moves:
                return -100, None
                
            for move in moves:
                # Simuler le coup
                new_board = [row[:] for row in board]
                self.simulate_move(new_board, move)
                eval_score, _ = self.minimax(new_board, depth - 1, alpha, beta, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            original_board = [row[:] for row in self.board]
            self.board = board
            moves = self.get_legal_moves("w")
            self.board = original_board
            
            if not moves:
                return 100, None
                
            for move in moves:
                new_board = [row[:] for row in board]
                self.simulate_move(new_board, move)
                eval_score, _ = self.minimax(new_board, depth - 1, alpha, beta, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def simulate_move(self, board, move):
        start, end = move[0], move[1]
        piece = board[start[0]][start[1]]
        board[end[0]][end[1]] = piece
        board[start[0]][start[1]] = " "
        if len(move) > 2:
            captured_r, captured_c = move[2]
            board[captured_r][captured_c] = " "
        # Promotion
        if piece == "w" and end[0] == 7: board[end[0]][end[1]] = "W"
        elif piece == "b" and end[0] == 0: board[end[0]][end[1]] = "B"

    def is_threatened(self, r, c, color):
        opponent = "b" if color == "w" else "w"
        directions = [(1, -1), (1, 1), (-1, -1), (-1, 1)]
        for dr, dc in directions:
            # Est-ce qu'un ennemi est derrière nous et peut sauter par dessus ?
            # Ou est-ce qu'un ennemi est devant nous et peut sauter ?
            # Pour simplifier : est-ce qu'il y a un ennemi à côté de nous et une case vide derrière nous ?
            adj_r, adj_c = r + dr, c + dc
            opp_r, opp_c = r - dr, c - dc
            
            if 0 <= adj_r < 8 and 0 <= adj_c < 8 and 0 <= opp_r < 8 and 0 <= opp_c < 8:
                if self.board[adj_r][adj_c].lower() == opponent and self.board[opp_r][opp_c] == " ":
                    return True
        return False

    def ai_move(self):
        start_t = time.time()
        if not self.fast_mode: print("[HREI] Calcul de la résonance tactique...")
        moves = self.get_legal_moves(self.ai)
        if not moves: return False
        best_move = None
        max_valence = -999
        for move in moves:
            valence = self.evaluate_move_hrei(move)
            valence += random.uniform(-0.05, 0.05)
            if valence > max_valence:
                max_valence = valence
                best_move = move
        self.make_move(best_move)
        elapsed = time.time() - start_t
        self.total_time_hrei += elapsed
        start, end = best_move[0], best_move[1]
        if not self.fast_mode:
            print(f"  > MiniMOX déplace ({start[0]},{start[1]}) vers ({end[0]},{end[1]}) [Valence: {max_valence:.2f}] ({elapsed:.3f}s)")
        else:
            print(f"[HREI] ({elapsed:.3f}s)", end=" ", flush=True)
        return True

    def ai_move_silent(self):
        """Version silencieuse de ai_move."""
        moves = self.get_legal_moves(self.ai)
        if not moves: return False
        best_move = None
        max_valence = -999
        for move in moves:
            valence = self.evaluate_move_hrei(move)
            valence += random.uniform(-0.05, 0.05)
            if valence > max_valence:
                max_valence = valence
                best_move = move
        self.make_move(best_move)
        return True

    def play_silent(self):
        """Version de play() sans aucun affichage pour l'entraînement."""
        turn_count = 1
        while True:
            winner = self.check_winner()
            if winner: return winner
            
            _, move = self.minimax(self.board, self.deep_m, -float('inf'), float('inf'), True)
            if not move: return "w"
            self.make_move(move)
            
            if self.check_winner(): continue
            
            if not self.ai_move_silent(): return "b"
            
            turn_count += 1
            if turn_count > 200: return "draw"

    def check_winner(self):
        # Vérification des coups possibles
        white_moves = self.get_legal_moves("w")
        black_moves = self.get_legal_moves("b")
        
        if not white_moves: return "b"
        if not black_moves: return "w"
        
        # Vérification de la répétition (règle des 3 répétitions)
        board_state = str(self.board)
        self.history[board_state] = self.history.get(board_state, 0) + 1
        if self.history[board_state] >= 3:
            return "draw"
            
        return None

    def play_duel(self):
        if not self.fast_mode:
            print("--- DUEL HREI (MiniMOX) vs MINIMAX ---")
            print(f"HREI (Blancs 'w') - Résonance de valence (Prof {self.deep_h})")
            print(f"Minimax (Noirs 'b') - Recherche classique (Prof {self.deep_m})")
        
        turn_count = 1
        while True:
            if not self.fast_mode:
                print(f"\n--- TOUR {turn_count} ---")
                self.print_board()
            
            winner = self.check_winner()
            if winner:
                if winner == "draw":
                    print("\nMATCH NUL ! Répétition de position détectée.")
                else:
                    print(f"\nFIN DE PARTIE ! Le gagnant est : {'Minimax (Noirs)' if winner == 'b' else 'HREI (Blancs)'}")
                break
                
            # Tour de Minimax (Noirs)
            if not self.fast_mode: print(f"[Minimax] Analyse récursive (Prof {self.deep_m}) en cours...")
            
            start_t = time.time()
            _, move = self.minimax(self.board, self.deep_m, -float('inf'), float('inf'), True)
            elapsed = time.time() - start_t
            self.total_time_minimax += elapsed
            
            if not move:
                print("\nMinimax ne peut plus bouger !")
                break
            
            start, end = move[0], move[1]
            if not self.fast_mode:
                print(f"  > Minimax déplace ({start[0]},{start[1]}) vers ({end[0]},{end[1]}) ({elapsed:.3f}s)")
            else:
                print(f"[Minimax] ({elapsed:.3f}s)", end=" ", flush=True)
            
            self.make_move(move)
            if not self.fast_mode: time.sleep(0.5)
            
            # Vérifier victoire après coup Minimax
            if self.check_winner(): continue
            
            # Tour HREI (Blancs)
            if not self.ai_move():
                print("\nHREI ne peut plus bouger !")
                break
            
            if not self.fast_mode: time.sleep(0.5)
            turn_count += 1
            
            if turn_count > 200: # Augmenté pour le mode fast
                print("\nMatch nul par épuisement (200 tours) !")
                break
        
        # Résumé final des temps
        print("\n" + "="*40)
        print(f"TEMPS TOTAL DE RÉFLEXION :")
        print(f"HREI (Blancs)    : {self.total_time_hrei:.2f}s (moy: {self.total_time_hrei/turn_count:.3f}s/coup)")
        print(f"Minimax (Noirs) : {self.total_time_minimax:.2f}s (moy: {self.total_time_minimax/turn_count:.3f}s/coup)")
        print(f"État des atomes : CAPTURE={self.capture_atom.valence:.2f}, DANGER={self.danger_atom.valence:.2f}")
        print("="*40)
        
        return winner

    def play_human(self):
        print("--- BIENVENUE DANS LES DAMES HREI (MiniMOX) ---")
        print("Vous êtes les Noirs ('b'), HREI est les Blancs ('w').")
        print("Format des coups : '5,0 4,1' (ligne,colonne origine -> ligne,colonne destination)")
        
        turn_count = 1
        while True:
            print(f"\n--- TOUR {turn_count} ---")
            self.print_board()
            
            winner = self.check_winner()
            if winner:
                if winner == "draw": print("Match nul !"); break
                print(f"Félicitations ! {'Vous avez' if winner == 'b' else 'HREI a'} gagné !"); break

            # --- Tour du Joueur (b) ---
            print("À vous de jouer (b).")
            legal_moves = self.get_legal_moves("b")
            if not legal_moves:
                print("Vous ne pouvez plus bouger ! HREI gagne.")
                return "w"
                
            # Affichage des coups possibles pour aider (optionnel mais utile)
            print("Coups possibles :")
            formatted_moves = []
            for m in legal_moves:
                s, e = m[0], m[1]
                formatted_moves.append(f"{s[0]},{s[1]}->{e[0]},{e[1]}")
            print("  " + " | ".join(formatted_moves[:10]) + ("..." if len(formatted_moves)>10 else ""))

            valid_move = None
            while not valid_move:
                try:
                    user_input = input("Votre coup (ex: 5,2 4,3) : ").strip()
                    parts = user_input.replace("->", " ").replace(",", " ").split()
                    if len(parts) >= 4:
                        r1, c1, r2, c2 = map(int, parts[:4])
                        # On cherche ce coup dans les legal_moves
                        for m in legal_moves:
                            if m[0] == (r1, c1) and m[1] == (r2, c2):
                                valid_move = m
                                break
                        if not valid_move:
                            print("Coup invalide ou interdit (règle de prise obligatoire ?). Réessayez.")
                    else:
                        print("Format incorrect. Essayez '5,0 4,1'")
                except ValueError:
                    print("Entrée invalide.")
            
            self.make_move(valid_move)
            
            if self.check_winner(): continue

            # --- Tour HREI (w) ---
            if not self.ai_move():
                print("HREI ne peut plus bouger ! Vous gagnez.")
                return "b"
            
            turn_count += 1
        return winner

if __name__ == "__main__":
    fast = "--fast" in sys.argv
    train_mode = "--train" in sys.argv
    reset_mode = "--reset" in sys.argv
    
    # Extraction des profondeurs
    deep_m = 3
    deep_h = 1
    
    for i, arg in enumerate(sys.argv):
        if arg == "--deepm" and i + 1 < len(sys.argv):
            deep_m = int(sys.argv[i+1])
        elif arg == "--deeph" and i + 1 < len(sys.argv):
            deep_h = int(sys.argv[i+1])

    if reset_mode:
        brain_path = os.path.join(os.path.dirname(__file__), "checkers_brain.json")
        if os.path.exists(brain_path):
            os.remove(brain_path)
            print("Cerveau de HREI réinitialisé.")

    if train_mode:
        num_games = 20 # On augmente un peu pour les nouveaux atomes
        print(f"DÉMARRAGE DE L'ENTRAÎNEMENT SILENCIEUX ({num_games} parties)...")
        wins = 0
        for i in range(num_games):
            game_trainer = CheckersHREI(fast_mode=True, deep_m=deep_m, deep_h=deep_h)
            winner = game_trainer.play_silent()
            game_trainer.learn_from_outcome(winner)
            if winner == "w": wins += 1
            print(f"Partie {i+1}/{num_games} terminée. Gagnant: {winner}")
        print(f"\nEntraînement terminé. Taux de victoire: {wins/num_games*100:.1f}%")
    else:
        game = CheckersHREI(fast_mode=fast, deep_m=deep_m, deep_h=deep_h)
        print("Choisissez le mode :")
        print("1. Humain vs HREI")
        print("2. Minimax vs HREI (Duel IA)")
        choice = input("> ")
        
        if choice == "2":
            winner = game.play_duel()
        else:
            winner = game.play_human()
            
        game.learn_from_outcome(winner)

def dummy_functions_to_avoid_syntax_error():
    # Ces fonctions sont maintenant des méthodes de classe, 
    # mais je les laisse ici pour que SearchReplace ne casse pas tout si besoin
    pass
