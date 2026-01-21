"""
Tower Clash: Diamonds & Kings - Main Game Loop
Simple test/demo of the game engine.
"""

from src.game_loader import load_game
from src.engine import start_game, execute_turn, check_victory


def display_game_state(state):
    """Pretty print the game state"""
    print("\n" + "="*60)
    print(f"ROUND {state.round_index} | Turn {state.turns_completed_total + 1}")
    print("="*60)
    
    for player in state.players:
        diamonds_hand = sum(1 for c in player.hand if c.suit.value == "♦")
        diamonds_public = len([d for d in state.public_diamonds if d.owner_id == player.id])
        print(f"{player.name:12} | Steps: {player.steps:2} | Hand: {len(player.hand)} ({diamonds_hand}♦) | Public: {diamonds_public}♦")
    
    print(f"\nDraw Pile: {len(state.draw_pile)} cards")
    print(f"Discard Pile: {len(state.discard_pile)} cards")
    print(f"Public Diamonds: {len(state.public_diamonds)}")


def display_hand(player):
    """Display a player's hand"""
    print(f"\n{player.name}'s Hand ({len(player.hand)} cards):")
    for i, card in enumerate(player.hand):
        print(f"  {i+1}. {card}")


def main():
    """Main game loop"""
    print("\n" + "🎮 "*20)
    print("  TOWER CLASH: DIAMONDS & KINGS")
    print("🎮 "*20 + "\n")
    
    # Load game configuration
    try:
        state = load_game("game.yaml", ["Alice", "Bob"], num_decks=1)
    except FileNotFoundError:
        print("ERROR: game.yaml not found!")
        print("Make sure you're running this from the project root.")
        return
    
    # Start game
    state = start_game(state)
    print(f"✓ Game started with {len(state.players)} players")
    print(f"✓ Goal: {state.goal_steps} steps")
    print(f"✓ Deck: {len(state.draw_pile)} cards")
    
    # Display initial state
    display_game_state(state)
    
    # Simple game loop (demo: 3 rounds)
    max_turns = 3
    turn_count = 0
    
    while turn_count < max_turns and state.winner is None:
        player = state.current_player()
        
        print(f"\n--- {player.name}'s Turn ---")
        display_hand(player)
        
        # Execute turn
        execute_turn(state, player)
        
        display_game_state(state)
        
        # Check for winner
        winner = check_victory(state)
        if winner:
            print(f"\n🏆 {winner.name} WINS! 🏆")
            return
        
        turn_count += 1
    
    print(f"\n--- Game End (Demo: {max_turns} turns) ---")
    display_game_state(state)
    print("\nTop scores:")
    sorted_players = sorted(state.players, key=lambda p: p.steps, reverse=True)
    for i, player in enumerate(sorted_players, 1):
        print(f"  {i}. {player.name}: {player.steps} steps")


if __name__ == "__main__":
    main()
