"""
Tower Clash: Diamonds & Kings - Simple AI Player
Basic AI strategy for automated players.
"""

import random
from typing import List, Optional, Tuple
from src.models import Card, Player, GameState, Suit, Rank


class AIPlayer:
    """Simple AI player with basic strategy"""
    
    def __init__(self, player: Player):
        self.player = player
    
    def find_best_combo(self, hand: List[Card]) -> Optional[List[Card]]:
        """Find the best combo in hand (highest value)"""
        combos = self.find_all_combos(hand)
        if not combos:
            return None
        
        # Sort by value and return best
        combos.sort(key=lambda c: self.combo_value(c), reverse=True)
        return combos[0]
    
    def find_all_combos(self, hand: List[Card]) -> List[List[Card]]:
        """Find all possible combos in hand"""
        combos = []
        
        # Group by rank
        by_rank = {}
        for card in hand:
            if card.rank not in by_rank:
                by_rank[card.rank] = []
            by_rank[card.rank].append(card)
        
        # Check each rank group for combos
        for rank, cards in by_rank.items():
            if len(cards) < 2:
                continue
            
            # Four of a kind
            if len(cards) == 4:
                combos.append(cards[:])
            # Three of a kind with diamond
            elif len(cards) >= 3:
                diamond = next((c for c in cards if c.suit == Suit.DIAMONDS), None)
                if diamond:
                    # Three cards including diamond
                    three = [diamond] + [c for c in cards if c != diamond][:2]
                    combos.append(three)
            
            # Two-card combos
            if len(cards) >= 2:
                for i in range(len(cards)):
                    for j in range(i+1, len(cards)):
                        combo = [cards[i], cards[j]]
                        if self.is_valid_two_card_combo(combo):
                            combos.append(combo)
            
            # Three-card combos
            if len(cards) >= 3:
                for i in range(len(cards)):
                    for j in range(i+1, len(cards)):
                        for k in range(j+1, len(cards)):
                            combo = [cards[i], cards[j], cards[k]]
                            if self.is_valid_three_card_combo(combo):
                                combos.append(combo)
        
        return combos
    
    def is_valid_two_card_combo(self, cards: List[Card]) -> bool:
        """Check if two cards form a valid combo"""
        if len(cards) != 2:
            return False
        
        suits = [c.suit for c in cards]
        has_heart = Suit.HEARTS in suits
        has_diamond = Suit.DIAMONDS in suits
        has_black = any(s in [Suit.SPADES, Suit.CLUBS] for s in suits)
        
        # Two blacks
        if all(s in [Suit.SPADES, Suit.CLUBS] for s in suits):
            return True
        # Heart + black
        if has_heart and has_black:
            return True
        # Heart + diamond
        if has_heart and has_diamond:
            return True
        # Diamond + black
        if has_diamond and has_black:
            return True
        
        return False
    
    def is_valid_three_card_combo(self, cards: List[Card]) -> bool:
        """Check if three cards form a valid combo"""
        if len(cards) != 3:
            return False
        
        suits = [c.suit for c in cards]
        has_diamond = any(s == Suit.DIAMONDS for s in suits)
        has_heart = any(s == Suit.HEARTS for s in suits)
        has_black = any(s in [Suit.SPADES, Suit.CLUBS] for s in suits)
        
        # Heart + both blacks
        if has_heart and Suit.SPADES in suits and Suit.CLUBS in suits:
            return True
        
        # Three of a kind with diamond
        if has_diamond and len(set(suits)) == 3:
            return True
        
        return False
    
    def combo_value(self, cards: List[Card]) -> int:
        """Estimate the value of a combo"""
        if not cards:
            return 0
        
        # Basic scoring
        length = len(cards)
        has_king = any(c.rank == Rank.KING for c in cards)
        has_diamond = any(c.suit == Suit.DIAMONDS for c in cards)
        
        base_value = {
            2: 1,  # Two-card combos
            3: 2,  # Three-card combos
            4: 3,  # Four-of-a-kind
        }.get(length, 0)
        
        # Bonuses
        if has_king:
            base_value *= 2  # King rank doubling
        
        if has_diamond:
            base_value += 1  # Diamond bonus
        
        return base_value
    
    def decide_action(self, state: GameState) -> str:
        """Decide next action: "combo", "skip", "command", "swap", "jackpot", "end" """
        
        # Check for jackpot
        total_diamonds = sum(1 for c in self.player.hand if c.suit == Suit.DIAMONDS)
        total_diamonds += len([d for d in state.public_diamonds if d.owner_id == self.player.id])
        
        if total_diamonds >= 6:
            return "jackpot"
        
        # Try to find a good combo
        best_combo = self.find_best_combo(self.player.hand)
        if best_combo and self.combo_value(best_combo) >= 2:
            return "combo"
        
        # Try diamond command if opponent is ahead
        opponents = [p for p in state.players if p.id != self.player.id]
        if opponents and max(p.steps for p in opponents) > self.player.steps + 5:
            if self.player.count_diamonds_in_hand() > 0 or len(self.player.public_diamonds) > 0:
                return "command"
        
        # Try diamond swap if beneficial
        if len(self.player.public_diamonds) > 0 and len(state.public_diamonds) > 1:
            return "swap"
        
        # Default: end turn
        return "end"
    
    def get_diamond_command_target(self, state: GameState) -> Optional[int]:
        """Choose best target for diamond command"""
        opponents = [p for p in state.players if p.id != self.player.id]
        if not opponents:
            return None
        
        # Target highest-scoring opponent
        target = max(opponents, key=lambda p: p.steps)
        return target.id
    
    def get_swap_target(self, state: GameState) -> Optional[int]:
        """Choose best target for diamond swap"""
        # Prefer to swap with opponents who have valuable diamonds
        other_players = [p for p in state.players if p.id != self.player.id]
        if not other_players:
            return None
        
        # Simple: random opponent with public diamonds
        targets = [p for p in other_players if any(d.owner_id == p.id for d in state.public_diamonds)]
        if targets:
            return random.choice(targets).id
        
        return random.choice(other_players).id


class AIPlayers:
    """Helper class to manage multiple AI players"""
    
    def __init__(self, state: GameState, ai_player_ids: List[int]):
        self.state = state
        self.ai_players = {pid: AIPlayer(state.players[pid]) for pid in ai_player_ids}
    
    def is_ai(self, player_id: int) -> bool:
        """Check if player is AI"""
        return player_id in self.ai_players
    
    def get_ai(self, player_id: int) -> Optional[AIPlayer]:
        """Get AI instance for player"""
        return self.ai_players.get(player_id)
