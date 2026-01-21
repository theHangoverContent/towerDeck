"""
Tower Clash: Diamonds & Kings - Data Models
Defines all game entities: Card, Player, GameState, etc.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class Suit(Enum):
    """Card suits"""
    HEARTS = "♥"
    SPADES = "♠"
    CLUBS = "♣"
    DIAMONDS = "♦"


class Rank(Enum):
    """Card ranks"""
    ACE = "A"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"


@dataclass
class Card:
    """Represents a single card"""
    rank: Rank
    suit: Suit

    def __str__(self):
        return f"{self.rank.value}{self.suit.value}"

    def __repr__(self):
        return str(self)

    def is_diamond(self) -> bool:
        return self.suit == Suit.DIAMONDS

    def is_black(self) -> bool:
        return self.suit in [Suit.SPADES, Suit.CLUBS]

    def is_heart(self) -> bool:
        return self.suit == Suit.HEARTS

    def is_king(self) -> bool:
        return self.rank == Rank.KING


@dataclass
class PublicDiamond:
    """Represents a diamond on the public row with ownership"""
    card: Card
    owner_id: int

    def __str__(self):
        return f"{self.card} (P{self.owner_id})"


@dataclass
class Player:
    """Represents a game player"""
    id: int
    name: str
    hand: List[Card] = field(default_factory=list)
    steps: int = 0
    public_diamonds: List[PublicDiamond] = field(default_factory=list)

    def __str__(self):
        return f"P{self.id} {self.name} ({self.steps} steps, {len(self.hand)} cards)"

    def count_diamonds_in_hand(self) -> int:
        return sum(1 for c in self.hand if c.is_diamond())

    def count_total_diamonds(self) -> int:
        """Total diamonds: hand + public diamonds owned"""
        return self.count_diamonds_in_hand() + len(self.public_diamonds)

    def get_non_diamond_hand(self) -> List[Card]:
        """Returns all non-diamond cards in hand"""
        return [c for c in self.hand if not c.is_diamond()]

    def is_hand_empty_non_diamonds(self) -> bool:
        """Check if hand only contains diamonds or is empty"""
        return len(self.get_non_diamond_hand()) == 0


@dataclass
class GameState:
    """Main game state"""
    players: List[Player]
    draw_pile: List[Card] = field(default_factory=list)
    discard_pile: List[Card] = field(default_factory=list)
    public_diamonds: List[PublicDiamond] = field(default_factory=list)
    
    # Game configuration
    goal_steps: int = 20
    tower_floor: int = 0
    num_decks: int = 1
    
    # Game progress
    round_index: int = 1
    turn_index: int = 0
    turns_completed_total: int = 0
    winner: Optional[int] = None
    
    # Config from YAML
    config: Dict[str, Any] = field(default_factory=dict)

    def is_round1(self) -> bool:
        """Round 1 ends after each player has taken one turn"""
        return self.turns_completed_total < len(self.players)

    def current_player(self) -> Player:
        """Get the current active player"""
        return self.players[self.turn_index % len(self.players)]

    def next_player(self) -> Player:
        """Get the next player in order"""
        self.turn_index += 1
        return self.current_player()

    def draw_pile_empty(self) -> bool:
        return len(self.draw_pile) == 0

    def discard_pile_empty(self) -> bool:
        return len(self.discard_pile) == 0

    def get_public_diamonds_for_player(self, player_id: int) -> List[PublicDiamond]:
        """Get all public diamonds owned by a player"""
        return [d for d in self.public_diamonds if d.owner_id == player_id]

    def __str__(self):
        lines = [f"=== Game State (Round {self.round_index}) ==="]
        for p in self.players:
            lines.append(str(p))
        lines.append(f"Draw: {len(self.draw_pile)} | Discard: {len(self.discard_pile)} | Public ♦: {len(self.public_diamonds)}")
        return "\n".join(lines)


@dataclass
class ComboDefinition:
    """Represents a combo pattern from YAML"""
    id: str
    cards_pattern: List[Dict[str, Any]]
    steps_delta: int = 0
    draw: int = 0
    discard_from_hand: int = 0

    def __str__(self):
        return f"{self.id}: {self.steps_delta:+d} steps"
