"""
Tower Clash: Diamonds & Kings - GUI (Tkinter)
Graphical user interface for the game.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, List
from src.models import Card, Player, GameState, Suit, Rank, PublicDiamond
from src.game_loader import load_game
from src.engine import (
    start_game, draw_card, discard_from_hand, resolve_combo,
    diamond_command, diamond_swap, jackpot_six_diamonds,
    apply_empty_hand_penalty_if_needed, end_of_turn_reveal_diamonds,
    check_victory
)


class TowerClashGUI:
    """Graphical interface for Tower Clash game"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Tower Clash: Diamonds & Kings")
        self.root.geometry("1400x880")
        
        self.state: Optional[GameState] = None
        self.selected_cards: List[int] = []
        self.card_buttons = {}
        self.turn_started = False
        self.revealing_diamonds = False
        self.selected_diamonds_to_reveal: List[int] = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the main UI"""
        # Title
        title = ttk.Label(self.root, text="🎮 Tower Clash: Diamonds & Kings 🎮", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=5)
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left: Game info
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(left_frame, text="Game Status", font=("Arial", 12, "bold")).pack()
        self.status_text = tk.Text(left_frame, height=10, width=40)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Center: Card display
        center_frame = ttk.Frame(main_frame)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(center_frame, text="Your Hand", font=("Arial", 12, "bold")).pack()
        self.hand_frame = ttk.Frame(center_frame)
        self.hand_frame.pack(fill=tk.BOTH, expand=True)
        
        # Right: Actions
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(right_frame, text="Actions", font=("Arial", 12, "bold")).pack()
        self.action_frame = ttk.Frame(right_frame)
        self.action_frame.pack(fill=tk.BOTH, expand=True)
        
        # Bottom: Control buttons
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        ttk.Button(bottom_frame, text="New Game", command=self.new_game).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Quit", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        self.new_game()
    
    def new_game(self):
        """Start a new game"""
        try:
            self.state = load_game("game.yaml", ["Alice", "Bob"], num_decks=1)
            self.state = start_game(self.state)
            self.turn_started = False
            self.revealing_diamonds = False
            self.selected_cards = []
            self.selected_diamonds_to_reveal = []
            self.update_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start game: {e}")
    
    def update_display(self):
        """Update the entire display"""
        if not self.state:
            return
        
        # Force immediate refresh before updating
        self.root.update_idletasks()
        
        # Update status
        self.update_status()
        
        # Update hand
        self.update_hand()
        
        # Update actions
        self.update_actions()
        
        # Force another refresh after updating
        self.root.update_idletasks()
    
    def update_status(self):
        """Update game status display"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete("1.0", tk.END)
        
        # Get fresh player reference to ensure up-to-date data
        player = self.state.current_player()
        
        text = f"""
=== Game Status ===
Round: {self.state.round_index}
Turn: {self.state.turns_completed_total}

Current Player: {player.name}
Steps: {player.steps}/20 ⭐

Players Status:
"""
        for i, p in enumerate(self.state.players):
            diamonds = sum(1 for c in p.hand if c.suit == Suit.DIAMONDS)
            public_diamonds = sum(1 for d in self.state.public_diamonds if d.owner_id == p.id)
            text += f"  [{i}] {p.name}: {p.steps} steps ({len(p.hand)} cards, {diamonds}♦ hand, {public_diamonds}♦ public)\n"
        
        text += f"""
Deck: {len(self.state.draw_pile)} cards
Discard: {len(self.state.discard_pile)} cards
Public ♦: {len(self.state.public_diamonds)}

Turn Status: {'READY TO DRAW' if not self.turn_started else 'IN PROGRESS'}
Reveal Diamonds: {'YES' if self.revealing_diamonds else 'NO'}
"""
        
        self.status_text.insert("1.0", text)
        self.status_text.config(state=tk.DISABLED)
    
    def update_hand(self):
        """Update hand display including public row"""
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        
        self.card_buttons = {}
        player = self.state.current_player()
        
        # Create a frame for scrolling with wrapping
        canvas = tk.Canvas(self.hand_frame, bg="white")
        scrollbar = ttk.Scrollbar(self.hand_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title for hand
        title_hand = ttk.Label(scrollable_frame, text="=== YOUR HAND ===", font=("Arial", 10, "bold"))
        title_hand.pack(fill=tk.X, padx=5, pady=5)
        
        # Hand cards
        if player.hand:
            cards_per_row = 6
            for row_idx in range(0, len(player.hand), cards_per_row):
                row_frame = ttk.Frame(scrollable_frame)
                row_frame.pack(fill=tk.X, padx=5, pady=3)
                
                for col_idx in range(cards_per_row):
                    card_idx = row_idx + col_idx
                    if card_idx < len(player.hand):
                        card = player.hand[card_idx]
                        if self.revealing_diamonds and card.suit == Suit.DIAMONDS:
                            self.add_diamond_button(row_frame, card_idx, card, is_public=False)
                        else:
                            self.add_card_button(row_frame, card_idx, card)
        else:
            ttk.Label(scrollable_frame, text="(No cards in hand)", font=("Arial", 9)).pack(padx=5, pady=3)
        
        # Public Row
        public_diamonds = [d for d in self.state.public_diamonds if d.owner_id == player.id]
        
        if public_diamonds:
            ttk.Separator(scrollable_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=5)
            
            title_public = ttk.Label(scrollable_frame, text="=== YOUR PUBLIC ROW ===", font=("Arial", 10, "bold"))
            title_public.pack(fill=tk.X, padx=5, pady=5)
            
            cards_per_row = 6
            public_cards = [d.card for d in public_diamonds]
            
            for row_idx in range(0, len(public_cards), cards_per_row):
                row_frame = ttk.Frame(scrollable_frame)
                row_frame.pack(fill=tk.X, padx=5, pady=3)
                
                for col_idx in range(cards_per_row):
                    card_idx = row_idx + col_idx
                    if card_idx < len(public_cards):
                        card = public_cards[card_idx]
                        public_d_idx = card_idx
                        if self.revealing_diamonds and card.suit == Suit.DIAMONDS:
                            self.add_diamond_button(row_frame, 10000 + public_d_idx, card, is_public=True)
                        else:
                            self.add_public_card_button(row_frame, 10000 + public_d_idx, card)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def add_card_button(self, parent, index: int, card: Card):
        """Add a card button to display"""
        suit_color = {
            Suit.HEARTS: "red",
            Suit.DIAMONDS: "blue",
            Suit.SPADES: "black",
            Suit.CLUBS: "green"
        }
        
        text = f"{card.rank.value}{card.suit.value}"
        btn = tk.Button(
            parent,
            text=text,
            width=6,
            height=4,
            bg=suit_color[card.suit],
            fg="white",
            font=("Arial", 10, "bold"),
            command=lambda: self.toggle_card(index)
        )
        btn.pack(side=tk.LEFT, padx=2)
        self.card_buttons[index] = btn
    
    def add_diamond_button(self, parent, index: int, card: Card, is_public: bool = False):
        """Add a diamond button for reveal phase (special highlight)"""
        text = f"{card.rank.value}♦"
        btn = tk.Button(
            parent,
            text=text,
            width=6,
            height=4,
            bg="gold",
            fg="darkblue",
            font=("Arial", 10, "bold"),
            command=lambda: self.toggle_diamond_reveal(index, is_public)
        )
        btn.pack(side=tk.LEFT, padx=2)
        self.card_buttons[index] = btn
    
    def add_public_card_button(self, parent, index: int, card: Card):
        """Add a public row card button (for combos)"""
        suit_color = {
            Suit.HEARTS: "red",
            Suit.DIAMONDS: "blue",
            Suit.SPADES: "black",
            Suit.CLUBS: "green"
        }
        
        text = f"{card.rank.value}{card.suit.value}"
        btn = tk.Button(
            parent,
            text=text,
            width=6,
            height=4,
            bg=suit_color[card.suit],
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.RIDGE,
            bd=3,
            command=lambda: self.toggle_card(index)
        )
        btn.pack(side=tk.LEFT, padx=2)
        self.card_buttons[index] = btn
    
    def toggle_card(self, index: int):
        """Toggle card selection"""
        if index in self.selected_cards:
            self.selected_cards.remove(index)
        else:
            self.selected_cards.append(index)
        
        # Highlight selected
        for i, btn in self.card_buttons.items():
            if i in self.selected_cards:
                btn.config(relief=tk.SUNKEN, bd=5)
            else:
                btn.config(relief=tk.RAISED, bd=1)
    
    def toggle_diamond_reveal(self, index: int, is_public: bool = False):
        """Toggle diamond selection for reveal"""
        if index in self.selected_diamonds_to_reveal:
            self.selected_diamonds_to_reveal.remove(index)
        else:
            self.selected_diamonds_to_reveal.append(index)
        
        # Highlight selected
        for i, btn in self.card_buttons.items():
            if i in self.selected_diamonds_to_reveal:
                btn.config(relief=tk.SUNKEN, bd=5)
            else:
                btn.config(relief=tk.RAISED, bd=1)
    
    def update_actions(self):
        """Update action buttons"""
        for widget in self.action_frame.winfo_children():
            widget.destroy()
        
        player = self.state.current_player()
        
        # Phase 1: Draw card at start of turn
        if not self.turn_started:
            ttk.Label(self.action_frame, text="DRAW PHASE", font=("Arial", 10, "bold"), foreground="blue").pack()
            ttk.Button(self.action_frame, text="Draw Card", 
                      command=self.start_turn).pack(fill=tk.X, pady=5)
            return
        
        # Phase 3: Reveal diamonds phase
        if self.revealing_diamonds:
            ttk.Label(self.action_frame, text="REVEAL DIAMONDS", font=("Arial", 10, "bold"), foreground="purple").pack()
            ttk.Label(self.action_frame, text="(Optional: select diamonds to reveal)", font=("Arial", 8)).pack()
            
            player_diamonds = [i for i, c in enumerate(player.hand) if c.suit == Suit.DIAMONDS]
            if player_diamonds:
                ttk.Button(self.action_frame, text="Clear Diamond Selection", 
                          command=self.clear_diamond_selection).pack(fill=tk.X, pady=3)
                ttk.Separator(self.action_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=3)
            
            # Use tk.Button for better control
            confirm_btn = tk.Button(self.action_frame, text="✓ Confirm Reveal", 
                          command=self.confirm_reveal_diamonds, bg="green", fg="white",
                          font=("Arial", 10, "bold"))
            confirm_btn.pack(fill=tk.X, pady=5)
            return
        
        # Phase 2: Action phase
        ttk.Label(self.action_frame, text="ACTION PHASE", font=("Arial", 10, "bold"), foreground="green").pack()
        ttk.Button(self.action_frame, text="Play Combo", 
                  command=self.play_combo).pack(fill=tk.X, pady=3)
        ttk.Button(self.action_frame, text="Diamond Swap (1x/turn)", 
                  command=self.play_diamond_swap).pack(fill=tk.X, pady=3)
        ttk.Button(self.action_frame, text="Diamond Command", 
                  command=self.play_diamond_command).pack(fill=tk.X, pady=3)
        ttk.Button(self.action_frame, text="Jackpot (if available)", 
                  command=self.play_jackpot).pack(fill=tk.X, pady=3)
        
        ttk.Separator(self.action_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        ttk.Label(self.action_frame, text="UTILITIES", font=("Arial", 9, "bold")).pack()
        ttk.Button(self.action_frame, text="Undo Selection", 
                  command=self.clear_selection).pack(fill=tk.X, pady=3)
        ttk.Button(self.action_frame, text="View Public ♦", 
                  command=self.view_public_diamonds).pack(fill=tk.X, pady=3)
        
        ttk.Separator(self.action_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        ttk.Label(self.action_frame, text="END TURN", font=("Arial", 10, "bold"), foreground="red").pack()
        ttk.Button(self.action_frame, text="End Turn", 
                  command=self.end_turn).pack(fill=tk.X, pady=5)
    
    def clear_selection(self):
        """Clear card selection"""
        self.selected_cards = []
        self.update_hand()
    
    def clear_diamond_selection(self):
        """Clear diamond selection for reveal"""
        self.selected_diamonds_to_reveal = []
        self.update_hand()
    
    def start_turn(self):
        """Start turn: draw a card"""
        try:
            player = self.state.current_player()
            draw_card(self.state, player)
            self.turn_started = True
            self.selected_cards = []
            messagebox.showinfo("Draw", f"Drew a card! You now have {len(player.hand)} cards.")
            self.update_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to draw card: {str(e)}")
            self.update_display()
    
    def play_combo(self):
        """Play selected cards as combo"""
        if not self.selected_cards:
            messagebox.showwarning("No Selection", "Select cards first!")
            return
        
        try:
            player = self.state.current_player()
            initial_steps = player.steps  # Log initial steps
            
            # Separate hand cards and public row cards
            hand_indices = [i for i in self.selected_cards if i < 10000]
            public_indices = [i - 10000 for i in self.selected_cards if i >= 10000]
            
            # Get the actual cards
            cards = []
            cards_from_hand = [player.hand[i] for i in hand_indices]
            cards.extend(cards_from_hand)
            
            public_diamonds = [d for d in self.state.public_diamonds if d.owner_id == player.id]
            public_diamond_objects = []
            for pub_idx in public_indices:
                if pub_idx < len(public_diamonds):
                    cards.append(public_diamonds[pub_idx].card)
                    public_diamond_objects.append(public_diamonds[pub_idx])
            
            # Resolve combo with ALL cards (resolve_combo will identify correctly)
            # But we need to remove public cards before they're processed
            # So we'll handle it specially
            
            # Create a list of indices to remove from hand (for resolve_combo)
            # and track which public cards to remove
            
            # First, remove public diamonds from state
            for pub_d in public_diamond_objects:
                if pub_d in self.state.public_diamonds:
                    self.state.public_diamonds.remove(pub_d)
                    self.state.discard_pile.append(pub_d.card)
            
            # Pass ALL cards to resolve_combo (both hand and public cards combined)
            steps_gained = resolve_combo(self.state, player, cards)
            final_steps = player.steps  # Log final steps
            
            if steps_gained >= 0:  # >= because some combos may have 0 steps but are valid
                # Get combo description from all cards (hand + public)
                combo_desc = self.describe_combo(cards, steps_gained)
                # Add actual steps change to feedback
                actual_gain = final_steps - initial_steps
                messagebox.showinfo("Combo!", f"{combo_desc}\n\n(Steps: {initial_steps} → {final_steps}, +{actual_gain})")
                self.selected_cards = []
                self.update_display()
            else:
                # Restore public diamonds if combo is invalid
                for pub_d in public_diamond_objects:
                    self.state.public_diamonds.append(pub_d)
                    if pub_d.card in self.state.discard_pile:
                        self.state.discard_pile.remove(pub_d.card)
                
                messagebox.showwarning("Invalid Combo", "These cards don't form a valid combo.")
                self.selected_cards = []
                self.update_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play combo: {str(e)}")
            self.selected_cards = []
            self.update_display()
    
    def describe_combo(self, cards: List[Card], steps: int) -> str:
        """Describe the combo that was played"""
        suits = [c.suit for c in cards]
        ranks = [c.rank for c in cards]
        
        # Check for specific combos
        hearts_count = sum(1 for s in suits if s == Suit.HEARTS)
        blacks_count = sum(1 for s in suits if s in [Suit.SPADES, Suit.CLUBS])
        diamonds_count = sum(1 for s in suits if s == Suit.DIAMONDS)
        
        card_str = ", ".join([f"{c.rank.value}{c.suit.value}" for c in cards])
        
        if diamonds_count > 0 and blacks_count > 0:
            return f"♦ Diamond + Black combo! ({card_str})\n+{steps} steps, Draw 1 card"
        elif diamonds_count > 0 and hearts_count > 0:
            return f"♥ Heart + Diamond combo! ({card_str})\n+{steps} steps, Draw 1 card"
        elif len(cards) == 3 and diamonds_count > 0:
            return f"Three-of-a-kind with Diamond! ({card_str})\n+{steps} steps, Draw 1 card"
        elif len(cards) == 3:
            return f"Three-of-a-kind! ({card_str})\n+{steps} steps"
        elif len(cards) == 4:
            return f"Four-of-a-kind! ({card_str})\n+{steps} steps, Draw 1 card"
        elif blacks_count == 2:
            return f"Two blacks! ({card_str})\n+{steps} steps"
        elif hearts_count == 1 and blacks_count == 1:
            return f"Heart + Black! ({card_str})\n+{steps} steps"
        elif hearts_count == 1 and blacks_count == 2:
            return f"Heart + Both Blacks! ({card_str})\n+{steps} steps"
        else:
            return f"Combo! ({card_str})\n+{steps} steps"
    
    def play_diamond_swap(self):
        """Play diamond swap with selection"""
        player = self.state.current_player()
        player_diamonds = [d for d in self.state.public_diamonds if d.owner_id == player.id]
        
        if not player_diamonds:
            messagebox.showwarning("No Diamonds", "You have no public diamonds!")
            return
        
        # Show available targets
        other_players = [p for p in self.state.players if p.id != player.id]
        other_names = [p.name for p in other_players]
        
        # Ask which player to swap with
        swap_choice = simpledialog.askinteger(
            "Diamond Swap",
            f"Select player to swap with:\n{chr(10).join(f'{i}: {n}' for i, n in enumerate(other_names))}",
            minvalue=0,
            maxvalue=len(other_players)-1
        )
        
        if swap_choice is None:
            return
        
        other = other_players[swap_choice]
        other_diamonds = [d for d in self.state.public_diamonds if d.owner_id == other.id]
        
        if not other_diamonds:
            messagebox.showwarning("No Target Diamonds", f"{other.name} has no public diamonds!")
            return
        
        # Show your diamonds to select which one to swap
        my_diamond_str = "\n".join(f"{i}: {d.card.rank.value}{d.card.suit.value}" for i, d in enumerate(player_diamonds))
        
        my_choice = simpledialog.askinteger(
            "Your Diamond",
            f"Select your diamond to swap:\n{my_diamond_str}",
            minvalue=0,
            maxvalue=len(player_diamonds)-1
        )
        
        if my_choice is None:
            return
        
        # Show opponent's diamonds to select which one to swap with
        other_diamond_str = "\n".join(f"{i}: {d.card.rank.value}{d.card.suit.value}" for i, d in enumerate(other_diamonds))
        
        other_choice = simpledialog.askinteger(
            f"{other.name}'s Diamond",
            f"Select {other.name}'s diamond to swap with:\n{other_diamond_str}",
            minvalue=0,
            maxvalue=len(other_diamonds)-1
        )
        
        if other_choice is None:
            return
        
        # Perform the swap
        my_diamond = player_diamonds[my_choice]
        other_diamond = other_diamonds[other_choice]
        
        # Swap ownership
        my_diamond.owner_id = other.id
        other_diamond.owner_id = player.id
        
        messagebox.showinfo("Swap!", 
                           f"Swapped:\n{player.name}'s {my_diamond.card.rank.value}{my_diamond.card.suit.value} → {other.name}\n"
                           f"{other.name}'s {other_diamond.card.rank.value}{other_diamond.card.suit.value} → {player.name}")
        self.update_display()
    
    def play_diamond_command(self):
        """Play diamond command with selection"""
        player = self.state.current_player()
        
        # Check if player has diamonds (in hand or public)
        diamonds_in_hand = player.count_diamonds_in_hand()
        diamonds_in_public = sum(1 for d in self.state.public_diamonds if d.owner_id == player.id)
        
        if diamonds_in_hand == 0 and diamonds_in_public == 0:
            messagebox.showwarning("No Diamonds", f"You have no diamonds to pay! (Hand: {diamonds_in_hand}, Public: {diamonds_in_public})")
            return
        
        # Choose target
        targets = [p for p in self.state.players if p.id != player.id]
        target_names = [p.name for p in targets]
        
        choice = simpledialog.askinteger(
            "Target",
            f"Select target: {', '.join(f'{i}: {n}' for i, n in enumerate(target_names))}",
            minvalue=0,
            maxvalue=len(targets)-1
        )
        
        if choice is None:
            return
        
        target = targets[choice]
        
        # Step 1: Choose which diamond to pay
        diamond_options = []
        diamond_indices = []
        
        # Diamonds from hand
        for i, card in enumerate(player.hand):
            if card.suit == Suit.DIAMONDS:
                diamond_options.append(f"From hand: {card.rank.value}{card.suit.value}")
                diamond_indices.append(('hand', i))
        
        # Diamonds from public row
        public_diamonds = [d for d in self.state.public_diamonds if d.owner_id == player.id]
        for i, public_d in enumerate(public_diamonds):
            diamond_options.append(f"From public row: {public_d.card.rank.value}{public_d.card.suit.value}")
            diamond_indices.append(('public', i))
        
        if not diamond_options:
            messagebox.showwarning("No Diamonds", "You have no diamonds to pay!")
            return
        
        diamond_choice = simpledialog.askinteger(
            "Pay Diamond",
            f"Choose diamond to pay:\n" + "\n".join(f"{i}: {opt}" for i, opt in enumerate(diamond_options)),
            minvalue=0,
            maxvalue=len(diamond_options)-1
        )
        
        if diamond_choice is None:
            return
        
        diamond_location, diamond_idx = diamond_indices[diamond_choice]
        
        # Step 2: Choose which card target should discard
        if len(target.hand) == 0:
            messagebox.showwarning("Empty Hand", f"{target.name} has no cards to discard!")
            return
        
        discard_options = [f"{i}: {card.rank.value}{card.suit.value}" for i, card in enumerate(target.hand)]
        
        discard_choice = simpledialog.askinteger(
            "Target Discards",
            f"{target.name} will discard:\n" + "\n".join(discard_options),
            minvalue=0,
            maxvalue=len(target.hand)-1
        )
        
        if discard_choice is None:
            return
        
        # Execute command
        discarded = diamond_command(
            self.state, player, target,
            diamond_to_pay_idx=diamond_idx if diamond_location == 'hand' else None,
            card_to_discard_idx=discard_choice
        )
        
        if discarded:
            effect_text = ""
            if discarded.suit in [Suit.SPADES, Suit.CLUBS]:
                effect_text = f"\n❌ {target.name} -1 step (black card)"
            elif discarded.suit == Suit.HEARTS:
                effect_text = f"\n✅ {target.name} +1 step (heart card)"
            elif discarded.suit == Suit.DIAMONDS:
                if self.state.is_round1():
                    effect_text = f"\n{target.name} drew 1 card (diamond, round 1)"
                else:
                    effect_text = f"\n⚠️ {target.name} hoarding penalty (diamond)"
            
            messagebox.showinfo(
                "Diamond Command!",
                f"Paid: {diamond_options[diamond_choice]}\n"
                f"{target.name} discarded: {discarded.rank.value}{discarded.suit.value}"
                f"{effect_text}"
            )
        
        self.update_display()
    
    def play_jackpot(self):
        """Play jackpot"""
        player = self.state.current_player()
        
        if jackpot_six_diamonds(self.state, player):
            messagebox.showinfo("Jackpot!", "Gained 6 steps!")
            self.update_display()
        else:
            messagebox.showinfo("No Jackpot", "You don't have 6 diamonds.")
    
    def view_public_diamonds(self):
        """View all public diamonds"""
        text = "=== PUBLIC DIAMONDS ===\n\n"
        for p in self.state.players:
            diamonds = [d for d in self.state.public_diamonds if d.owner_id == p.id]
            if diamonds:
                text += f"{p.name}: {len(diamonds)} diamonds\n"
                for d in diamonds:
                    text += f"  - {d.card.rank.value}{d.card.suit.value}\n"
            else:
                text += f"{p.name}: (no public diamonds)\n"
        messagebox.showinfo("Public Diamonds", text)
    
    def end_turn(self):
        """End current turn - transition to reveal diamonds phase"""
        player = self.state.current_player()
        
        # Step 1: Apply empty hand penalty if needed (before reveal)
        apply_empty_hand_penalty_if_needed(self.state, player)
        
        # Step 2: Transition to diamond reveal phase
        self.revealing_diamonds = True
        self.selected_diamonds_to_reveal = []
        
        # Check if player has any diamonds to reveal
        diamond_indices = [i for i, c in enumerate(player.hand) if c.suit == Suit.DIAMONDS]
        if not diamond_indices:
            messagebox.showinfo("No Diamonds", "You have no diamonds to reveal. Proceeding to next turn...")
            self.confirm_reveal_diamonds()
        else:
            messagebox.showinfo("Reveal Diamonds Phase", 
                               f"You have {len(diamond_indices)} diamond(s). Select which ones to reveal (optional).")
            self.update_display()
    
    def confirm_reveal_diamonds(self):
        """Confirm diamond reveal and advance to next player"""
        try:
            player = self.state.current_player()
            
            # Check if we're in Round 1 or later
            if self.state.round_index > 1:
                # Ask if player wants to reveal diamonds
                choice = messagebox.askyesno(
                    "Reveal Diamonds?",
                    f"Round {self.state.round_index}: Do you want to reveal diamonds from your hand?\n\n"
                    f"(You can partially select which diamonds to reveal)"
                )
                
                if not choice:
                    # Player chose not to reveal
                    messagebox.showinfo("No Reveal", f"{player.name} revealed no diamonds")
                    self.selected_diamonds_to_reveal = []
                else:
                    # Player wants to reveal - let them select
                    self.revealing_diamonds = True
                    self.update_display()
                    messagebox.showinfo("Select Diamonds", 
                                      f"Click on the diamonds you want to reveal, then click 'Confirm Reveal'")
                    return  # Wait for user to click confirm again
            
            # Reveal selected diamonds
            if self.selected_diamonds_to_reveal:
                # Get diamonds to reveal in reverse order to avoid index shifting
                diamonds_to_reveal = []
                for idx in sorted(self.selected_diamonds_to_reveal, reverse=True):
                    card = player.hand[idx]
                    diamonds_to_reveal.append(card)
                    player.hand.pop(idx)
                
                # Add to public diamonds with ownership
                for card in diamonds_to_reveal:
                    pd = PublicDiamond(card=card, owner_id=player.id)
                    self.state.public_diamonds.append(pd)
                
                messagebox.showinfo("Diamonds Revealed", 
                                   f"{player.name} revealed {len(diamonds_to_reveal)} diamond(s)")
            else:
                messagebox.showinfo("No Reveal", f"{player.name} revealed no diamonds")
            
            # Step 3: Check victory
            winner = check_victory(self.state)
            if winner:
                messagebox.showinfo("🏆 VICTORY! 🏆", 
                                  f"{winner.name} wins with {winner.steps} steps!\n\nGame Over!")
                self.new_game()
                return
            
            # Step 4: Advance to next player
            self.state.next_player()
            self.state.turns_completed_total += 1
            
            # Round incrementing is now handled in engine.end_of_turn()
            
            # Reset turn state
            self.turn_started = False
            self.revealing_diamonds = False
            self.selected_cards = []
            self.selected_diamonds_to_reveal = []
            
            next_player = self.state.current_player()
            messagebox.showinfo("Next Turn", f"It's {next_player.name}'s turn!")
            self.update_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to advance turn: {str(e)}\n\nDebug: {repr(e)}")
            self.update_display()


def main():
    """Main GUI entry point"""
    root = tk.Tk()
    app = TowerClashGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
