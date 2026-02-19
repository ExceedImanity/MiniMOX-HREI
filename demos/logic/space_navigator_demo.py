import sys
import os
import time
import random
import math
import copy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from engine.core import HREIEngine
from atoms.base import CognitiveAtom

# --- MATHS 3D PURES ---
class Vector3:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
    def add(self, v): return Vector3(self.x + v.x, self.y + v.y, self.z + v.z)
    def dist(self, v): return math.sqrt((self.x-v.x)**2 + (self.y-v.y)**2 + (self.z-v.z)**2)

# --- L'UNIVERS ---
class SpaceState:
    def __init__(self, ship_pos, ship_vel, asteroids, score=0, status="FLYING"):
        self.ship_pos = ship_pos
        self.ship_vel = ship_vel
        self.asteroids = asteroids 
        self.score = score
        self.status = status 

    def to_hash(self):
        """LA CORRECTION DE GÉNIE : ABSTRACTION SITUATIONNELLE"""
        # 1. On arrondit la position du vaisseau (Grille de 2.0 unités)
        sx = round(self.ship_pos.x / 2.0)
        sy = round(self.ship_pos.y / 2.0)
        
        # 2. On cherche le danger le plus proche
        closest_ast = None
        min_dz = 999
        for ast in self.asteroids:
            dz = ast.z - self.ship_pos.z
            if 0 < dz < 20:
                if dz < min_dz:
                    min_dz = dz
                    closest_ast = ast
        
        if closest_ast:
            # On calcule la position RELATIVE du danger
            dx = round((closest_ast.x - self.ship_pos.x) / 2.0)
            dy = round((closest_ast.y - self.ship_pos.y) / 2.0)
            return f"S({sx},{sy})D({dx},{dy})"
        return f"S({sx},{sy})FREE"

    def clone(self):
        return SpaceState(
            Vector3(self.ship_pos.x, self.ship_pos.y, self.ship_pos.z),
            Vector3(self.ship_vel.x, self.ship_vel.y, self.ship_vel.z),
            self.asteroids, self.score, self.status
        )

class SpaceWorld:
    def __init__(self, seed=None):
        if seed: random.seed(seed)
        self.asteroids = []
        for z in range(30, 2000, 30): # Un peu plus espacé pour laisser une chance
            for _ in range(random.randint(1, 2)):
                self.asteroids.append(Vector3(random.uniform(-7, 7), random.uniform(-3, 3), z))
        if seed: random.seed(None)

    def step(self, state, action):
        if state.status != "FLYING": return state
        new_state = state.clone()
        thrust = 1.2 
        if action == "UP": new_state.ship_vel.y += thrust
        elif action == "DOWN": new_state.ship_vel.y -= thrust
        elif action == "LEFT": new_state.ship_vel.x -= thrust
        elif action == "RIGHT": new_state.ship_vel.x += thrust
        
        new_state.ship_vel.x *= 0.6
        new_state.ship_vel.y *= 0.6
        new_state.ship_vel.z = 3.5 
        new_state.ship_pos = new_state.ship_pos.add(new_state.ship_vel)
        
        if abs(new_state.ship_pos.x) > 10 or abs(new_state.ship_pos.y) > 5:
            new_state.status = "CRASHED_WALL"
        for ast in new_state.asteroids:
            if abs(ast.z - new_state.ship_pos.z) < 4:
                if new_state.ship_pos.dist(ast) < 2.2:
                    new_state.status = "CRASHED_ASTEROID"
                    break
        return new_state

class SpaceNavigatorHREI:
    def __init__(self, world, memory_file="genius_memory.json"):
        self.world = world
        self.engine = HREIEngine(memory_file=memory_file)
        
        # Atomes Cognitifs pour la navigation spatiale
        self.atom_survival = CognitiveAtom("SURVIE", valence=100.0)
        self.atom_progress = CognitiveAtom("PROGRES", valence=10.0)
        self.atom_curiosity = CognitiveAtom("CURIOSITE", valence=5.0)
        
        self.engine.add_atom(self.atom_survival)
        self.engine.add_atom(self.atom_progress)
        self.engine.add_atom(self.atom_curiosity)

    def simulator_interface(self, state, mode):
        if mode == "GET_ACTIONS": return ["UP", "DOWN", "LEFT", "RIGHT", "NEUTRAL"]
        else: return (self.world.step(state, mode), 0, "AGENT")

    def evaluator_interface(self, state):
        if "CRASHED" in state.status: 
            return -self.atom_survival.valence * 1000.0 # Punition massive
            
        valence = state.ship_pos.z * self.atom_progress.valence
        
        sorted_asteroids = sorted(state.asteroids, key=lambda a: abs(a.z - state.ship_pos.z))
        for ast in sorted_asteroids[:5]:
            dz = ast.z - state.ship_pos.z
            if 0 < dz < 25:
                d_xy = math.sqrt((ast.x - state.ship_pos.x)**2 + (ast.y - state.ship_pos.y)**2)
                if d_xy < 5.0:
                    # La peur augmente inversement à la distance
                    threat_level = (25.0 - dz) / 25.0
                    valence -= (self.atom_survival.valence * 600.0 * threat_level) / (d_xy + 0.1)
                    
        return valence

    def fly(self, episode=1, max_time=15):
        state = SpaceState(Vector3(0,0,0), Vector3(0,0,3.5), self.world.asteroids)
        t_start = time.time()
        frame = 0
        best_action = "NEUTRAL"
        
        while state.status == "FLYING":
            frame += 1
            if time.time() - t_start > max_time: return "SURVIVED", state.ship_pos.z

            if frame % 2 == 0 or frame == 1:
                actions = ["UP", "DOWN", "LEFT", "RIGHT", "NEUTRAL"]
                max_res = -float('inf')
                
                danger_near = False
                for ast in self.world.asteroids:
                    if 0 < (ast.z - state.ship_pos.z) < 20:
                        danger_near = True; break
                
                current_depth = 8 if danger_near else 2
                cache = {}
                for act in actions:
                    next_s = self.world.step(state, act)
                    res = self.engine.hybrid_resonance_search(
                        next_s, self.simulator_interface, self.evaluator_interface, 
                        depth=current_depth, cache=cache, beam_width=2
                    )
                    if res > max_res:
                        max_res = res
                        best_action = act

            state = self.world.step(state, best_action)
            if state.ship_pos.z > 1900: return "SUCCESS", state.ship_pos.z
        return state.status, state.ship_pos.z

if __name__ == "__main__":
    print("=== ACADEMY 100 : GENIUS ABSTRACTION MODE ===")
    memory_file = "genius_memory.json"
    results = []
    for i in range(1, 101):
        world = SpaceWorld(seed=random.randint(1, 100000))
        pilot = SpaceNavigatorHREI(world, memory_file=memory_file)
        status, dist = pilot.fly(episode=i, max_time=10) # 10s pour aller plus vite
        results.append(dist)
        if i % 10 == 0:
            print(f"Épisode {i}/100 | Moyenne: {sum(results[-10:])/10:.1f} | Mémoire Situations: {len(pilot.engine.memory)}")
    
    print("\n=== VOL DE GALA FINAL (GRAINE 777) ===")
    gala_world = SpaceWorld(seed=777)
    gala_pilot = SpaceNavigatorHREI(gala_world, memory_file=memory_file)
    res, final_z = gala_pilot.fly(episode="GALA", max_time=30)
    print(f"RÉSULTAT DU GALA : {res} à Z={final_z:.1f}")
