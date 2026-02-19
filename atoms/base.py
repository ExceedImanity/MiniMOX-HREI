from typing import List, Dict, Any, Optional
import time

class CognitiveAtom:
    def __init__(self, label: str, data: Any = None, valence: float = 0.0):
        self.id = label  # Identifiant unique
        self.label = label
        self.data = data
        
        # --- DYNAMIQUE ÉNERGÉTIQUE ---
        self.valence = valence  # Charge émotionnelle (-100 à +100)
        self.energy = 1.0       # Énergie vitale (0.0 à 1.0)
        self.activation = 0.0   # Niveau d'excitation actuel (Working Memory)
        
        self.last_accessed = time.time()
        
        # --- SYNAPSES ---
        self.relations: Dict[str, List[str]] = {} # type -> [target_ids]
        self.link_weights: Dict[str, float] = {}  # target_id -> weight (0.0 à 5.0)
        
        self.embedding: Optional[List[float]] = None # Vecteur sémantique

    def relate_to(self, target_id: str, relation_type: str, weight: float = 1.0):
        """Crée ou renforce une connexion synaptique."""
        if relation_type not in self.relations:
            self.relations[relation_type] = []
        if target_id not in self.relations[relation_type]:
            self.relations[relation_type].append(target_id)
        
        # Renforcement Hebbien
        current_w = self.link_weights.get(target_id, 0.0)
        self.link_weights[target_id] = min(5.0, current_w + weight)

    def stimulate(self, amount: float = 0.1):
        """Active l'atome (Simule l'attention)."""
        self.activation = min(1.0, self.activation + amount)
        self.energy = min(1.0, self.energy + (amount * 0.1))
        self.last_accessed = time.time()

    def decay(self, rate: float = 0.01):
        """
        Loi de l'Oubli : L'atome perd de l'activation et de l'énergie avec le temps.
        Si un lien devient trop faible, il casse.
        """
        # Baisse de l'excitation immédiate (rapide)
        self.activation *= 0.9
        
        # Baisse de l'énergie structurelle (lente)
        self.energy = max(0.0, self.energy - rate)
        
        # Élagage synaptique
        dead_links = []
        for target, w in self.link_weights.items():
            # Les liens s'affaiblissent s'ils ne sont pas utilisés
            self.link_weights[target] *= (1.0 - (rate * 0.5))
            if self.link_weights[target] < 0.1:
                dead_links.append(target)
        
        for target in dead_links:
            del self.link_weights[target]
            # Nettoyage des relations
            for r_type in self.relations:
                if target in self.relations[r_type]:
                    self.relations[r_type].remove(target)

    def __repr__(self):
        return f"<Atom {self.label} (V:{self.valence:.1f} E:{self.energy:.2f})>"