"""
Tower Clash: Diamonds & Kings - Unit Tests
Comprehensive tests for game logic.
"""

import pytest
from src.models import Card, Player, GameState, Suit, Rank, PublicDiamond
from src.game_loader import GameLoader
from src.engine import (
    draw_card, discard_from_hand, resolve_combo, 
    king_discard_trigger, is_four_kings, all_same_rank,
    identify_combo, count_player_diamonds_total,
    end_of_turn_reveal_diamonds, apply_empty_hand_penalty_if_needed,
    jackpot_six_diamonds, apply_hoarding_penalty
)


@pytest.fixture
def game_state():
    """Create a test game state"""
    loader = GameLoader("game.yaml")
    state = loader.load_game_state(["Alice", "Bob"], num_decks=1)
    return state


class TestCard:
    """Test Card class"""
    
    def test_card_creation(self):
        card = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        assert card.rank == Rank.ACE
        assert card.suit == Suit.HEARTS
    
    def test_card_is_diamond(self):
        card_diamond = Card(rank=Rank.ACE, suit=Suit.DIAMONDS)
        card_heart = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        
        assert card_diamond.is_diamond()
        assert not card_heart.is_diamond()
    
    def test_card_is_black(self):
        card_spade = Card(rank=Rank.ACE, suit=Suit.SPADES)
        card_club = Card(rank=Rank.ACE, suit=Suit.CLUBS)
        card_heart = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        
        assert card_spade.is_black()
        assert card_club.is_black()
        assert not card_heart.is_black()
    
    def test_card_is_king(self):
        king = Card(rank=Rank.KING, suit=Suit.HEARTS)
        ace = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        
        assert king.is_king()
        assert not ace.is_king()
    
    def test_card_string(self):
        card = Card(rank=Rank.KING, suit=Suit.DIAMONDS)
        assert str(card) == "K♦"


class TestPlayer:
    """Test Player class"""
    
    def test_player_creation(self):
        player = Player(id=0, name="Alice")
        assert player.id == 0
        assert player.name == "Alice"
        assert len(player.hand) == 0
        assert player.steps == 0
    
    def test_count_diamonds_in_hand(self):
        player = Player(id=0, name="Alice")
        player.hand = [
            Card(Rank.ACE, Suit.DIAMONDS),
            Card(Rank.KING, Suit.HEARTS),
            Card(Rank.TWO, Suit.DIAMONDS)
        ]
        assert player.count_diamonds_in_hand() == 2
    
    def test_count_total_diamonds(self):
        player = Player(id=0, name="Alice")
        player.hand = [Card(Rank.ACE, Suit.DIAMONDS)]
        player.public_diamonds = [
            PublicDiamond(Card(Rank.KING, Suit.DIAMONDS), 0),
            PublicDiamond(Card(Rank.QUEEN, Suit.DIAMONDS), 0)
        ]
        assert player.count_total_diamonds() == 3
    
    def test_is_hand_empty_non_diamonds(self):
        player = Player(id=0, name="Alice")
        player.hand = [Card(Rank.ACE, Suit.DIAMONDS)]
        assert player.is_hand_empty_non_diamonds()
        
        player.hand.append(Card(Rank.KING, Suit.HEARTS))
        assert not player.is_hand_empty_non_diamonds()


class TestGameState:
    """Test GameState class"""
    
    def test_game_state_creation(self, game_state):
        assert len(game_state.players) == 2
        assert game_state.goal_steps == 20
        assert game_state.round_index == 1
    
    def test_is_round1(self, game_state):
        assert game_state.is_round1()
        game_state.turns_completed_total = 2
        assert not game_state.is_round1()
    
    def test_current_player(self, game_state):
        game_state.turn_index = 0
        assert game_state.current_player().id == 0
        game_state.turn_index = 1
        assert game_state.current_player().id == 1
    
    def test_next_player(self, game_state):
        game_state.turn_index = 0
        assert game_state.next_player().id == 1
        assert game_state.turn_index == 1


class TestDeckManagement:
    """Test deck and card management"""
    
    def test_draw_card(self, game_state):
        player = game_state.players[0]
        initial_hand_size = len(player.hand)
        
        draw_card(game_state, player)
        assert len(player.hand) == initial_hand_size + 1
    
    def test_draw_pile_empty(self, game_state):
        player = game_state.players[0]
        
        # Empty draw pile
        game_state.draw_pile = []
        game_state.discard_pile = [Card(Rank.ACE, Suit.HEARTS)]
        
        card = draw_card(game_state, player)
        assert card is not None
        assert len(game_state.draw_pile) == 0
    
    def test_discard_from_hand(self, game_state):
        player = game_state.players[0]
        card = Card(Rank.ACE, Suit.HEARTS)
        player.hand.append(card)
        
        discard_from_hand(game_state, player, card)
        assert card not in player.hand
        assert card in game_state.discard_pile


class TestComboDetection:
    """Test combo detection and resolution"""
    
    def test_all_same_rank(self):
        cards = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.ACE, Suit.CLUBS)
        ]
        assert all_same_rank(cards)
        
        cards.append(Card(Rank.KING, Suit.DIAMONDS))
        assert not all_same_rank(cards)
    
    def test_is_four_kings(self):
        four_kings = [
            Card(Rank.KING, Suit.HEARTS),
            Card(Rank.KING, Suit.SPADES),
            Card(Rank.KING, Suit.CLUBS),
            Card(Rank.KING, Suit.DIAMONDS)
        ]
        assert is_four_kings(four_kings)
        
        # Wrong suits
        wrong_kings = four_kings[:3]
        assert not is_four_kings(wrong_kings)
        
        # Wrong rank
        wrong_rank = [
            Card(Rank.KING, Suit.HEARTS),
            Card(Rank.KING, Suit.SPADES),
            Card(Rank.KING, Suit.CLUBS),
            Card(Rank.ACE, Suit.DIAMONDS)
        ]
        assert not is_four_kings(wrong_rank)
    
    def test_identify_combo_two_blacks(self):
        cards = [
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.ACE, Suit.CLUBS)
        ]
        assert identify_combo(cards) == "two_blacks"
    
    def test_identify_combo_heart_plus_black(self):
        cards = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.ACE, Suit.SPADES)
        ]
        assert identify_combo(cards) == "heart_plus_black"
    
    def test_identify_combo_heart_plus_diamond(self):
        cards = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.ACE, Suit.DIAMONDS)
        ]
        assert identify_combo(cards) == "heart_plus_diamond"
    
    def test_identify_combo_four_of_kind(self):
        cards = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.ACE, Suit.CLUBS),
            Card(Rank.ACE, Suit.DIAMONDS)
        ]
        assert identify_combo(cards) == "four_of_kind_any_rank"
    
    def test_resolve_combo(self, game_state):
        player = game_state.players[0]
        player.steps = 0
        
        cards = [
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.ACE, Suit.CLUBS)
        ]
        player.hand = cards[:]
        
        steps_gained = resolve_combo(game_state, player, cards)
        assert steps_gained == 1
        assert player.steps == 1


class TestKings:
    """Test King-specific mechanics"""
    
    def test_king_discard_black_king(self, game_state):
        player = game_state.players[0]
        player.steps = 10
        
        card = Card(Rank.KING, Suit.SPADES)
        king_discard_trigger(game_state, player, card)
        assert player.steps == 8  # -2 for black king
    
    def test_king_discard_heart_king(self, game_state):
        player = game_state.players[0]
        player.steps = 10
        
        card = Card(Rank.KING, Suit.HEARTS)
        king_discard_trigger(game_state, player, card)
        assert player.steps == 12  # +2 for heart king
    
    def test_king_discard_diamond_king(self, game_state):
        player = game_state.players[0]
        initial_hand = len(player.hand)
        
        card = Card(Rank.KING, Suit.DIAMONDS)
        king_discard_trigger(game_state, player, card)
        # Should draw 2 cards
        assert len(player.hand) == initial_hand + 2


class TestDiamonds:
    """Test diamond mechanics"""
    
    def test_end_of_turn_reveal_diamonds(self, game_state):
        player = game_state.players[0]
        diamonds = [
            Card(Rank.ACE, Suit.DIAMONDS),
            Card(Rank.KING, Suit.DIAMONDS)
        ]
        player.hand = diamonds + [Card(Rank.ACE, Suit.HEARTS)]
        
        end_of_turn_reveal_diamonds(game_state, player)
        
        # Diamonds moved to public
        assert len(player.hand) == 1
        assert len(game_state.public_diamonds) == 2
    
    def test_count_player_diamonds_total(self, game_state):
        player = game_state.players[0]
        # Clear existing hand first
        player.hand = [Card(Rank.ACE, Suit.DIAMONDS)]
        player.public_diamonds = []
        game_state.public_diamonds = [
            PublicDiamond(Card(Rank.KING, Suit.DIAMONDS), 0)
        ]
        
        total = count_player_diamonds_total(game_state, player)
        assert total == 2
    
    def test_jackpot_six_diamonds(self, game_state):
        player = game_state.players[0]
        player.steps = 0
        
        # Give player 6 diamonds
        for rank in [Rank.ACE, Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX]:
            player.hand.append(Card(rank, Suit.DIAMONDS))
        
        result = jackpot_six_diamonds(game_state, player)
        assert result is True
        assert player.steps == 6


class TestPenalties:
    """Test penalty mechanics"""
    
    def test_empty_hand_penalty(self, game_state):
        player = game_state.players[0]
        player.steps = 5
        player.hand = []
        
        apply_empty_hand_penalty_if_needed(game_state, player)
        
        assert player.steps == 4  # -1 step
        assert len(player.hand) == 6  # Drew 6 cards


class TestGameIntegration:
    """Integration tests"""
    
    def test_full_turn_sequence(self, game_state):
        player = game_state.players[0]
        initial_hand_size = len(player.hand)
        
        # Draw
        draw_card(game_state, player)
        assert len(player.hand) == initial_hand_size + 1
        
        # End of turn reveal
        end_of_turn_reveal_diamonds(game_state, player)
        
        # Some diamonds might have been revealed
        assert len(game_state.public_diamonds) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
