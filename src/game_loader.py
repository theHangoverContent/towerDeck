"""
Tower Clash: Diamonds & Kings - Game Loader
Loads game configuration from YAML and initializes the deck.
"""

import yaml
from typing import Dict, Any, List
from src.models import Card, Suit, Rank, Player, GameState, ComboDefinition


class GameLoader:
    """Loads game config from YAML and creates game state"""

    def __init__(self, yaml_path: str):
        with open(yaml_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        self.game_config = self.config['game']

    def load_game_state(self, player_names: List[str], num_decks: int = 1) -> GameState:
        """Initialize a game state from config and player names"""
        
        # Validate player count
        min_players = self.game_config['players']['min']
        max_players = self.game_config['players']['max']
        num_players = len(player_names)
        
        if not (min_players <= num_players <= max_players):
            raise ValueError(f"Expected {min_players}-{max_players} players, got {num_players}")

        # Create players
        players = [Player(id=i, name=name) for i, name in enumerate(player_names)]

        # Create game state
        state = GameState(
            players=players,
            goal_steps=self.game_config['victory']['tower_goal_steps'],
            tower_floor=self.game_config['victory']['tower_floor_steps'],
            num_decks=num_decks,
            config=self.game_config
        )

        # Create and shuffle deck
        state.draw_pile = self._create_deck(num_decks)
        import random
        random.shuffle(state.draw_pile)

        return state

    def _create_deck(self, num_decks: int) -> List[Card]:
        """Create a standard 52-card deck (repeated num_decks times)"""
        deck = []
        
        # Get ranks and suits from config
        ranks_str = self.game_config['ranks']
        suits_config = self.game_config['suits']
        
        # Map string representations to Rank enums
        rank_value_map = {
            'A': Rank.ACE, '2': Rank.TWO, '3': Rank.THREE, '4': Rank.FOUR,
            '5': Rank.FIVE, '6': Rank.SIX, '7': Rank.SEVEN, '8': Rank.EIGHT,
            '9': Rank.NINE, '10': Rank.TEN, 'J': Rank.JACK, 'Q': Rank.QUEEN,
            'K': Rank.KING
        }
        
        suit_map = {
            'hearts': Suit.HEARTS,
            'spades': Suit.SPADES,
            'clubs': Suit.CLUBS,
            'diamonds': Suit.DIAMONDS
        }
        
        for _ in range(num_decks):
            for rank_str in ranks_str:
                for suit_name in suits_config.keys():
                    rank = rank_value_map[rank_str]
                    suit = suit_map[suit_name]
                    deck.append(Card(rank=rank, suit=suit))
        
        return deck

    def get_combo_definitions(self) -> Dict[str, ComboDefinition]:
        """Parse combo definitions from YAML"""
        combos = {}
        
        combo_section = self.game_config.get('combos', {})
        
        # Standard combos
        for combo_data in combo_section.get('standard', []):
            combo_id = combo_data['id']
            combos[combo_id] = ComboDefinition(
                id=combo_id,
                cards_pattern=combo_data.get('cards', []),
                steps_delta=combo_data.get('steps_delta', 0),
                draw=combo_data.get('draw', 0),
                discard_from_hand=combo_data.get('discard_from_hand', 0)
            )
        
        # Diamond interaction combos
        for combo_data in combo_section.get('diamond_interactions', []):
            combo_id = combo_data['id']
            combos[combo_id] = ComboDefinition(
                id=combo_id,
                cards_pattern=combo_data.get('cards', []),
                steps_delta=combo_data.get('steps_delta', 0),
                draw=combo_data.get('draw', 0),
                discard_from_hand=combo_data.get('discard_from_hand', 0)
            )
        
        return combos


def load_game(yaml_path: str, player_names: List[str], num_decks: int = 1) -> GameState:
    """Convenience function to load a game"""
    loader = GameLoader(yaml_path)
    return loader.load_game_state(player_names, num_decks)
