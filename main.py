# =============================================================================
# Chronicles of Valdris - Multi-Agent RPG System
# Microsoft Agents League Hackathon 2026 | Challenge B - Role Play Game System
# =============================================================================
# All data is synthetic and created for demonstration purposes only.
# No real people, no PII, no copyrighted content is included.
# =============================================================================

import os
import sys
import random
import textwrap
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types as genai_types
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# Load environment variables from .env file
load_dotenv()


# =============================================================================
# WORLD LORE — Simulates Foundry IQ Local Knowledge Base Retrieval
# The GameMaster queries this dictionary before narrating each scene,
# mimicking a retrieval-augmented generation (RAG) pipeline.
# =============================================================================

WORLD_LORE = {
    "world_overview": (
        "Valdris is a realm caught between two forces: the ancient magic of the Starwell "
        "and the creeping corruption of the Shadow Rift. For centuries, the Starwell Relic "
        "kept the Rift sealed beneath the Ancient Ruins east of Valdris City. Thirty years "
        "ago, the Relic vanished — stolen, lost, or hidden by forces unknown. Since then, "
        "shadow creatures have grown bolder, forests have darkened, and the Royal House of "
        "Valdris has grown desperate. Three factions now race to find the Relic: the "
        "scholarly Order of Silver Root, the cunning Shadow Guild, and the faltering "
        "Royal House itself. Into this chaos, a party of adventurers enters the "
        "Moonlit Gate Tavern in Valdris City, seeking coin and glory."
    ),

    "locations": {
        "Moonlit Gate Tavern": (
            "A warm, lantern-lit tavern inside Valdris City's main gate. The floor is "
            "scuffed stone, the ale is strong, and the barkeep Orwen asks no questions. "
            "Bounty boards line the eastern wall. A back room hosts private dealings "
            "between factions. The tavern is the party's home base and safe haven."
        ),
        "Darkwood Forest": (
            "A dense, ancient forest northwest of Valdris City. The canopy is so thick "
            "that midday looks like dusk. Forest Bandits camp along the main road while "
            "Stone Golems guard a hidden shrine deeper within. Lyra believes the forest "
            "holds a ley-line that could pinpoint the Relic's last known location. "
            "Skill checks for navigation: DC 13. Skill checks to avoid ambush: DC 11."
        ),
        "Valdris City": (
            "A walled city of 40,000 souls ruled by King Aldric Valdris III. The city "
            "is divided into three districts: the Noble Quarter (Order of Silver Root HQ), "
            "the Merchant District (Shadow Guild front operations), and the Outer Ward "
            "(common folk, the Moonlit Gate Tavern). The Royal Palace sits at the city's "
            "center, its spires visible for miles. City guards patrol in pairs; asking "
            "about the Relic openly draws unwanted attention."
        ),
        "Ancient Ruins": (
            "A sprawling ruin complex 10 leagues east of Valdris City. Once the seat of "
            "the Valdris Empire's first dynasty, now overrun by Shadow Wraiths and "
            "guarded by an Ancient Guardian — a stone colossus animated by old empire "
            "magic. The Starwell itself is a deep circular shaft at the ruins' center "
            "from which magical energy once flowed upward. The Relic must be returned "
            "here to re-seal the Shadow Rift. Skill check to navigate safely: DC 15."
        ),
    },

    "factions": {
        "Order of Silver Root": (
            "A scholarly order of mages and historians headquartered in Valdris City's "
            "Noble Quarter. They believe the Relic must be studied before being used, "
            "fearing a botched re-sealing could worsen the Rift. Their leader, Archon "
            "Serevyn, is brilliant but cautious. They will trade information for artifacts "
            "and are neutral unless threatened. Ally potential: HIGH."
        ),
        "Shadow Guild": (
            "A criminal syndicate disguised as a merchant consortium. They believe the "
            "Relic's power can be extracted and sold, uncaring about the Rift. Their "
            "enforcer, Mira Coldhand, has been tracking the party since the Tavern. "
            "They deal in blackmail, theft, and assassination. Enemy by default, though "
            "they can be bribed for a price. Ally potential: LOW (at extreme cost)."
        ),
        "Royal House of Valdris": (
            "King Aldric III is desperate — his kingdom is crumbling under shadow "
            "creature raids. He has issued a royal decree: whoever returns the Relic "
            "earns a lordship and 10,000 gold coins. However, the Royal Spymaster, "
            "Councillor Voss, has his own agenda and may betray the party if they "
            "grow too powerful. Ally potential: MEDIUM (politically risky)."
        ),
    },

    "main_quest": (
        "QUEST: Find the Starwell Relic\n"
        "The Starwell Relic is a fist-sized crystal orb inscribed with runes of binding. "
        "Thirty years ago it was removed from the Ancient Ruins by a wizard named Dorath "
        "the Grey, who feared it was being corrupted. Dorath died before revealing its "
        "location. Clues point to three possible hiding spots: a sealed vault beneath "
        "the Moonlit Gate Tavern, a hidden grove in Darkwood Forest, and a crypt inside "
        "the Ancient Ruins itself. The party must investigate each location, survive "
        "the encounters, and ultimately return the Relic to the Starwell.\n"
        "STAGES:\n"
        "  1. [Tavern] Find Dorath's journal hidden in the Tavern basement.\n"
        "  2. [Forest] Decode the journal's map using the Darkwood ley-line.\n"
        "  3. [Ruins]  Defeat the Ancient Guardian and return the Relic.\n"
        "REWARD: Royal lordship + 10,000 gold + peace restored to Valdris."
    ),

    "monsters": {
        "Shadow Wraith": (
            "CR 4. HP: 45. AC: 13 (natural). Speed: fly 40ft.\n"
            "Attacks: Life Drain (2d6+3 necrotic, DC 13 CON save or max HP reduced).\n"
            "Weakness: radiant damage, torchlight (disadvantage in bright light).\n"
            "Found in: Ancient Ruins, shadowy alleys of Valdris City at night.\n"
            "Tactics: Bran recommends rushing with torch held high; Lyra can cast "
            "a light spell to force disadvantage."
        ),
        "Stone Golem": (
            "CR 6. HP: 90. AC: 17 (stone). Speed: 30ft. Immune to non-magical attacks.\n"
            "Attacks: Slam (2d10+6 bludgeoning). Special: Slow (DC 15 CON save).\n"
            "Weakness: magical weapons or spells; Lyra's arcane bolts are effective.\n"
            "Found in: Darkwood Forest shrine, outer Ancient Ruins perimeter.\n"
            "Tactics: Non-magical weapons are useless; Lyra must lead; Bran creates "
            "a distraction while Lyra channels arcane energy."
        ),
        "Forest Bandit": (
            "CR 1/2. HP: 16. AC: 12 (leather). Speed: 30ft.\n"
            "Attacks: Shortsword (1d6+2) or Shortbow (1d6+2, range 80ft).\n"
            "Weakness: intimidation checks (DC 10) can cause them to flee.\n"
            "Found in: Darkwood Forest road, Valdris City Outer Ward.\n"
            "Tactics: Zara can scout their camp and thin numbers before engagement; "
            "Bran's intimidating presence can end fights early."
        ),
        "Ancient Guardian": (
            "CR 9. HP: 152. AC: 19 (ancient stone). Speed: 30ft. Boss monster.\n"
            "Attacks: Crushing Fist (3d8+7), Seismic Stomp (3d6, all creatures in 10ft, "
            "DC 16 DEX save or knocked prone).\n"
            "Special: Rune Shield (immune to spells of 3rd level or lower until shield "
            "breaks; Lyra must expend two full turns of casting to break it).\n"
            "Weakness: the Crystal of Sight, if found, reveals a glowing rune on its "
            "chest — Bran can target it for double damage.\n"
            "Found in: Ancient Ruins — Starwell Chamber (final encounter).\n"
            "Tactics: Multi-phase battle. Lyra breaks shield, Zara flanks for sneak "
            "attack damage, Bran targets the rune."
        ),
    },

    "artifacts": {
        "Starwell Relic": (
            "A fist-sized crystal orb covered in glowing silver runes of binding. "
            "When held by someone of pure intent, it pulses with warm white light. "
            "Its purpose is to seal the Shadow Rift beneath the Ancient Ruins. "
            "Attempting to use it for power causes 4d10 psychic damage per attempt. "
            "Currently: LOCATION UNKNOWN (quest objective)."
        ),
        "Crystal of Sight": (
            "A palm-sized prism of blue-grey crystal found in the Darkwood Forest shrine. "
            "When held up to one eye and focused, it reveals hidden runes, invisible "
            "creatures, and the weak points of constructs. Against the Ancient Guardian, "
            "it reveals a glowing chest rune worth double damage. Weight: negligible. "
            "Carried by: party inventory (if found)."
        ),
        "Shadow Blade": (
            "A curved black dagger once belonging to a Shadow Guild assassin. The blade "
            "deals 1d4+2 piercing plus 2d6 necrotic damage. On a critical hit, the "
            "target must make a DC 14 CON save or be blinded for 1 round. "
            "The blade whispers faint, unsettling thoughts to whoever holds it — Zara "
            "is resistant to this effect due to her rogue training. Currently: lootable "
            "from a Shadow Guild enforcer in the Merchant District."
        ),
    },

    "homebrew_rules": {
        "dice_checks": (
            "All skill checks use a d20 roll (random.randint(1,20)).\n"
            "1-4:   Critical Failure — action backfires spectacularly.\n"
            "5-9:   Failure — action fails, possible complication.\n"
            "10-14: Partial Success — action succeeds with a cost or twist.\n"
            "15-19: Full Success — action succeeds cleanly.\n"
            "20:    Critical Success — action exceeds expectations with bonus effect."
        ),
        "combat": (
            "Combat is narrative, not grid-based. The GameMaster narrates outcomes "
            "based on dice rolls and agent suggestions. Each combat encounter involves "
            "one skill check per character action. Party wins if cumulative roll "
            "total exceeds the monster's CR threshold (CR × 5). "
            "Example: Forest Bandit group (CR 1/2 × 4 = CR 2, threshold: 10)."
        ),
        "health_system": (
            "Party health is tracked per character: Bran=30, Lyra=20, Zara=25.\n"
            "Damage is applied narratively based on failed rolls.\n"
            "  Failed roll (5-9): 1d6 damage to the acting character.\n"
            "  Critical failure (1-4): 2d6 damage to the acting character.\n"
            "A healing potion restores 1d8+2 HP. Party members die at 0 HP.\n"
            "A dead party member cannot act; the game ends if all three die."
        ),
    },
}


# =============================================================================
# SHARED GAME STATE — Persisted across all agents each turn
# =============================================================================

game_state = {
    "location": "Moonlit Gate Tavern",
    "active_quest": "Find the Starwell Relic",
    "party_health": {"Bran": 30, "Lyra": 20, "Zara": 25},
    "party_health_max": {"Bran": 30, "Lyra": 20, "Zara": 25},
    "inventory": ["torch", "rope", "healing potion x2"],
    "quest_flags": {},          # e.g. {"journal_found": True, "leyline_decoded": True}
    "turn_count": 0,
    "session_log": [],          # Full history of player actions and GM narrations
    "known_lore": [],           # Lore keys the party has discovered
}


# =============================================================================
# UTILITY: DISPLAY HELPERS
# =============================================================================

def print_banner():
    """Print the game title banner in color."""
    banner = r"""
  ██████╗██╗  ██╗██████╗  ██████╗ ███╗   ██╗██╗ ██████╗██╗     ███████╗███████╗
 ██╔════╝██║  ██║██╔══██╗██╔═══██╗████╗  ██║██║██╔════╝██║     ██╔════╝██╔════╝
 ██║     ███████║██████╔╝██║   ██║██╔██╗ ██║██║██║     ██║     █████╗  ███████╗
 ██║     ██╔══██║██╔══██╗██║   ██║██║╚██╗██║██║██║     ██║     ██╔══╝  ╚════██║
 ╚██████╗██║  ██║██║  ██║╚██████╔╝██║ ╚████║██║╚██████╗███████╗███████╗███████║
  ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝ ╚═════╝╚══════╝╚══════╝╚══════╝
                           ██████╗ ███████╗
                          ██╔═══██╗██╔════╝
                          ██║   ██║█████╗
                          ██║   ██║██╔══╝
                          ╚██████╔╝██║
                           ╚═════╝ ╚═╝
          ██╗   ██╗ █████╗ ██╗     ██████╗ ██████╗ ██╗███████╗
          ██║   ██║██╔══██╗██║     ██╔══██╗██╔══██╗██║██╔════╝
          ██║   ██║███████║██║     ██║  ██║██████╔╝██║███████╗
          ╚██╗ ██╔╝██╔══██║██║     ██║  ██║██╔══██╗██║╚════██║
           ╚████╔╝ ██║  ██║███████╗██████╔╝██║  ██║██║███████║
            ╚═══╝  ╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝╚══════╝
    """
    print(Fore.YELLOW + Style.BRIGHT + banner)
    print(Fore.CYAN + Style.BRIGHT + "  " + "═" * 78)
    print(Fore.CYAN + "  " + " " * 12 + "⚔  Microsoft Agents League Hackathon 2026  ⚔")
    print(Fore.CYAN + "  " + " " * 18 + "Challenge B — Role Play Game System")
    print(Fore.CYAN + Style.BRIGHT + "  " + "═" * 78)
    print()


def print_separator(char="─", color=Fore.WHITE):
    """Print a styled separator line."""
    print(color + char * 80)


def print_section(title: str, color=Fore.CYAN):
    """Print a bold section header."""
    print()
    print(color + Style.BRIGHT + f"  ╔══ {title.upper()} " + "═" * max(0, 60 - len(title)) + "╗")


def wrap_print(text: str, color=Fore.WHITE, indent=4):
    """Word-wrap and print text with optional indent and color."""
    width = 76 - indent
    lines = text.strip().split("\n")
    for line in lines:
        if line.strip() == "":
            print()
            continue
        wrapped = textwrap.wrap(line, width=width)
        for wl in wrapped:
            print(color + " " * indent + wl)


def print_status_bar(name: str, hp: int, max_hp: int, char_color):
    """Print a character health bar."""
    bar_width = 20
    fill = int((hp / max_hp) * bar_width) if max_hp > 0 else 0
    fill = max(0, min(fill, bar_width))
    bar_color = Fore.GREEN if hp > max_hp * 0.5 else (Fore.YELLOW if hp > max_hp * 0.25 else Fore.RED)
    bar = bar_color + "█" * fill + Fore.WHITE + Style.DIM + "░" * (bar_width - fill)
    status = f"  {char_color}{Style.BRIGHT}{name:<6}{Style.RESET_ALL}  HP: {bar_color}{hp:>2}/{max_hp:<2}  [{bar}{Style.RESET_ALL}]"
    print(status)


def show_party_status():
    """Display full party health bars."""
    print_section("Party Status", Fore.GREEN)
    print_status_bar("Bran",  game_state["party_health"]["Bran"],  game_state["party_health_max"]["Bran"],  Fore.RED)
    print_status_bar("Lyra",  game_state["party_health"]["Lyra"],  game_state["party_health_max"]["Lyra"],  Fore.MAGENTA)
    print_status_bar("Zara",  game_state["party_health"]["Zara"],  game_state["party_health_max"]["Zara"],  Fore.CYAN)
    print()


def show_inventory():
    """Display current party inventory."""
    print_section("Inventory", Fore.YELLOW)
    if not game_state["inventory"]:
        wrap_print("(empty)", Fore.WHITE + Style.DIM)
    else:
        for i, item in enumerate(game_state["inventory"], 1):
            print(Fore.YELLOW + f"    [{i}] " + Fore.WHITE + item)
    print()


def show_quest_flags():
    """Display current quest progress flags."""
    print_section("Quest Progress", Fore.CYAN)
    wrap_print(f"Active Quest: {game_state['active_quest']}", Fore.WHITE)
    wrap_print(f"Location:     {game_state['location']}", Fore.WHITE)
    if game_state["quest_flags"]:
        print(Fore.CYAN + "    Milestones:")
        for flag, value in game_state["quest_flags"].items():
            icon = Fore.GREEN + "✓" if value else Fore.RED + "✗"
            print(f"      {icon} {Fore.WHITE}{flag.replace('_', ' ').title()}")
    else:
        wrap_print("No milestones reached yet.", Fore.WHITE + Style.DIM)
    print()


def roll_dice(sides: int = 20, label: str = "Skill Check") -> int:
    """Roll a dice, display result, return value."""
    result = random.randint(1, sides)
    if result == sides:
        grade = Fore.YELLOW + Style.BRIGHT + "✦ CRITICAL SUCCESS! ✦"
    elif result >= 15:
        grade = Fore.GREEN + "✔ Full Success"
    elif result >= 10:
        grade = Fore.CYAN + "~ Partial Success"
    elif result >= 5:
        grade = Fore.RED + "✘ Failure"
    else:
        grade = Fore.RED + Style.BRIGHT + "☠ CRITICAL FAILURE!"
    print(Fore.WHITE + f"    🎲 [{label}] Rolling d{sides}... " + Fore.YELLOW + Style.BRIGHT + str(result) + Fore.WHITE + f"  →  {grade}" + Style.RESET_ALL)
    time.sleep(0.4)
    return result


def apply_damage(character: str, roll: int):
    """Apply damage to a character based on their roll result (homebrew rules)."""
    if roll <= 4:   # Critical failure
        dmg = random.randint(1, 6) + random.randint(1, 6)
        game_state["party_health"][character] = max(0, game_state["party_health"][character] - dmg)
        print(Fore.RED + Style.BRIGHT + f"    ⚠  {character} takes {dmg} damage from a critical failure! (HP: {game_state['party_health'][character]})")
    elif roll <= 9:  # Failure
        dmg = random.randint(1, 6)
        game_state["party_health"][character] = max(0, game_state["party_health"][character] - dmg)
        print(Fore.RED + f"    ⚠  {character} takes {dmg} damage. (HP: {game_state['party_health'][character]})")


def use_healing_potion(character: str) -> bool:
    """Use a healing potion if available. Returns True if used."""
    if "healing potion x2" in game_state["inventory"]:
        heal = random.randint(1, 8) + 2
        game_state["party_health"][character] = min(
            game_state["party_health_max"][character],
            game_state["party_health"][character] + heal
        )
        # Remove one potion use
        game_state["inventory"].remove("healing potion x2")
        remaining = sum(1 for i in game_state["inventory"] if "healing potion" in i)
        if remaining > 0:
            game_state["inventory"].append(f"healing potion x{remaining}")
        print(Fore.GREEN + f"    💊 {character} uses a healing potion and recovers {heal} HP! (HP: {game_state['party_health'][character]})")
        return True
    elif "healing potion x1" in game_state["inventory"]:
        heal = random.randint(1, 8) + 2
        game_state["party_health"][character] = min(
            game_state["party_health_max"][character],
            game_state["party_health"][character] + heal
        )
        game_state["inventory"].remove("healing potion x1")
        print(Fore.GREEN + f"    💊 {character} uses the last healing potion and recovers {heal} HP! (HP: {game_state['party_health'][character]})")
        return True
    return False


def check_party_alive() -> bool:
    """Return True if at least one party member is alive."""
    return any(hp > 0 for hp in game_state["party_health"].values())


def show_session_summary():
    """Display end-of-session summary."""
    print_section("Session Summary", Fore.YELLOW)
    wrap_print(f"Total Turns Played: {game_state['turn_count']}", Fore.WHITE)
    wrap_print(f"Final Location: {game_state['location']}", Fore.WHITE)
    print()
    print(Fore.CYAN + Style.BRIGHT + "    Party Final Status:")
    for name, hp in game_state["party_health"].items():
        status = Fore.GREEN + "Alive" if hp > 0 else Fore.RED + "Fallen"
        print(f"      {Fore.WHITE}{name}: {status} {Fore.WHITE}(HP: {hp})")
    print()
    print(Fore.YELLOW + Style.BRIGHT + "    Quest Milestones Achieved:")
    if game_state["quest_flags"]:
        for flag, val in game_state["quest_flags"].items():
            icon = "✓" if val else "✗"
            print(f"      {icon} {flag.replace('_', ' ').title()}")
    else:
        wrap_print("None yet — the quest continues!", Fore.WHITE + Style.DIM)
    print()
    print(Fore.WHITE + Style.DIM + "    Session Log (last 10 actions):")
    for entry in game_state["session_log"][-10:]:
        print(Fore.WHITE + Style.DIM + f"      • {entry}")
    print()
    print_separator("═", Fore.YELLOW)
    print(Fore.YELLOW + Style.BRIGHT + "  Thank you for playing Chronicles of Valdris!")
    print(Fore.CYAN + "  Microsoft Agents League Hackathon 2026 | Challenge B")
    print_separator("═", Fore.YELLOW)


# =============================================================================
# GEMINI API SETUP
# =============================================================================

def setup_gemini():
    """Initialize and return the Gemini client, or None on failure."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_key_here":
        print(Fore.YELLOW + Style.BRIGHT + "\n  [!] No GEMINI_API_KEY found in .env file.")
        print(Fore.YELLOW + "  Running in OFFLINE DEMO mode (pre-scripted responses).")
        print(Fore.WHITE + "  To use live AI, create a .env file with your Gemini API key.\n")
        return None
    try:
        client = genai.Client(api_key=api_key)
        # Quick connectivity test
        client.models.generate_content(
            model="gemini-1.5-flash",
            contents="Say: ONLINE"
        )
        print(Fore.GREEN + Style.BRIGHT + "\n  [✓] Gemini 1.5 Flash API connected successfully.\n")
        return client
    except Exception as e:
        print(Fore.YELLOW + f"\n  [!] Gemini API error: {e}")
        print(Fore.YELLOW + "  Falling back to OFFLINE DEMO mode.\n")
        return None


# =============================================================================
# BASE AGENT CLASS
# =============================================================================

class BaseAgent:
    """
    Abstract base class for all RPG agents.
    Each agent holds a system_prompt defining its personality,
    and a respond() method that calls Gemini (or offline fallback).
    """

    def __init__(self, name: str, system_prompt: str, model, color):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model            # Gemini model reference (may be None in offline mode)
        self.color = color            # Colorama color for this agent's output
        self.conversation_history = []  # Per-agent conversation history for context

    def respond(self, context: str, player_action: str) -> str:
        """
        Generate a response given the current game context and player action.
        Uses Gemini if available; otherwise returns a pre-scripted fallback.
        """
        if self.model is None:
            # Offline demo mode — use fallback responses
            return self._offline_fallback(player_action)

        # Build the full prompt: system + context + player action
        prompt = (
            f"{self.system_prompt}\n\n"
            f"=== CURRENT GAME CONTEXT ===\n{context}\n\n"
            f"=== PLAYER ACTION ===\n{player_action}\n\n"
            f"Respond in character (2-4 sentences). Be vivid, specific to the world of Valdris, "
            f"and advance the story. Stay under 100 words."
        )

        try:
            # One Gemini API call per agent response — efficient for free tier
            response = self.model.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.85,
                    max_output_tokens=900,
                    top_p=0.95,
                )
            )
            return response.text.strip()
        except Exception as e:
            # Graceful API error handling — fall back to scripted response
            print(Fore.YELLOW + Style.DIM + f"    [API fallback for {self.name}: {e}]")
            return self._offline_fallback(player_action)

    def _offline_fallback(self, player_action: str) -> str:
        """Override in subclasses for character-specific offline responses."""
        return f"[{self.name} considers the situation carefully...]"

    def print_response(self, text: str):
        """Pretty-print an agent's response with their name label."""
        print()
        print(self.color + Style.BRIGHT + f"  ┌── {self.name} ──")
        print(self.color + "  │")
        for line in text.strip().split("\n"):
            wrapped = textwrap.wrap(line, width=72)
            for wl in wrapped:
                print(self.color + "  │  " + Style.RESET_ALL + wl)
        print(self.color + "  └" + "─" * 60)
        print()


# =============================================================================
# AGENT 1: GAME MASTER (Orchestrator)
# =============================================================================

class GameMasterAgent(BaseAgent):
    """
    The GameMasterAgent is the central orchestrator of Chronicles of Valdris.
    It receives player input, queries WORLD_LORE, decides which character
    agents respond, rolls dice, updates game_state, and narrates the scene.
    This mirrors the pattern of an AI orchestrator managing sub-agents
    via tool calls in a Microsoft Agents League architecture.
    """

    GM_SYSTEM_PROMPT = """
You are the Game Master of Chronicles of Valdris, a high-fantasy RPG world.
Your role: narrate the scene vividly, incorporate the party's responses,
describe the consequences of dice rolls, and update the world accordingly.

Tone: Epic, immersive, second-person ("You see...", "The party finds...").
Style: Rich descriptions, sensory details (sounds, smells, textures).
Rules:
 - Always acknowledge the player's action.
 - Integrate Bran's, Lyra's, and Zara's responses naturally into the narration.
 - Describe dice roll consequences clearly (success/failure/critical).
 - End every narration with exactly 3-4 numbered player choices.
 - Keep narration to 150-200 words maximum.
 - Never break the fourth wall or mention AI.
"""

    SCENE_INTRO = """
The city of Valdris hums with nervous energy as you push open the heavy oak
door of the Moonlit Gate Tavern. Lantern light spills across worn flagstones;
the smell of hearth smoke and roasted game fills your lungs. At the far end
of the common room, your companions wait at a corner table — Bran Ironvale
sharpening his blade, Lyra Vey reading from a cracked tome, and Zara
Nightwhisper watching the door with quiet, predatory calm.

A hunched figure in a grey cloak approaches your table and slides a rolled
parchment across the scarred wood. It bears the royal seal of House Valdris.
The message is brief: "Find the Starwell Relic. The realm depends on it."
Zara pockets the parchment before anyone else can see it, eyebrow raised.
"""

    def __init__(self, warrior: "WarriorAgent", mage: "MageAgent", rogue: "RogueAgent", model):
        super().__init__(
            name="⚔  Game Master",
            system_prompt=self.GM_SYSTEM_PROMPT,
            model=model,
            color=Fore.WHITE
        )
        # Sub-agents: the GM calls on these as needed
        self.warrior = warrior
        self.mage    = mage
        self.rogue   = rogue

    def query_lore(self, player_action: str) -> str:
        """
        Simulate Foundry IQ local retrieval: scan WORLD_LORE for context
        relevant to the player's action keywords. Returns a summary string.
        This is the RAG (Retrieval-Augmented Generation) simulation layer.
        """
        action_lower = player_action.lower()
        retrieved = []

        # Keyword-based lore retrieval — simulates vector similarity search
        keyword_map = {
            ("tavern", "inn", "drink", "ale", "barkeep", "orwen", "door", "enter"):
                ("location_moonlit_gate", WORLD_LORE["locations"]["Moonlit Gate Tavern"]),
            ("forest", "darkwood", "tree", "bandits", "woods", "grove"):
                ("location_darkwood", WORLD_LORE["locations"]["Darkwood Forest"]),
            ("city", "valdris city", "market", "noble", "ward", "district", "king", "palace"):
                ("location_valdris_city", WORLD_LORE["locations"]["Valdris City"]),
            ("ruins", "ancient", "starwell", "guardian", "rift", "east"):
                ("location_ruins", WORLD_LORE["locations"]["Ancient Ruins"]),
            ("order", "silver root", "archon", "serevyn", "scholar", "mage faction"):
                ("faction_order", WORLD_LORE["factions"]["Order of Silver Root"]),
            ("shadow guild", "mira", "merchant", "criminal", "assassin", "guild"):
                ("faction_guild", WORLD_LORE["factions"]["Shadow Guild"]),
            ("king", "royal", "aldric", "lord", "lordship", "decree", "kingdom"):
                ("faction_royal", WORLD_LORE["factions"]["Royal House of Valdris"]),
            ("relic", "starwell", "quest", "dorath", "seal", "rift", "orb"):
                ("main_quest", WORLD_LORE["main_quest"]),
            ("wraith", "shadow creature", "ghost", "undead"):
                ("monster_wraith", WORLD_LORE["monsters"]["Shadow Wraith"]),
            ("golem", "stone", "construct", "shrine"):
                ("monster_golem", WORLD_LORE["monsters"]["Stone Golem"]),
            ("bandit", "thief", "outlaw", "road", "ambush"):
                ("monster_bandit", WORLD_LORE["monsters"]["Forest Bandit"]),
            ("guardian", "boss", "colossus", "final", "chamber"):
                ("monster_guardian", WORLD_LORE["monsters"]["Ancient Guardian"]),
            ("crystal", "crystal of sight", "prism", "reveal", "hidden"):
                ("artifact_crystal", WORLD_LORE["artifacts"]["Crystal of Sight"]),
            ("shadow blade", "dagger", "black blade", "whisper"):
                ("artifact_shadow_blade", WORLD_LORE["artifacts"]["Shadow Blade"]),
            ("rules", "dice", "roll", "combat", "health", "potion", "heal"):
                ("homebrew_rules", str(WORLD_LORE["homebrew_rules"])),
        }

        for keywords, (lore_key, lore_text) in keyword_map.items():
            if any(kw in action_lower for kw in keywords):
                if lore_key not in game_state["known_lore"]:
                    game_state["known_lore"].append(lore_key)
                retrieved.append(lore_text)

        # Always include world overview for first 3 turns
        if game_state["turn_count"] <= 3:
            retrieved.insert(0, WORLD_LORE["world_overview"])

        if not retrieved:
            retrieved.append(
                f"Current location: {game_state['location']}. "
                f"Active quest: {game_state['active_quest']}."
            )

        return "\n\n---\n\n".join(retrieved[:3])  # Cap at 3 lore chunks to keep prompt lean

    def decide_agents(self, player_action: str) -> list:
        """
        Decide which character agents should respond to this action.
        Mirrors an orchestrator dispatching tasks to sub-agents.
        Combat → Warrior; Magic/Lore → Mage; Stealth/Scouting → Rogue.
        """
        action_lower = player_action.lower()
        responding = []

        # Combat, danger, fight keywords → Bran responds
        combat_words = ["fight", "attack", "charge", "battle", "sword", "weapon",
                        "defend", "combat", "monster", "golem", "wraith", "bandit",
                        "guardian", "tavern brawl", "strike", "hit", "kill", "confront"]
        if any(w in action_lower for w in combat_words):
            responding.append(self.warrior)

        # Magic, lore, relic, puzzle keywords → Lyra responds
        magic_words = ["magic", "spell", "relic", "rune", "lore", "book", "tome",
                       "crystal", "arcane", "ley", "decode", "journal", "translate",
                       "investigate", "study", "research", "identify", "ancient",
                       "rift", "starwell", "seal", "glow", "enchant"]
        if any(w in action_lower for w in magic_words):
            responding.append(self.mage)

        # Stealth, scouting, social, trap keywords → Zara responds
        stealth_words = ["sneak", "scout", "hide", "trap", "pick", "lock", "shadow",
                         "listen", "watch", "follow", "stalk", "observe", "search",
                         "merchant", "guild", "bribe", "persuade", "bluff", "steal",
                         "secret", "notice", "door", "chest", "passage", "alley"]
        if any(w in action_lower for w in stealth_words):
            responding.append(self.rogue)

        # Default: if no agent matched, pick 2 randomly for organic feel
        if not responding:
            responding = random.sample([self.warrior, self.mage, self.rogue], k=2)

        # Cap at 2 agents per turn to keep output focused
        return responding[:2]

    def update_game_state(self, player_action: str, roll: int):
        """
        Update game_state based on the player's action and dice roll.
        Handles location transitions and quest flag progression.
        """
        action_lower = player_action.lower()

        # --- Location transitions ---
        location_triggers = {
            "darkwood":  "Darkwood Forest",
            "forest":    "Darkwood Forest",
            "ruins":     "Ancient Ruins",
            "ancient":   "Ancient Ruins",
            "city":      "Valdris City",
            "palace":    "Valdris City",
            "tavern":    "Moonlit Gate Tavern",
            "inn":       "Moonlit Gate Tavern",
        }
        for keyword, location in location_triggers.items():
            if keyword in action_lower and game_state["location"] != location:
                if roll >= 10:   # Partial success or better to travel
                    game_state["location"] = location
                    print(Fore.CYAN + f"\n  📍 Location updated: {location}")
                break

        # --- Quest flag progression ---
        if "journal" in action_lower and roll >= 10:
            game_state["quest_flags"]["journal_found"] = True
        if ("decode" in action_lower or "ley" in action_lower or "leyline" in action_lower) and roll >= 10:
            game_state["quest_flags"]["leyline_decoded"] = True
        if ("crystal" in action_lower or "crystal of sight" in action_lower) and roll >= 15:
            game_state["quest_flags"]["crystal_obtained"] = True
            if "Crystal of Sight" not in game_state["inventory"]:
                game_state["inventory"].append("Crystal of Sight")
                print(Fore.YELLOW + "  🎒 Crystal of Sight added to inventory!")
        if ("shadow blade" in action_lower or "black dagger" in action_lower) and roll >= 12:
            game_state["quest_flags"]["shadow_blade_found"] = True
            if "Shadow Blade" not in game_state["inventory"]:
                game_state["inventory"].append("Shadow Blade")
                print(Fore.YELLOW + "  🎒 Shadow Blade added to inventory!")
        if ("guardian" in action_lower or "ancient guardian" in action_lower) and roll >= 15:
            game_state["quest_flags"]["guardian_defeated"] = True
        if ("relic" in action_lower or "starwell relic" in action_lower) and roll >= 18:
            game_state["quest_flags"]["relic_found"] = True
            if "Starwell Relic" not in game_state["inventory"]:
                game_state["inventory"].append("Starwell Relic")
                print(Fore.YELLOW + Style.BRIGHT + "  🌟 THE STARWELL RELIC has been recovered!")
        if ("seal" in action_lower or "return" in action_lower) and \
                game_state["quest_flags"].get("relic_found") and roll >= 12:
            game_state["quest_flags"]["rift_sealed"] = True

        # --- Apply combat damage on low rolls ---
        if roll <= 9 and any(w in action_lower for w in ["fight", "attack", "charge", "confront", "engage"]):
            active_chars = [c for c, hp in game_state["party_health"].items() if hp > 0]
            if active_chars:
                hit_char = random.choice(active_chars)
                apply_damage(hit_char, roll)

        # --- Log the action ---
        game_state["session_log"].append(
            f"[Turn {game_state['turn_count']}] {player_action[:60]}... (roll: {roll})"
        )
        game_state["turn_count"] += 1

    def build_context(self, lore: str) -> str:
        """Build a concise context string for sub-agent prompts."""
        alive = {k: v for k, v in game_state["party_health"].items() if v > 0}
        return (
            f"Location: {game_state['location']}\n"
            f"Quest: {game_state['active_quest']}\n"
            f"Party HP — Bran: {game_state['party_health']['Bran']}, "
            f"Lyra: {game_state['party_health']['Lyra']}, "
            f"Zara: {game_state['party_health']['Zara']}\n"
            f"Inventory: {', '.join(game_state['inventory'])}\n"
            f"Quest flags: {game_state['quest_flags']}\n"
            f"Relevant Lore:\n{lore[:600]}"
        )

    def run_turn(self, player_action: str):
        """
        Main orchestration method — executes one full game turn:
        1. Query lore  2. Roll dice  3. Call sub-agents
        4. Update state  5. Narrate scene  6. Show choices
        """
        print_separator("─", Fore.WHITE + Style.DIM)
        print()

        # ── STEP 1: Retrieve relevant world lore (Foundry IQ simulation) ──
        lore = self.query_lore(player_action)

        # ── STEP 2: Roll dice for the player's action ──
        print(Fore.WHITE + Style.DIM + "  [Resolving action...]")
        roll = roll_dice(20, player_action[:30])

        # ── STEP 3: Determine which agents respond ──
        responding_agents = self.decide_agents(player_action)
        context = self.build_context(lore)

        # ── STEP 4: Collect character agent responses ──
        agent_responses = []
        for agent in responding_agents:
            print(Fore.WHITE + Style.DIM + f"  [Consulting {agent.name.strip()}...]")
            response = agent.respond(context, player_action)
            agent.print_response(response)
            agent_responses.append(f"{agent.name.strip()}: {response}")

        # ── STEP 5: Update game state (location, flags, damage) ──
        self.update_game_state(player_action, roll)

        # ── STEP 6: GameMaster narrates the final scene ──
        print_section("Narration", Fore.WHITE)
        gm_context = (
            f"{context}\n\n"
            f"Player action: {player_action}\n"
            f"Dice roll: {roll}/20\n"
            f"Agent responses:\n" + "\n".join(agent_responses)
        )
        narration = self.respond(gm_context, player_action)
        wrap_print(narration, Fore.WHITE)

        # ── STEP 7: Show choices and status ──
        self._show_suggested_choices(roll, player_action)
        show_party_status()

        # Victory condition check
        if game_state["quest_flags"].get("rift_sealed"):
            self._victory_sequence()

    def _show_suggested_choices(self, roll: int, player_action: str):
        """Display contextual player choices based on current state."""
        print_section("Your Choices", Fore.CYAN)
        location = game_state["location"]

        choices = {
            "Moonlit Gate Tavern": [
                "1. Search the tavern basement for Dorath's journal",
                "2. Ask Orwen the barkeep about the Starwell Relic",
                "3. Head to the Darkwood Forest to investigate",
                "4. Sneak into the Merchant District to find the Shadow Guild",
            ],
            "Darkwood Forest": [
                "1. Search for the ley-line grove to decode the journal",
                "2. Scout the road ahead for Forest Bandits",
                "3. Investigate the stone shrine deeper in the woods",
                "4. Return to Valdris City to resupply",
            ],
            "Valdris City": [
                "1. Visit the Order of Silver Root headquarters for information",
                "2. Confront the Shadow Guild agent in the Merchant District",
                "3. Request an audience with King Aldric at the Royal Palace",
                "4. Head east toward the Ancient Ruins",
            ],
            "Ancient Ruins": [
                "1. Fight through to the Starwell Chamber",
                "2. Investigate the outer ruins for the Crystal of Sight",
                "3. Try to sneak past the Ancient Guardian",
                "4. Use the Crystal of Sight to find the Guardian's weak point",
            ],
        }

        current_choices = choices.get(location, choices["Moonlit Gate Tavern"])
        for choice in current_choices:
            print(Fore.CYAN + f"    {choice}")

        print()
        print(Fore.WHITE + Style.DIM + "    Commands: 'status' · 'inventory' · 'quit' · or type any action")
        print()

    def _offline_fallback(self, player_action: str) -> str:
        """Scripted GM narrations for offline demo mode."""
        location = game_state["location"]
        fallbacks = {
            "Moonlit Gate Tavern": (
                "The Moonlit Gate Tavern thrums with evening conversation. Smoke from "
                "the hearth curls toward the rafters. Orwen, the barrel-chested barkeep, "
                "polishes a tankard with practised indifference as you lay out your plan. "
                "Bran's hand rests on his sword pommel — old habit. Lyra traces a rune on "
                "the table with one finger, lost in thought. Zara's gaze flicks to the "
                "back room where two cloaked figures watch you with unsettling interest. "
                "'We're already being observed,' she murmurs. 'Whatever we do next, we do "
                "it carefully.'\n\n"
                "What is your next move?"
            ),
            "Darkwood Forest": (
                "Darkwood Forest closes around you like a fist. The canopy seals out the "
                "sun and replaces it with a greenish, underwater gloom. Somewhere to the "
                "north, a twig snaps. Bran raises his fist — the signal to halt. Lyra "
                "whispers that she can feel arcane energy thrumming underfoot, close now. "
                "Zara materialises from the shadows, expression tight. 'Three bandits on "
                "the ridge. They haven't spotted us yet.' The air smells of damp earth "
                "and something older — stone, and magic.\n\nWhat do you do?"
            ),
            "Valdris City": (
                "Valdris City buzzes around you. The Noble Quarter's white spires gleam "
                "in afternoon light while the Outer Ward's alleyways simmer with tension. "
                "A city guard patrol rounds the corner ahead; Zara steers you smoothly "
                "into a side street. 'Word travels fast here,' she warns. 'The Shadow "
                "Guild already knows we're in the city.' Lyra's eyes are on the Order of "
                "Silver Root tower. 'Archon Serevyn could help us decode the journal.' "
                "Bran grunts. 'Or we go straight to the Palace and demand answers.'\n\n"
                "What do you do?"
            ),
            "Ancient Ruins": (
                "The Ancient Ruins loom against a bruised sky. Crumbled arches reach "
                "skyward like broken fingers; shadow creatures drift between the pillars, "
                "not yet aware of your presence. At the ruin's heart, you can see the "
                "Starwell — a perfect circle of darkness breathing cold air upward. "
                "The Ancient Guardian stands motionless before it, stone eyes fixed "
                "forward. Lyra whispers urgently: 'The Rune Shield is active. I need "
                "two full casting sequences to break it.' Bran draws his sword. Zara "
                "is already circling left, silent as smoke.\n\nThe final battle begins."
            ),
        }
        return fallbacks.get(location, fallbacks["Moonlit Gate Tavern"])

    def _victory_sequence(self):
        """Display the victory ending sequence."""
        print()
        print_separator("═", Fore.YELLOW)
        print(Fore.YELLOW + Style.BRIGHT + """
  ✦ ✦ ✦  VICTORY — THE RIFT IS SEALED  ✦ ✦ ✦

  The Starwell Relic pulses with blinding white light as you place it
  into the Starwell's receptacle. A deep resonant tone shakes the ruins.
  The Shadow Rift — that gaping wound in reality — contracts with a sound
  like a dying storm, and then... silence.

  A messenger hawk arrives within the hour bearing the royal seal.
  King Aldric III honours his decree: the party receives a lordship
  in the Greenfield Valley and 10,000 gold coins.

  Bran stands straighter than you've ever seen him.
  Lyra is already writing her account of the arcane mechanism.
  Zara counts her share of the gold with a rare, satisfied smile.

  Valdris is safe. For now.
        """)
        print_separator("═", Fore.YELLOW)
        show_session_summary()
        sys.exit(0)


# =============================================================================
# AGENT 2: WARRIOR — Bran Ironvale
# =============================================================================

class WarriorAgent(BaseAgent):
    """
    Bran Ironvale: Brave, fiercely protective, deeply suspicious of magic.
    He speaks plainly, acts decisively, and measures every situation
    through the lens of threat assessment and tactical advantage.
    """

    WARRIOR_SYSTEM_PROMPT = """
You are Bran Ironvale, a veteran warrior in the world of Valdris.
Personality: Brave, blunt, protective of the party, deeply suspicious of magic
and magic-users (though you trust Lyra more than strangers).
Speech style: Direct, short sentences. Military vocabulary. Occasional dry humour.
You never suggest retreat without exhausting every other option.
Your specialty: combat tactics, threat assessment, defending the party.
Never speak more than 3 sentences. Always assess threats first.
World context: You are in Valdris, on a quest to find the Starwell Relic.
"""

    OFFLINE_RESPONSES = [
        "Straight steel and steady nerve — that's all this situation needs. "
        "I've faced worse odds in the Greymarch campaign. Let them come.",

        "That magic energy Lyra's sensing puts my teeth on edge. "
        "I'll take point. Whatever's ahead, I hit it first.",

        "Three enemies on the ridge. Classic pincer formation. "
        "We take the left flank, draw them down, and Zara finishes the right. Simple.",

        "I don't like it. Too quiet. In my experience, too quiet means "
        "something's already in position. Stay close.",

        "The Guardian's stone. My sword won't bite unless Lyra breaks that shield. "
        "I'll keep it busy — take the hits so she can cast. Do it fast.",

        "Bandits on the road. I've intimidated worse. Let me walk ahead, "
        "alone. Most men lose their nerve when they see a drawn sword and "
        "a face that's stopped caring.",
    ]

    def __init__(self, model):
        super().__init__(
            name="⚔  Bran Ironvale",
            system_prompt=self.WARRIOR_SYSTEM_PROMPT,
            model=model,
            color=Fore.RED
        )

    def _offline_fallback(self, player_action: str) -> str:
        """Return a random scripted Bran response for offline mode."""
        return random.choice(self.OFFLINE_RESPONSES)


# =============================================================================
# AGENT 3: MAGE — Lyra Vey
# =============================================================================

class MageAgent(BaseAgent):
    """
    Lyra Vey: Brilliant, analytically precise, slightly condescending about
    non-magical solutions. She is the party's lore expert and the only one
    who fully understands the Starwell Relic's mechanics.
    """

    MAGE_SYSTEM_PROMPT = """
You are Lyra Vey, an arcane mage in the world of Valdris.
Personality: Highly intelligent, analytical, slightly arrogant about magical matters.
You find mundane solutions "quaint" but recognise their utility.
You are deeply fascinated by the Starwell Relic and the Shadow Rift.
Speech style: Precise vocabulary, occasional Latin-sounding arcane terms,
references to magical theory. You do not apologise for being right.
Your specialty: magical analysis, lore interpretation, arcane combat.
Never speak more than 3 sentences. Always identify the magical angle first.
World context: You are in Valdris, analysing the arcane resonance of the Starwell Relic.
"""

    OFFLINE_RESPONSES = [
        "Fascinating — the arcane residue here matches the resonance pattern I found "
        "in Dorath's annotations. The Relic was here within the last decade. "
        "I can triangulate its current location if given thirty minutes and quiet.",

        "The ley-line beneath this forest is remarkably well-preserved. "
        "I can channel it to amplify my detection spells tenfold. "
        "Bran, please stop shuffling — your iron boots disrupt the harmonic.",

        "Stone Golems are immune to non-magical attacks — I trust Bran absorbed "
        "that detail the first three times I mentioned it. I'll lead. "
        "My arcane bolts should suffice for its joint seams.",

        "The journal's cipher uses a modified Valdrian Imperial script — "
        "discontinued in the third dynasty. I've already decoded the relevant passages. "
        "The Relic was hidden in three pieces, not one. Inconvenient.",

        "That Shadow Wraith is weakened by radiant energy. Hold the torch higher, Bran. "
        "I'll recite the binding verse — it should immobilise the creature long enough "
        "for a decisive strike.",

        "The Rune Shield around the Ancient Guardian operates on a resonance lock. "
        "Two full arcane discharges, precisely timed, will shatter it. "
        "Do not interrupt me mid-cast unless you enjoy stone fists.",
    ]

    def __init__(self, model):
        super().__init__(
            name="✦  Lyra Vey",
            system_prompt=self.MAGE_SYSTEM_PROMPT,
            model=model,
            color=Fore.MAGENTA
        )

    def _offline_fallback(self, player_action: str) -> str:
        return random.choice(self.OFFLINE_RESPONSES)


# =============================================================================
# AGENT 4: ROGUE — Zara Nightwhisper
# =============================================================================

class RogueAgent(BaseAgent):
    """
    Zara Nightwhisper: Street-smart, witty, perpetually skeptical of
    authority and optimism alike. She is the party's eyes and ears,
    excelling at stealth, traps, social engineering, and finding
    the angle everyone else missed.
    """

    ROGUE_SYSTEM_PROMPT = """
You are Zara Nightwhisper, a rogue and scout in the world of Valdris.
Personality: Witty, deeply skeptical, pragmatic. You distrust authority,
grand plans, and anyone who smiles too much. You are, however, absolutely
loyal to the party — you just express it through sarcasm.
Speech style: Dry wit, rhetorical questions, observational humour.
You notice what others miss — social cues, physical details, exits.
Your specialty: scouting, trap detection, stealth, social manipulation.
Never speak more than 3 sentences. Always notice the overlooked detail.
World context: You are in Valdris, keeping the party alive through caution.
"""

    OFFLINE_RESPONSES = [
        "I've already counted four exits, two hidden watchers, and one very nervous "
        "informant by the fire — he's been staring at us since we walked in. "
        "Should I go have a friendly conversation with him?",

        "The 'merchant' who followed us from the Tavern gate? Shadow Guild. "
        "The emblem on his boot gave it away. We've been made. "
        "I suggest we make the next move before they do.",

        "There's a trap on that door — pressure plate, third flagstone from the left. "
        "Also, the lock's a Valdrian Imperial-era mechanism. Give me forty seconds "
        "and try not to breathe loudly.",

        "Lyra's plan is theoretically brilliant and practically going to get us killed. "
        "Let me scout the east passage first — if the Guardian has a blind spot, "
        "I'll find it.",

        "Optimism is adorable. Meanwhile, I'll be on the roof checking sight lines. "
        "If anyone's tracking us, they're using the market crowd as cover. "
        "I'll flush them out.",

        "The barkeep hesitated for exactly two seconds when you mentioned Dorath's name. "
        "He knows something. Buy him a drink — let me watch his hands while he pours.",
    ]

    def __init__(self, model):
        super().__init__(
            name="🗡  Zara Nightwhisper",
            system_prompt=self.ROGUE_SYSTEM_PROMPT,
            model=model,
            color=Fore.CYAN
        )

    def _offline_fallback(self, player_action: str) -> str:
        return random.choice(self.OFFLINE_RESPONSES)


# =============================================================================
# MAIN GAME LOOP
# =============================================================================

def print_intro(gm: GameMasterAgent):
    """Print the game introduction and opening scene."""
    print_banner()
    time.sleep(0.5)

    print_section("Welcome, Adventurer", Fore.YELLOW)
    print()
    wrap_print(
        "You stand at the threshold of a legend. The realm of Valdris teeters on "
        "the edge of shadow, and only you — and three unlikely companions — stand "
        "between the world and the consuming dark of the Shadow Rift.",
        Fore.YELLOW
    )
    print()
    wrap_print(
        "Commands available at any time:",
        Fore.WHITE + Style.DIM
    )
    print(Fore.WHITE + Style.DIM + "    status    — Show party health")
    print(Fore.WHITE + Style.DIM + "    inventory — Check your items")
    print(Fore.WHITE + Style.DIM + "    quest     — Show quest progress")
    print(Fore.WHITE + Style.DIM + "    quit      — End session & show summary")
    print()
    input(Fore.CYAN + Style.BRIGHT + "  Press ENTER to begin your adventure..." + Style.RESET_ALL)

    print_section("Opening Scene", Fore.WHITE)
    print()
    # Animate the opening scene text character by character for drama
    scene = gm.SCENE_INTRO.strip()
    for char in scene:
        print(Fore.WHITE + char, end="", flush=True)
        if char in ".!?":
            time.sleep(0.04)
        elif char == "\n":
            time.sleep(0.01)
        else:
            time.sleep(0.005)
    print()
    print()

    show_party_status()

    print(Fore.CYAN + Style.BRIGHT + "\n  " + "─" * 78)
    wrap_print(
        "What do you do? (Type freely — the world responds to your actions.)",
        Fore.CYAN + Style.BRIGHT
    )
    print()


def main():
    """
    Entry point for Chronicles of Valdris.
    Sets up agents, runs the game loop, handles special commands.
    """
    # ── Initialise Gemini API ──
    model = setup_gemini()

    # ── Instantiate all four agents ──
    warrior = WarriorAgent(model)
    mage    = MageAgent(model)
    rogue   = RogueAgent(model)
    gm      = GameMasterAgent(warrior, mage, rogue, model)

    # ── Print intro and opening scene ──
    print_intro(gm)

    # ── Main game loop ──
    while True:
        try:
            # Get player input
            player_input = input(Fore.GREEN + Style.BRIGHT + "  ➤  " + Style.RESET_ALL).strip()

            if not player_input:
                print(Fore.WHITE + Style.DIM + "  (The world waits. What do you do?)")
                continue

            # ── Special commands ──
            cmd = player_input.lower()

            if cmd == "quit" or cmd == "exit":
                print()
                show_session_summary()
                break

            elif cmd == "status":
                show_party_status()
                continue

            elif cmd == "inventory":
                show_inventory()
                continue

            elif cmd == "quest":
                show_quest_flags()
                continue

            elif cmd.startswith("heal "):
                # Allow player to manually use healing potion
                target = cmd[5:].strip().capitalize()
                if target in game_state["party_health"]:
                    if not use_healing_potion(target):
                        print(Fore.RED + "  No healing potions remaining!")
                else:
                    print(Fore.RED + f"  Unknown party member: {target}. Use 'heal Bran', 'heal Lyra', or 'heal Zara'.")
                continue

            elif cmd == "help":
                print()
                wrap_print("Available commands:", Fore.WHITE + Style.BRIGHT)
                print(Fore.WHITE + "    status        — Show party health bars")
                print(Fore.WHITE + "    inventory     — List your items")
                print(Fore.WHITE + "    quest         — Show quest progress & flags")
                print(Fore.WHITE + "    heal [name]   — Use a healing potion on Bran/Lyra/Zara")
                print(Fore.WHITE + "    quit          — End session & show summary")
                print(Fore.WHITE + "    (anything else) — Take that action in the world")
                print()
                continue

            # Check party is still alive
            if not check_party_alive():
                print()
                print(Fore.RED + Style.BRIGHT + "  ☠  THE PARTY HAS FALLEN.")
                print(Fore.RED + "  The Shadow Rift swallows Valdris. The world grows dark.")
                print()
                show_session_summary()
                break

            # ── Run the full agent turn ──
            gm.run_turn(player_input)

        except KeyboardInterrupt:
            print()
            print(Fore.YELLOW + "\n  [Interrupted] Ending session...")
            show_session_summary()
            break

    print(Fore.YELLOW + Style.BRIGHT + "\n  Farewell, adventurer. May your blade stay sharp.")
    print()


if __name__ == "__main__":
    main()
