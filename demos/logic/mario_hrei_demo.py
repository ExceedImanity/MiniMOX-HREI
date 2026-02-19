import sys
import os
import time
import random
import math
import copy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

# --- PHYSIQUE DU MONDE ---
GRAVITY = 1.5
JUMP_FORCE = -3.5 # Force impulsionnelle
MAX_SPEED_X = 1.0
FRICTION = 0.8

class MarioState:
    def __init__(self, x, y, vx, vy, is_grounded, map_data):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.is_grounded = is_grounded
        self.map_data = map_data # Read-only ref
        self.status = "ALIVE" # ALIVE, DEAD, WON
        self.score = 0

    def clone(self):
        new_state = MarioState(self.x, self.y, self.vx, self.vy, self.is_grounded, self.map_data)
        new_state.status = self.status
        new_state.score = self.score
        return new_state

    def to_hash(self):
        # Pour le cache HREI (on arrondit pour grouper les états proches)
        return (int(self.x), int(self.y), int(self.vx*10), int(self.vy*10))

class MarioWorld:
    def __init__(self):
        # Création du niveau 1-1 Simplifié
        # . = Air, # = Sol, G = Goomba, ? = Bloc, | = Tuyau, F = Fin
        layout = [
            ".....................................................................................",
            ".....................................................................................",
            ".....................................................................................",
            ".....................................??..............................................",
            "......................................................................F..............",
            "....................?......?.....................G...................###.............",
            ".......................................|.......#####................##.##............",
            ".....G..........................|......|......#######......G.......##...##...........",
            "###################...###################...#####################.##.....##.........."
        ]
        self.height = len(layout)
        self.width = len(layout[0])
        self.grid = layout
        self.start_x = 2.0
        self.start_y = float(self.height - 4) # On part de plus haut pour bien tomber

    def get_tile(self, x, y):
        ix, iy = int(x), int(y)
        if iy < 0 or iy >= self.height: return "." 
        if ix < 0 or ix >= self.width: return "." 
        return self.grid[iy][ix]

    def step(self, state, action):
        if state.status != "ALIVE": return state

        new_state = state.clone()
        
        # 1. Input Physics
        if action == "RIGHT":
            new_state.vx += 0.4
        elif action == "LEFT":
            new_state.vx -= 0.4
        elif action == "JUMP" and new_state.is_grounded:
            new_state.vy = JUMP_FORCE
            new_state.is_grounded = False
        elif action == "RUN_JUMP" and new_state.is_grounded:
             new_state.vx += 0.6
             new_state.vy = JUMP_FORCE * 1.1
             new_state.is_grounded = False

        # 2. Gravity & Friction
        new_state.vy += GRAVITY * 0.15
        new_state.vx *= FRICTION
        if abs(new_state.vx) < 0.05: new_state.vx = 0

        # 3. Movement X (Horizontal)
        new_state.x += new_state.vx
        
        # Collision Mur (on vérifie au niveau du corps de Mario)
        if self.get_tile(new_state.x, new_state.y) in ["#", "|", "?"]:
            new_state.x -= new_state.vx
            new_state.vx = 0

        # 4. Movement Y (Vertical)
        new_state.y += new_state.vy

        # Collision Sol (on vérifie sous les pieds)
        # Si le bas du sprite touche un bloc solide
        foot_y = new_state.y + 0.5
        tile_below = self.get_tile(new_state.x, foot_y)
        
        if tile_below in ["#", "|", "?"]:
            if new_state.vy > 0: # On descend
                new_state.y = math.floor(foot_y) - 0.51 # On se pose juste au dessus
                new_state.vy = 0
                new_state.is_grounded = True
        else:
            new_state.is_grounded = False

        # 5. Interaction Mortelle / Victoire
        current_tile = self.get_tile(new_state.x, new_state.y)
        if current_tile == "G":
            new_state.status = "DEAD"
        if current_tile == "F":
            new_state.status = "WON"
            
        # Chute dans le vide
        if new_state.y > self.height:
            new_state.status = "DEAD"

        return new_state

# --- CERVEAU HREI ---
class SuperMarioHREI:
    def __init__(self, world):
        self.world = world
        self.engine = HREIEngine()
        
        # Atomes Cognitifs
        self.atom_progress = CognitiveAtom("DESIRE_FORWARD", valence=5.0)
        self.atom_survival = CognitiveAtom("FEAR_OF_DEATH", valence=500.0) # Priorité absolue
        self.atom_flow = CognitiveAtom("MOMENTUM_JOY", valence=2.0)
        
        self.engine.add_atom(self.atom_progress)
        self.engine.add_atom(self.atom_survival)
        self.engine.add_atom(self.atom_flow)

    def simulator_interface(self, state, mode):
        if mode == "GET_ACTIONS":
            # Optimisation : Si on a de l'élan, on évite de s'arrêter pour rien
            if abs(state.vx) > 0.1:
                return ["RIGHT", "JUMP", "RUN_JUMP"]
            return ["RIGHT", "JUMP", "RUN_JUMP", "WAIT"]
        else:
            # Mode Simulation : On demande au monde de calculer le prochain état
            next_state = self.world.step(state, mode)
            # Petite pénalité de temps pour encourager la vitesse
            return (next_state, -0.1, "AGENT")

    def evaluator_interface(self, state):
        """
        La Fonction de Valence optimisée : Survie, Trous et Évitement d'Ennemis.
        Utilise les atomes cognitifs pour pondérer les décisions.
        """
        if state.status == "DEAD":
            # La mort est l'opposé absolu de la survie
            return -self.atom_survival.valence * 2000.0 
        if state.status == "WON":
            # La victoire est le but ultime (Progrès maximisé)
            return self.atom_progress.valence * 100000.0

        valence = 0.0
        
        # 1. Progrès (L'attraction du drapeau)
        valence += state.x * self.atom_progress.valence * 20.0 
        
        # 2. Peur du Vide (Analyse verticale)
        tile_below = self.world.get_tile(state.x, state.y + 1)
        if tile_below == "." and not state.is_grounded:
            valence -= self.atom_survival.valence * 10.0
            
        # 3. Évitement des Ennemis (Aura de Mort intelligente)
        # On ne regarde que devant soi (0 à 5 cases)
        for dx in range(0, 6): 
            for dy in range(-1, 2): # Juste autour de la hauteur actuelle
                tile = self.world.get_tile(state.x + dx, state.y + dy)
                if tile == "G":
                    # Si on est au-dessus du Goomba (saut), on n'a pas peur !
                    if (state.y + 1) < (state.y + dy): 
                        continue # Je suis au-dessus, je l'écrase
                        
                    dist = abs(dx) + abs(dy)
                    if dist <= 1: 
                        valence -= self.atom_survival.valence * 100.0 # Danger immédiat
                    else: 
                        valence -= (self.atom_survival.valence * 4.0) / dist 
        
        # 4. Bonus de Momentum (Flow)
        valence += state.vx * self.atom_flow.valence * 15.0

        return valence

    def play(self):
        print("=== SUPER MINIMOX BROS : HREI VISION 8-FRAMES (OPTIMISÉE) ===")
        print("Lancement du moteur cognitif...")
        
        current_state = MarioState(self.world.start_x, self.world.start_y, 0, 0, True, self.world.grid)
        
        step = 0
        while current_state.status == "ALIVE":
            step += 1
            
            # 1. HREI RÉFLÉCHIT
            actions = self.simulator_interface(current_state, "GET_ACTIONS")
            best_action = "WAIT"
            max_res = -float('inf')
            
            # On utilise un cache pour cette frame
            frame_cache = {}
            
            for action_candidate in actions:
                next_s, _, _ = self.simulator_interface(current_state, action_candidate)
                # Profondeur 8 = Suffisant pour voir le trou et réactif
                res = self.engine.hybrid_resonance_search(
                    next_s, 
                    self.simulator_interface, 
                    self.evaluator_interface, 
                    depth=8, 
                    precise_threshold=3,
                    cache=frame_cache
                )
                if res > max_res:
                    max_res = res
                    best_action = action_candidate
            
            action = best_action
            
            # 2. ACTION RÉELLE
            current_state = self.world.step(current_state, action)
            
            # 3. RENDU ASCII
            self.render(current_state, action, step)
            # time.sleep(0.15) # On enlève le sleep pour voir si ça va plus vite
            
            if step > 200:
                print("Time Over ! Mario a traîné.")
                break

        if current_state.status == "WON":
            print("\nVICTOIRE ! HREI A TROUVÉ L'HARMONIE DU NIVEAU !")
        else:
            print("\nGAME OVER. La dissonance a eu raison de Mario.")

    def render(self, state, action, step):
        # On affiche une fenêtre autour de Mario (Scrolling)
        cam_x = int(state.x) - 10
        cam_x = max(0, min(cam_x, self.world.width - 60))
        
        buffer = f"\nFrame {step} | Action: {action} | Valence: {self.evaluator_interface(state):.1f}\n"
        buffer += "+" + "-"*60 + "+\n"
        
        mario_ix, mario_iy = int(state.x), int(state.y)
        
        for y in range(self.world.height):
            line = "|"
            for x in range(cam_x, cam_x + 60):
                if x == mario_ix and y == mario_iy:
                    line += "M" # Mario
                else:
                    line += self.world.grid[y][x]
            line += "|"
            buffer += line + "\n"
        buffer += "+" + "-"*60 + "+"
        print(buffer)

if __name__ == "__main__":
    world = MarioWorld()
    player = SuperMarioHREI(world)
    player.play()
