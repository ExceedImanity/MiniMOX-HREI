# 🌌 MiniMOX | Hybrid Resonance Engine (HREI)

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python: 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Architecture: Hybrid-Intelligence](https://img.shields.io/badge/Architecture-Hybrid--Intelligence-purple.svg)]()
[![Performance: Ultra-Fast](https://img.shields.io/badge/Performance-Ultra--Fast-green.svg)]()

# MiniMOX | Hybrid Resonance Engine (HREI)

"Beyond Deep Learning. Beyond Classical Algorithms. Welcome to Hybrid Intelligence."

MiniMOX is an experimental AI architecture powered by the Hybrid Resonance Engine (HREI). It fuses algorithmic search (System 2) with semantic vector structures (System 1) to enable decision-making based on **Valence** and **Resonance**.

---

## 🚀 The Breakthrough Innovation

Unlike traditional AI (statistical black boxes) or classical algorithms (rigid tools), MiniMOX utilizes **Cognitive Atoms** to:

*   🧠 **Feel Logic:** Use valences (digital pleasure/pain) to guide problem-solving.
*   ⚡ **Semantic Resonance:** Vibrate concepts together to find solutions without exhaustive brute force.
*   🤖 **Cyborg Architecture:** A hybrid engine capable of delegating complex tasks to ultra-fast reflex modules.

---

## 💻 Basic Usage

Integrate the power of HREI into your own projects in seconds:

```python
from engine.core import HREIEngine
from atoms.base import CognitiveAtom

# 1. Initialize the Brain
engine = HREIEngine()

# 2. Create Cognitive Atoms (Label, Valence)
idea = CognitiveAtom("New Idea", valence=5.0)
goal = CognitiveAtom("Success", valence=20.0)

# 3. Add to Engine & Build Relations
engine.add_atom(idea)
engine.add_atom(goal)
idea.relate_to(goal.id, "leads_to")

# 4. Trigger Semantic Resonance
thoughts = engine.resonate("Success", iterations=5)
print(thoughts)
```

> **💡 Go Further:** MiniMOX can do much more (Decision making, Autonomous Learning, Hybrid Search, etc.). Explore the `demos/` folder for complex implementations or dive into `engine/core.py` to see the full potential of the API.

---

## 📊 Benchmarks & Performance Philosophy

MiniMOX/HREI n'est pas conçu pour remplacer les algorithmes classiques sur les tâches de brute-force. Il est conçu pour **les guider**.

### 🔬 Test : Remplissage de grille Sudoku 100x100 (10 000 cellules)

🏆 LE GRAND MATCH : ALGORITHME vs HREI vs HYBRIDE (100x100)
----------------------------------------------------------------------
| Approche | Capacité Traitée | Temps d'Exécution | Statut / Observation |
| :--- | :--- | :--- | :--- |
| ⚡ **ALGORITHME** (Force Brute) | 10 000 cases | 0,001077 s | **Standard** : Rapide mais rigide. |
| 🧠 **HREI** (Réflexion Totale) | 661 cases | 1,000000 s | **Lent** : Analyse profonde, mais volume limité. |
| 🚀 **HYBRIDE** (Optimisé) | 10 000 cases | **0,000103 s** | **Champion** : L'intelligence au service de la vitesse. |
----------------------------------------------------------------------
📊 VERDICT FINAL :
L'Hybride est 9723.7x plus rapide que l'IA pure.
L'Hybride conserve le contrôle cognitif tout en égalant presque la vitesse de l'algorithme.

---

## 🛠️ Core Architecture

### 1. Cognitive Atoms (`Atoms`)
Every data point is an atom with energy, activation, and valence. They are not just numbers; they are **experiences**.

### 2. Resonance Engine (`Engine`)
The heart of the system. It uses *Semantic Resonance Search* to explore complex decision trees by focusing only on "positively resonant" branches.

### 3. Episodic Memory
Experience management that allows the AI to learn from successes and failures in real-time without massive retraining.

---

## 🎨 Application Domains

MiniMOX is not limited to pure logic. Its architecture excels in:
*   🎵 **Musical Composition** (Semantic harmony)
*   🔐 **Advanced Cryptography** (Pattern resonance)
*   🧬 **Bioinformatics** (Protein sequence analysis)
*   🎮 **Strategic Game AI** (Neuro-symbolic decision making)

---

## ⚡ Quick Start

```bash
git clone https://github.com/ExceedImanity/MiniMOX-HREI.git
cd MiniMOX-HREI
pip install -e .
python main.py
```

--- 

## ⚠️ Limitations Connues

- **Pas pour le Deep Learning** : HREI ne remplace pas PyTorch/TensorFlow pour la vision ou le NLP.
- **Mémoire JSON** : La persistance actuelle (`memory_episodic.json`) est adaptée aux prototypes. Pour la production, une intégration SQLite/FAISS est recommandée.
- **Complexité O(N²)** : L'auto-connexion sémantique compare tous les atomes entre eux. Au-delà de ~5000 atomes, envisager une indexation vectorielle approximative (ANN).

---

## 📜 Philosophy & Credits
MiniMOX is built on the idea that intelligence is not an accumulation of data, but a **harmony of connections**. 

**Created and maintained by [ExceedImanity](https://github.com/ExceedImanity).**

### 🎓 How to Cite
If you use the HREI architecture in your research or projects, please credit the author:
`ExceedImanity (2026). MiniMOX: Hybrid Resonance Engine (HREI).`
