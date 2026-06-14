# 🏰 Chronicles of Valdris
### A Multi-Agent RPG System — Microsoft Agents League Hackathon 2026
**Challenge B: Role Play Game System**

---

> *"The Shadow Rift grows. The Starwell Relic is lost. Only you — and three unlikely companions — stand between Valdris and the consuming dark."*

---

## 📖 Project Overview

**Chronicles of Valdris** is a fully playable, terminal-based multi-agent RPG built entirely in Python using **Google Gemini 1.5 Flash** as the AI backbone. It demonstrates a production-grade multi-agent architecture where a central **orchestrator agent** (the Game Master) dynamically dispatches tasks to **specialist sub-agents** (Warrior, Mage, Rogue), synthesises their responses, and narrates a coherent, evolving story.

The system simulates key Microsoft AI stack concepts:
- **Foundry IQ local knowledge retrieval** → `WORLD_LORE` dictionary (RAG simulation)
- **Orchestrator → Sub-Agent dispatch** → `GameMasterAgent.decide_agents()`
- **Shared memory / state management** → `game_state` dictionary
- **Graceful fallback** → offline demo mode when API is unavailable

---

## 🤖 Multi-Agent Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PLAYER INPUT                                  │
│                    "Search the forest grove"                        │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    GAME MASTER AGENT (Orchestrator)                  │
│                                                                     │
│  1. query_lore()  ──────────►  WORLD_LORE dict                     │
│                               (Foundry IQ RAG Simulation)          │
│                                                                     │
│  2. roll_dice()   ──────────►  random.randint(1, 20)               │
│                               Result: 16 → Full Success            │
│                                                                     │
│  3. decide_agents() ────────►  [MageAgent, RogueAgent]             │
│      keyword analysis             ↑ magic keywords detected        │
│                                   ↑ stealth keywords detected      │
│                                                                     │
│  4. update_game_state() ────►  quest_flags, location, inventory    │
│                                                                     │
│  5. respond() ──────────────►  Gemini 1.5 Flash API call          │
│      (Final narration)            (ONE call per turn)              │
└──────────┬──────────────────────────────────┬───────────────────────┘
           │                                  │
           ▼                                  ▼
┌──────────────────────┐          ┌───────────────────────┐
│   MAGE AGENT         │          │   ROGUE AGENT         │
│   Lyra Vey           │          │   Zara Nightwhisper   │
│                      │          │                       │
│  "The ley-line here  │          │  "I've already        │
│  matches Dorath's    │          │  spotted the trap     │
│  annotations..."     │          │  on the third stone." │
│                      │          │                       │
│  → Gemini API call   │          │  → Gemini API call    │
└──────────────────────┘          └───────────────────────┘
           │                                  │
           └──────────────┬───────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     FINAL NARRATION (GM)                            │
│  Synthesises: lore + roll result + agent responses → epic scene    │
│  + Shows party health bars + Quest choices + Inventory update      │
└─────────────────────────────────────────────────────────────────────┘
```

### Agent Roster

| Agent | Name | Role | Personality | Trigger Keywords |
|---|---|---|---|---|
| `GameMasterAgent` | ⚔ Game Master | Orchestrator | Narrative, omniscient | All input |
| `WarriorAgent` | Bran Ironvale | Combat Tactician | Brave, blunt, anti-magic | fight, attack, charge, defend... |
| `MageAgent` | Lyra Vey | Arcane Expert | Analytical, slightly arrogant | magic, relic, rune, lore, decode... |
| `RogueAgent` | Zara Nightwhisper | Scout & Face | Witty, skeptical, observant | sneak, scout, trap, search, notice... |

---

## 🗺️ How It Simulates Microsoft IQ Layers

| Microsoft Agents League Layer | Chronicles of Valdris Implementation |
|---|---|
| **Foundry IQ — Local Knowledge Base** | `WORLD_LORE` dict with 7 categories, queried each turn via keyword matching |
| **Orchestrator Agent** | `GameMasterAgent` — routes input, dispatches sub-agents, synthesises output |
| **Specialist Sub-Agents** | `WarriorAgent`, `MageAgent`, `RogueAgent` — each with distinct system prompts |
| **Shared Memory / World State** | `game_state` dict — persisted across all agents every turn |
| **RAG-style Retrieval** | `query_lore()` scans `WORLD_LORE` for semantically relevant context |
| **Tool Use (dice, damage)** | `roll_dice()`, `apply_damage()`, `use_healing_potion()` called by GM |
| **Graceful Degradation** | Offline demo mode with pre-scripted responses when API unavailable |
| **One API Call Per Turn** | GM batches all agent context into a single Gemini call for narration |

---

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/chronicles-of-valdris.git
cd chronicles-of-valdris
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Your API Key
```bash
# Copy the example env file
copy .env.example .env   # Windows
cp .env.example .env     # Linux/macOS

# Edit .env and add your key
# Get a FREE key at: https://aistudio.google.com/
GEMINI_API_KEY=your_actual_key_here
```

### 4. Run the Game
```bash
python main.py
```

> **No API key?** The game runs in **Offline Demo Mode** with richly scripted character responses. No setup required — just `python main.py`.

---

## 🎮 Example Gameplay

```
  ╔══ OPENING SCENE ════════════════════════════════════════════════════╗

  The city of Valdris hums with nervous energy as you push open the
  heavy oak door of the Moonlit Gate Tavern. Lantern light spills across
  worn flagstones; the smell of hearth smoke and roasted game fills your
  lungs. Bran Ironvale sharpens his blade. Lyra Vey reads from a cracked
  tome. Zara Nightwhisper watches the door with quiet, predatory calm.

  ╔══ PARTY STATUS ══════════════════════════════════════════════════════╗
  Bran   HP: 30/30  [████████████████████]
  Lyra   HP: 20/20  [████████████████████]
  Zara   HP: 25/25  [████████████████████]

  ➤  Search the tavern basement for Dorath's journal

  ────────────────────────────────────────────────────────────────────────

  🎲 [Search tavern basem] Rolling d20... 16  →  ✔ Full Success

  [Consulting Lyra Vey...]

  ✦  Lyra Vey
  │  The arcane signature on this chest matches Dorath's known
  │  enchantment style — third dynasty locking runes. Give me a
  │  moment; I'll bypass the ward without triggering the alarm.
  └────────────────────────────────────────────────────────────────────

  [Consulting Zara Nightwhisper...]

  🗡  Zara Nightwhisper
  │  There are fresh boot scuffs on the floor here — someone's been
  │  down recently. And that wall bracket? It's a lever. These old
  │  taverns always have a second basement.
  └────────────────────────────────────────────────────────────────────

  📍 Quest flag updated: Journal Found ✓
  🎒 Dorath's Journal added to inventory!

  ╔══ NARRATION ═════════════════════════════════════════════════════════╗

    Dust cascades from the ceiling as the hidden panel grinds open.
    Beyond lies a cramped stone chamber — shelves of rotting books
    and a single ironbound chest etched with faintly glowing runes.
    Lyra dispatches the ward in moments with practiced ease. Inside
    the chest, wrapped in oilcloth, is a battered leather journal.
    The name on the cover reads: DORATH THE GREY. Zara notices a
    second concealed door in the east wall, barely visible in the
    torchlight. The journal's first page reads: "I have hidden it
    in three places. Find the ley-line first."

  ╔══ YOUR CHOICES ══════════════════════════════════════════════════════╗
    1. Search the tavern basement for Dorath's journal
    2. Ask Orwen the barkeep about the Starwell Relic
    3. Head to the Darkwood Forest to investigate
    4. Sneak into the Merchant District to find the Shadow Guild

  Commands: 'status' · 'inventory' · 'quit' · or type any action
```

---

## 🗂️ Project Structure

```
chronicles-of-valdris/
│
├── main.py            ← Complete game (all agents, lore, game loop)
├── requirements.txt   ← Python dependencies
├── .env.example       ← API key template
└── README.md          ← This file
```

---

## 🧠 Key Design Decisions

### Single-File Architecture
All agents, lore, and game logic live in `main.py` for hackathon portability and easy review. In production, each agent would be a separate module with its own test suite.

### One Gemini API Call Per Turn
To maximise efficiency on the free tier, only the **Game Master's final narration** calls the Gemini API. Character agent calls are also made (one each), but the GM batches all context into a single, rich prompt. This pattern mirrors agentic frameworks that bill per-call.

### Offline Demo Mode
If `GEMINI_API_KEY` is missing or invalid, every agent falls back to pre-scripted, character-consistent responses. This ensures the game is **always demonstrable** — even in venues without internet access.

### RAG Simulation via `WORLD_LORE`
The `query_lore()` method in `GameMasterAgent` performs keyword-based retrieval across the `WORLD_LORE` dictionary, returning only the most relevant 1–3 lore chunks. This simulates a vector database retrieval step without requiring an actual vector store, keeping the demo self-contained.

---

## ⚙️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core language |
| `google-generativeai` | Gemini 1.5 Flash API (free tier) |
| `colorama` | Cross-platform ANSI terminal colors |
| `python-dotenv` | `.env` file management |
| `random` (stdlib) | Dice rolling (d20 system) |
| `textwrap` (stdlib) | Terminal text wrapping |
| `time` (stdlib) | Dramatic typing animation |

---

## 🎲 Game Systems

### Dice Check Results (d20)
| Roll | Result | Effect |
|---|---|---|
| 1–4 | ☠ Critical Failure | Action backfires, 2d6 damage |
| 5–9 | ✘ Failure | Action fails, 1d6 damage in combat |
| 10–14 | ~ Partial Success | Succeeds with a cost or twist |
| 15–19 | ✔ Full Success | Clean success |
| 20 | ✦ Critical Success | Exceeds expectations, bonus effect |

### Health System
- **Bran Ironvale** — 30 HP (tank)
- **Lyra Vey** — 20 HP (glass cannon)
- **Zara Nightwhisper** — 25 HP (balanced)
- Healing potions restore 1d8+2 HP. Use: `heal Bran` / `heal Lyra` / `heal Zara`

### Quest Progression Flags
| Flag | Trigger | Effect |
|---|---|---|
| `journal_found` | Search tavern + roll ≥ 10 | Unlocks forest ley-line path |
| `leyline_decoded` | Decode journal in forest + roll ≥ 10 | Reveals Relic location |
| `crystal_obtained` | Find crystal in forest + roll ≥ 15 | Adds Crystal of Sight to inventory |
| `shadow_blade_found` | Loot guild enforcer + roll ≥ 12 | Adds Shadow Blade to inventory |
| `guardian_defeated` | Fight Guardian + roll ≥ 15 | Opens Starwell Chamber |
| `relic_found` | Recover Relic + roll ≥ 18 | Victory path unlocked |
| `rift_sealed` | Return Relic + roll ≥ 12 | 🏆 Victory! |

---

## 🔑 Commands Reference

| Command | Effect |
|---|---|
| `status` | Show party HP bars |
| `inventory` | List all items |
| `quest` | Show quest flags & progress |
| `heal Bran` | Use healing potion on Bran |
| `heal Lyra` | Use healing potion on Lyra |
| `heal Zara` | Use healing potion on Zara |
| `help` | Show all commands |
| `quit` | End session, show summary |
| *any other text* | Execute that action in the world |

---

## 🚀 Hackathon Submission Notes

- **Event:** Microsoft Agents League Hackathon 2026
- **Challenge:** B — Role Play Game System
- **Team:** Pratham Borhade
- **Submission Date:** June 2026

This project demonstrates:
1. ✅ Multi-agent orchestration pattern (GM → Warrior/Mage/Rogue)
2. ✅ Local knowledge base retrieval (Foundry IQ simulation)
3. ✅ Shared world state management across agents
4. ✅ Gemini 1.5 Flash integration (free tier, single API call per turn)
5. ✅ Graceful offline fallback for demo resilience
6. ✅ Rich terminal UX (colorama, health bars, animations)
7. ✅ Complete playable game loop with win/lose conditions

---

## 📜 License & Attribution

All world data, characters, locations, factions, and lore in this project are **entirely fictional and synthetic**, created solely for demonstration purposes. No real persons, organisations, or copyrighted works are referenced or depicted.

```
# All data is synthetic and created for demonstration purposes only.
```

---

*Built with ⚔ and ✨ for the Microsoft Agents League Hackathon 2026*
