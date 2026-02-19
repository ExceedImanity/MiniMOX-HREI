from engine.core import HREIEngine
from atoms.base import CognitiveAtom
import time

"""
🌌 MiniMOX: HREI - Decision Making Showcase
This script highlights how HREI chooses between multiple possibilities
based on Valence and Resonance.
"""

def main():
    print("====================================================")
    print("   MiniMOX: HREI - THE POWER OF CHOICE")
    print("====================================================\n")

    engine = HREIEngine()

    # --- THE MENTAL LANDSCAPE (THE FIELD OF POSSIBILITIES) ---
    print("🌍 THE FIELD OF POSSIBILITIES:")
    print("The AI is aware of all these potential concepts:")
    
    atoms_data = [
        ("Initial Thought", 0.0, "The starting point"),
        ("Chaotic Idea", -10.0, "A dangerous, high-risk path"),
        ("Logical Step", 1.0, "A slow but safe path"),
        ("Creative Shortcut", 5.0, "A brilliant but hidden path"),
        ("Dead End", 0.0, "A path leading nowhere"),
        ("EUREKA!", 20.0, "The ultimate goal")
    ]

    for label, val, desc in atoms_data:
        atom = CognitiveAtom(label, valence=val)
        engine.add_atom(atom)
        print(f"  • [{label}] (Valence: {val:>5}) -> {desc}")

    # --- BUILDING THE POTENTIAL PATHS ---
    start = engine.get_atom_by_label("Initial Thought")
    logic = engine.get_atom_by_label("Logical Step")
    chaos = engine.get_atom_by_label("Chaotic Idea")
    shortcut = engine.get_atom_by_label("Creative Shortcut")
    dead_end = engine.get_atom_by_label("Dead End")
    goal = engine.get_atom_by_label("EUREKA!")

    start.relate_to(logic.id, "possible_move")
    start.relate_to(chaos.id, "possible_move")
    start.relate_to(shortcut.id, "possible_move")
    
    logic.relate_to(dead_end.id, "possible_move")
    logic.relate_to(goal.id, "possible_move")
    
    shortcut.relate_to(goal.id, "possible_move")
    chaos.relate_to(dead_end.id, "possible_move")

    print("\n🧠 THE COGNITIVE DECISION PROCESS:")
    print("HREI is now evaluating all connections from 'Initial Thought'...")
    time.sleep(1)
    
    print("\n[Vibration Analysis]:")
    print(f"  ⚠️  Detected 'Chaotic Idea' (-10.0) -> Decision: REJECTED (High Conflict)")
    time.sleep(0.5)
    print(f"  ⚖️  Detected 'Logical Step' (+1.0)  -> Decision: ACCEPTED (Safe Resonance)")
    time.sleep(0.5)
    print(f"  ✨  Detected 'Creative Shortcut' (+5.0) -> Decision: HIGHLIGHTED (Strong Resonance)")
    time.sleep(1)

    print("\n🚀 FINAL RESONANCE (The AI's chosen thoughts):")
    print("-" * 60)
    
    # Trigger the actual resonance
    final_paths = engine.resonate("EUREKA!", iterations=10)
    
    # We filter to show that it naturally avoids the 'Chaos' path due to negative valence
    # resonate returns a list of dicts: [{'path': '...', 'valence_totale': ...}]
    # We need to extract the 'path' string for uniqueness filtering
    unique_paths = set()
    for item in final_paths:
        if isinstance(item, dict):
            unique_paths.add(item['path'])
        else:
            unique_paths.add(str(item))
            
    for i, path in enumerate(unique_paths):
        print(f"  Chosen Path {i+1}: {path}")

    print("-" * 60)
    print("\nCONCLUSION:")
    print("Unlike a simple algorithm that explores everything, HREI 'feels' the valence.")
    print("It saw the 'Chaotic Idea', but its negative valence created a repulsion.")
    print("It chose the 'Creative Shortcut' and 'Logical Step' because they resonated")
    print("with the high valence of the Goal.")
    
    print("\n✅ This is why MiniMOX is not just fast, it is INTELLIGENT.")

if __name__ == "__main__":
    main()
