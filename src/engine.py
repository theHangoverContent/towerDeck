"""
Tower Clash: Diamonds & Kings - Game Engine
Complete implementation of game logic and turn management.
"""

import random
from typing import List, Optional, Tuple
from src.models import Card, Player, GameState, PublicDiamond, Rank, Suit


# ============ INITIALIZATION ============

def start_game(state: GameState) -> GameState:
    """Initialize game: deal cards and set starting state"""
    state.round_index = 1
    state.turn_index = 0
    state.turns_completed_total = 0
    deal_each_player(state, 6)
    return state


def deal_each_player(state: GameState, num_cards: int) -> None:
    """Deal num_cards to each player"""
    for player in state.players:
        for _ in range(num_cards):
            draw_card(state, player)


# ============ DECK MANAGEMENT ============

def draw_card(state: GameState, player: Player) -> Optional[Card]:
    """Draw a card from draw pile, reshuffle if needed"""
    if state.draw_pile_empty():
        reshuffle_discard_into_draw(state)
    
    if state.draw_pile_empty():
        return None  # No cards available
    
    card = state.draw_pile.pop()
    player.hand.append(card)
    return card


def reshuffle_discard_into_draw(state: GameState) -> None:
    """Move discard pile back to draw pile and shuffle"""
    if state.discard_pile_empty():
        return
    
    state.draw_pile = state.discard_pile
    state.discard_pile = []
    random.shuffle(state.draw_pile)


def discard_card(state: GameState, player: Player, card: Card) -> None:
    """Remove card from player's hand and add to discard pile"""
    if card in player.hand:
        player.hand.remove(card)
    state.discard_pile.append(card)


# ============ DIAMOND MANAGEMENT ============

def end_of_turn_reveal_diamonds(state: GameState, player: Player) -> None:
    """Move all diamonds from hand to public row (face-up)"""
    diamonds = [c for c in player.hand if c.suit == Suit.DIAMONDS]
    for d in diamonds:
        player.hand.remove(d)
        public_d = PublicDiamond(card=d, owner_id=player.id)
        state.public_diamonds.append(public_d)


def count_player_diamonds_total(state: GameState, player: Player) -> int:
    """Count total diamonds: hand + public owned"""
    hand_diamonds = sum(1 for c in player.hand if c.suit == Suit.DIAMONDS)
    public_diamonds = len([d for d in state.public_diamonds if d.owner_id == player.id])
    return hand_diamonds + public_diamonds


def discard_six_player_diamonds(state: GameState, player: Player) -> None:
    """Discard up to 6 diamonds from player's diamonds"""
    # First, diamonds from hand
    diamonds_to_discard = []
    count = 0
    
    for c in player.hand[:]:
        if c.suit == Suit.DIAMONDS and count < 6:
            player.hand.remove(c)
            state.discard_pile.append(c)
            count += 1
    
    # Then, owned public diamonds
    owned = [d for d in state.public_diamonds if d.owner_id == player.id and count < 6]
    for d in owned[:6 - count]:
        state.public_diamonds.remove(d)
        state.discard_pile.append(d.card)
        count += 1


# ============ CARD OPERATIONS ============

def discard_from_hand(state: GameState, player: Player, card: Card) -> None:
    """Discard card from hand and apply king trigger"""
    if card in player.hand:
        player.hand.remove(card)
    state.discard_pile.append(card)
    king_discard_trigger(state, player, card)


def king_discard_trigger(state: GameState, discarder: Player, card: Card) -> None:
    """Apply effects when a King is discarded"""
    if card.rank != Rank.KING:
        return
    
    if card.suit in [Suit.SPADES, Suit.CLUBS]:
        # Black King: -2 steps
        discarder.steps = max(state.tower_floor, discarder.steps - 2)
    elif card.suit == Suit.HEARTS:
        # Heart King: +2 steps
        discarder.steps += 2
    elif card.suit == Suit.DIAMONDS:
        # Diamond King: draw 2
        draw_card(state, discarder)
        draw_card(state, discarder)


# ============ COMBO DETECTION & RESOLUTION ============

def is_four_kings(cards: List[Card]) -> bool:
    """Check if cards are the four kings"""
    if len(cards) != 4:
        return False
    suits = {c.suit for c in cards}
    return all(c.rank == Rank.KING for c in cards) and suits == {
        Suit.HEARTS, Suit.SPADES, Suit.CLUBS, Suit.DIAMONDS
    }


def all_same_rank(cards: List[Card]) -> bool:
    """Check if all cards have the same rank"""
    if not cards:
        return False
    rank = cards[0].rank
    return all(c.rank == rank for c in cards)


def identify_combo(cards: List[Card]) -> Optional[str]:
    """Identify which combo pattern these cards match"""
    if not all_same_rank(cards):
        return None
    
    if not cards:
        return None
    
    num_cards = len(cards)
    
    # Four of a kind
    if num_cards == 4:
        return "four_of_kind_any_rank"
    
    # Three of a kind (with or without diamond)
    if num_cards == 3:
        has_diamond = any(c.suit == Suit.DIAMONDS for c in cards)
        if has_diamond:
            return "three_kind_including_diamond"
        else:
            # Three of a kind without diamond is also valid (basic combo)
            return "three_of_kind_basic"
    
    # Two cards
    if num_cards == 2:
        suits = [c.suit for c in cards]
        has_heart = Suit.HEARTS in suits
        has_diamond = Suit.DIAMONDS in suits
        has_black = any(s in [Suit.SPADES, Suit.CLUBS] for s in suits)
        
        if has_heart and has_diamond:
            return "heart_plus_diamond"
        elif has_diamond and has_black:
            return "diamond_plus_black"
        elif has_heart and has_black:
            return "heart_plus_black"
        elif all(s in [Suit.SPADES, Suit.CLUBS] for s in suits):
            return "two_blacks"
    
    return None


def resolve_combo(state: GameState, active: Player, combo_cards: List[Card]) -> int:
    """
    Resolve a combo and apply effects.
    Returns the steps gained.
    """
    if not all_same_rank(combo_cards):
        return 0
    
    rank = combo_cards[0].rank
    
    # Four Kings special
    if rank == Rank.KING and is_four_kings(combo_cards):
        active.steps += 6
        draw_card(state, active)
        draw_card(state, active)
        for card in combo_cards:
            discard_card(state, active, card)
        return 6
    
    # Identify combo
    combo_id = identify_combo(combo_cards)
    if combo_id is None:
        return 0
    
    # Get effects from combo definition
    steps_gain = get_combo_steps(combo_id)
    draw_count = get_combo_draw(combo_id)
    discard_count = get_combo_discard(combo_id)
    
    # King rank doubling for step gains
    if rank == Rank.KING and steps_gain > 0:
        steps_gain *= 2
    
    active.steps += steps_gain
    
    # Apply discard effect
    if discard_count > 0 and len(active.hand) > 0:
        for _ in range(discard_count):
            if active.hand:
                # Simple strategy: discard first card (in real game, player chooses)
                card_to_discard = active.hand[0]
                discard_from_hand(state, active, card_to_discard)
    
    # Apply draw effect
    for _ in range(draw_count):
        draw_card(state, active)
    
    # Discard combo cards
    for card in combo_cards:
        discard_card(state, active, card)
    
    return steps_gain


# ============ COMBO EFFECTS (from YAML) ============

def get_combo_steps(combo_id: str) -> int:
    """Get step gains for a combo"""
    steps_map = {
        "two_blacks": 1,
        "heart_plus_black": 2,
        "heart_plus_both_blacks": 3,
        "heart_plus_diamond": 1,
        "diamond_plus_black": 0,
        "three_kind_including_diamond": 1,
        "three_of_kind_basic": 1,
        "four_of_kind_any_rank": 3,
    }
    return steps_map.get(combo_id, 0)


def get_combo_draw(combo_id: str) -> int:
    """Get draw count for a combo"""
    draw_map = {
        "heart_plus_diamond": 1,
        "diamond_plus_black": 1,
        "three_kind_including_diamond": 1,
        "four_of_kind_any_rank": 1,
    }
    return draw_map.get(combo_id, 0)


def get_combo_discard(combo_id: str) -> int:
    """Get discard from hand count for a combo"""
    discard_map = {
        "diamond_plus_black": 1,
        "three_kind_including_diamond": 1,
    }
    return discard_map.get(combo_id, 0)


# ============ DIAMOND ACTIONS ============

def diamond_command(state: GameState, active: Player, target: Player, 
                    diamond_to_pay_idx: Optional[int] = None,
                    card_to_discard_idx: Optional[int] = None) -> Optional[Card]:
    """
    Diamond Command: pay 1 diamond to force target to discard 1.
    Must have a diamond in hand or public.
    
    Args:
        state: Game state
        active: Player using the command
        target: Player being targeted
        diamond_to_pay_idx: Index of diamond to pay (None = auto-select)
        card_to_discard_idx: Index of card target should discard (None = auto-select)
    
    Returns:
        The card that was discarded, or None
    """
    # Check if active has a diamond to pay
    if not (active.count_diamonds_in_hand() > 0 or len(active.public_diamonds) > 0):
        return None  # No diamonds to pay
    
    # Pay 1 diamond (no effects on attacker)
    if active.count_diamonds_in_hand() > 0:
        if diamond_to_pay_idx is None:
            diamond = next(c for c in active.hand if c.suit == Suit.DIAMONDS)
        else:
            diamond = active.hand[diamond_to_pay_idx]
        # Use discard_card instead of discard_from_hand to avoid King trigger effects
        discard_card(state, active, diamond)
    else:
        if diamond_to_pay_idx is None:
            diamond_to_pay = active.public_diamonds[0]
        else:
            diamond_to_pay = active.public_diamonds[diamond_to_pay_idx]
        state.public_diamonds.remove(diamond_to_pay)
        state.discard_pile.append(diamond_to_pay.card)
    
    # Target discards 1
    if len(target.hand) == 0:
        return None
    
    if card_to_discard_idx is None:
        discarded = target.hand[0]  # Auto-select first
    else:
        discarded = target.hand[card_to_discard_idx]
    
    discard_from_hand(state, target, discarded)
    
    # Apply effects based on discarded card (only to target, not active)
    if discarded.suit in [Suit.SPADES, Suit.CLUBS]:
        # Black: target -1 step
        target.steps = max(state.tower_floor, target.steps - 1)
    elif discarded.suit == Suit.HEARTS:
        # Heart: target +1 step (the one who discarded)
        target.steps += 1
    elif discarded.suit == Suit.DIAMONDS:
        # Diamond: only target affected
        if state.is_round1():
            draw_card(state, target)
        else:
            apply_hoarding_penalty(state, target)
    
    return discarded


def apply_hoarding_penalty(state: GameState, player: Player) -> None:
    """
    After Round 1: player discarded a diamond from hand.
    Penalty: discard all hand, discard all owned public diamonds, -1 step, draw 6.
    """
    # Discard all hand
    while player.hand:
        discard_from_hand(state, player, player.hand[0])
    
    # Discard all owned public diamonds
    owned = [d for d in state.public_diamonds if d.owner_id == player.id]
    for d in owned:
        state.public_diamonds.remove(d)
        state.discard_pile.append(d.card)
    
    # -1 step
    player.steps = max(state.tower_floor, player.steps - 1)
    
    # Draw 6
    for _ in range(6):
        draw_card(state, player)


def diamond_swap(state: GameState, active: Player, target: Player) -> None:
    """Swap ownership of one of active's public diamonds with target's"""
    active_diamonds = [d for d in state.public_diamonds if d.owner_id == active.id]
    target_diamonds = [d for d in state.public_diamonds if d.owner_id == target.id]
    
    if active_diamonds and target_diamonds:
        # Simplified: swap first available
        d1 = active_diamonds[0]
        d2 = target_diamonds[0]
        d1.owner_id = target.id
        d2.owner_id = active.id


def jackpot_six_diamonds(state: GameState, player: Player) -> bool:
    """
    Check and apply 6-diamond jackpot.
    Returns True if jackpot was triggered.
    """
    if count_player_diamonds_total(state, player) < 6:
        return False
    
    player.steps += 6
    discard_six_player_diamonds(state, player)
    
    # Refill hand to 6 non-diamond cards
    non_diamond_count = len(player.get_non_diamond_hand())
    while non_diamond_count < 6:
        draw_card(state, player)
        non_diamond_count += 1
    
    return True


# ============ PENALTIES ============

def apply_empty_hand_penalty_if_needed(state: GameState, player: Player) -> None:
    """If hand is empty (no non-diamond cards), apply penalty"""
    if player.is_hand_empty_non_diamonds():
        player.steps = max(state.tower_floor, player.steps - 1)
        for _ in range(6):
            draw_card(state, player)


# ============ TURN MANAGEMENT ============

def execute_turn(state: GameState, player: Player) -> None:
    """Execute a full turn for a player"""
    # Draw phase
    draw_card(state, player)
    
    # Action phase (simplified: for now, just play best combo if available)
    # In a real game, this would be interactive
    
    # End of turn
    apply_empty_hand_penalty_if_needed(state, player)
    end_of_turn_reveal_diamonds(state, player)
    
    # Update turn tracking
    state.turns_completed_total += 1
    
    # Increment round when all players have completed a turn
    turns_in_current_round = state.turns_completed_total % len(state.players)
    if turns_in_current_round == 0:
        state.round_index += 1
    
    # Check victory
    if player.steps >= state.goal_steps:
        state.winner = player.id


def check_victory(state: GameState) -> Optional[Player]:
    """Check if any player has won"""
    for player in state.players:
        if player.steps >= state.goal_steps:
            return player
    return None
