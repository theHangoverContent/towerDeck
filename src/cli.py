"""
Tower Clash: Diamonds & Kings - Interactive CLI
Full interactive game with player choices and AI players.
"""

from typing import List, Optional, Tuple
from src.models import Card, Player, GameState, Suit, Rank
from src.game_loader import load_game
from src.engine import (
    start_game, draw_card, discard_from_hand, resolve_combo,
    diamond_command, diamond_swap, jackpot_six_diamonds,
    apply_empty_hand_penalty_if_needed, end_of_turn_reveal_diamonds,
    check_victory
)


class InteractiveCLI:
    """Interactive command-line interface for the game"""
    
    def __init__(self, state: GameState):
        self.state = state
        self.ai_players = set()  # IDs of AI players
    
    def display_header(self, text: str):
        """Display a formatted header"""
        print("\n" + "="*70)
        print(f"  {text}")
        print("="*70)
    
    def display_game_state(self):
        """Display current game state"""
        print(f"\n{'─'*70}")
        print(f"ROUND {self.state.round_index} | Total Turns: {self.state.turns_completed_total}")
        print(f"{'─'*70}")
        
        for player in self.state.players:
            diamonds_hand = sum(1 for c in player.hand if c.suit == Suit.DIAMONDS)
            diamonds_public = len([d for d in self.state.public_diamonds if d.owner_id == player.id])
            
            ai_tag = " (AI)" if player.id in self.ai_players else ""
            marker = "➤" if player.id == self.state.current_player().id else " "
            print(f"{marker} P{player.id} {player.name:12} | Steps: {player.steps:2}/20 | "
                  f"Hand: {len(player.hand)} ({diamonds_hand}♦) | Public: {diamonds_public}♦{ai_tag}")
        
        print(f"\nDraw: {len(self.state.draw_pile)} | Discard: {len(self.state.discard_pile)} | "
              f"Public♦: {len(self.state.public_diamonds)}")
    
    def display_player_hand(self, player: Player):
        """Display a player's hand with indices"""
        print(f"\n{player.name}'s Hand ({len(player.hand)} cards):")
        for i, card in enumerate(player.hand, 1):
            suit_emoji = card.suit.value
            print(f"  {i:2}. {card.rank.value}{suit_emoji}", end="")
            if i % 3 == 0:
                print()
            else:
                print("  ", end="")
        print()
    
    def display_public_diamonds(self):
        """Display public diamonds row"""
        if not self.state.public_diamonds:
            print("Public Diamonds Row: (empty)")
            return
        
        print("\nPublic Diamonds Row:")
        for i, diamond in enumerate(self.state.public_diamonds, 1):
            owner_name = self.state.players[diamond.owner_id].name
            print(f"  {i}. {diamond.card} (owned by {owner_name})")
    
    def get_player_choice(self, player: Player) -> str:
        """Get action choice from player"""
        print(f"\n{player.name}'s action:")
        print("  1. Play cards / Cash-in combos")
        print("  2. Diamond Swap (once/turn)")
        print("  3. Diamond Command")
        print("  4. Skip-turn cycle (discard & draw)")
        print("  5. Check jackpot & end turn")
        print("  6. View public diamonds")
        print("  0. End turn")
        
        while True:
            choice = input("\nChoose action (0-6): ").strip()
            if choice in "0123456":
                return choice
            print("Invalid choice. Try again.")
    
    def play_combo(self, player: Player) -> bool:
        """Allow player to play a combo"""
        self.display_player_hand(player)
        
        print("\nEnter card numbers for combo (space-separated, e.g., '1 3 5'):")
        print("Or 'skip' to skip this action:")
        
        choice = input("> ").strip().lower()
        if choice == "skip":
            return False
        
        try:
            indices = [int(x) - 1 for x in choice.split()]
            cards = [player.hand[i] for i in indices]
            
            combo_id = resolve_combo(self.state, player, cards)
            if combo_id > 0:
                print(f"✓ Combo resolved! Gained {combo_id} steps")
                return True
            else:
                print("✗ Invalid combo")
                return False
        except (ValueError, IndexError):
            print("✗ Invalid input")
            return False
    
    def play_skip_turn(self, player: Player) -> bool:
        """Execute skip-turn cycle"""
        if len(player.hand) == 0:
            print("Cannot skip: hand is empty")
            return False
        
        self.display_player_hand(player)
        print("\nSelect card to discard:")
        
        choice = input("> ").strip()
        try:
            idx = int(choice) - 1
            card = player.hand[idx]
            discard_from_hand(self.state, player, card)
            print(f"✓ Discarded {card}")
            
            new_card = draw_card(self.state, player)
            print(f"✓ Drew {new_card}")
            
            # If diamond was discarded, may repeat
            if card.suit == Suit.DIAMONDS:
                repeat = input("Diamond discarded! Repeat? (y/n): ").strip().lower()
                if repeat == 'y':
                    return self.play_skip_turn(player)
            
            return True
        except (ValueError, IndexError):
            print("✗ Invalid input")
            return False
    
    def play_diamond_command(self, player: Player) -> bool:
        """Execute diamond command action"""
        # Check if player has diamond
        if player.count_diamonds_in_hand() == 0 and len(player.public_diamonds) == 0:
            print("You have no diamonds to pay with!")
            return False
        
        # Select target
        print("\nSelect target player:")
        other_players = [p for p in self.state.players if p.id != player.id]
        for i, p in enumerate(other_players):
            print(f"  {i}. {p.name}")
        
        try:
            target_idx = int(input("> ").strip())
            if target_idx < 0 or target_idx >= len(other_players):
                raise IndexError()
            target = other_players[target_idx]
        except (ValueError, IndexError):
            print("✗ Invalid target")
            return False
        
        diamond_command(self.state, player, target)
        print(f"✓ Used Diamond Command on {target.name}")
        return True
    
    def play_turn(self, player: Player) -> None:
        """Execute a full interactive turn"""
        self.display_game_state()
        
        if player.id in self.ai_players:
            print(f"\n{player.name} (AI) is playing...")
            self.play_ai_turn(player)
        else:
            print(f"\n{player.name}'s Turn!")
            self.play_interactive_turn(player)
        
        # End of turn
        apply_empty_hand_penalty_if_needed(self.state, player)
        end_of_turn_reveal_diamonds(self.state, player)
        
        self.state.turns_completed_total += 1
        if self.state.turns_completed_total == len(self.state.players):
            self.state.round_index = 2
    
    def play_interactive_turn(self, player: Player):
        """Interactive turn loop"""
        # Draw phase
        card = draw_card(self.state, player)
        print(f"Drew: {card}")
        
        # Action phase
        while True:
            choice = self.get_player_choice(player)
            
            if choice == "0":
                break
            elif choice == "1":
                self.play_combo(player)
            elif choice == "2":
                self.play_diamond_swap(player)
            elif choice == "3":
                self.play_diamond_command(player)
            elif choice == "4":
                if self.play_skip_turn(player):
                    break
            elif choice == "5":
                if jackpot_six_diamonds(self.state, player):
                    print(f"✓ Jackpot! Gained 6 steps!")
                break
            elif choice == "6":
                self.display_public_diamonds()
    
    def play_diamond_swap(self, player: Player) -> bool:
        """Execute diamond swap"""
        player_diamonds = [d for d in self.state.public_diamonds if d.owner_id == player.id]
        if not player_diamonds:
            print("You have no public diamonds!")
            return False
        
        # Select target
        print("\nSelect target player to swap with:")
        other_players = [p for p in self.state.players if p.id != player.id]
        for i, p in enumerate(other_players):
            print(f"  {i}. {p.name}")
        
        try:
            target_idx = int(input("> ").strip())
            if target_idx < 0 or target_idx >= len(other_players):
                raise IndexError()
            target = other_players[target_idx]
        except (ValueError, IndexError):
            print("✗ Invalid target")
            return False
        
        diamond_swap(self.state, player, target)
        print(f"✓ Swapped diamond ownership with {target.name}")
        return True
    
    def play_ai_turn(self, player: Player):
        """Simple AI turn logic"""
        from src.ai import AIPlayer
        ai = AIPlayer(player)
        
        # Draw
        card = draw_card(self.state, player)
        print(f"  Drew: {card}")
        
        # Try to play best combo
        best_combo = ai.find_best_combo(player.hand)
        if best_combo:
            combo_id = resolve_combo(self.state, player, best_combo)
            print(f"  Played combo, gained {combo_id} steps")
        else:
            print(f"  No combos available")
    
    def run_game(self):
        """Main game loop"""
        self.display_header("🎮 TOWER CLASH: DIAMONDS & KINGS 🎮")
        
        state = start_game(self.state)
        print(f"\n✓ Game started!")
        print(f"✓ Players: {', '.join(p.name for p in self.state.players)}")
        print(f"✓ Goal: {self.state.goal_steps} steps")
        print(f"✓ Cards: {len(self.state.draw_pile)}")
        
        input("\nPress ENTER to begin...")
        
        # Main game loop
        while self.state.winner is None:
            player = self.state.current_player()
            self.play_turn(player)
            
            # Check victory
            winner = check_victory(self.state)
            if winner:
                self.display_header(f"🏆 {winner.name} WINS! 🏆")
                self.display_game_state()
                return
            
            self.state.next_player()
    
    def setup_players(self):
        """Setup players (human or AI)"""
        print("\n" + "="*70)
        print("  PLAYER SETUP")
        print("="*70)
        
        for player in self.state.players:
            print(f"\nPlayer {player.id}: {player.name}")
            choice = input("  (H)uman or (A)I? [H]: ").strip().lower()
            if choice == 'a':
                self.ai_players.add(player.id)
                print(f"  ✓ Set to AI")
            else:
                print(f"  ✓ Set to Human")


def main():
    """Main entry point"""
    try:
        # Load game config
        state = load_game("game.yaml", ["Alice", "Bob"], num_decks=1)
        
        # Create CLI and setup players
        cli = InteractiveCLI(state)
        cli.setup_players()
        
        # Run game
        cli.run_game()
        
    except FileNotFoundError:
        print("ERROR: game.yaml not found!")
        print("Run from project root: python -m src.cli")


if __name__ == "__main__":
    main()
