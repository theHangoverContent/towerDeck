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
        self.root.geometry("1200x800")
        
        self.state: Optional[GameState] = None
        self.selected_cards: List[int] = []
        self.card_buttons = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the main UI"""
        # Title
        title = ttk.Label(self.root, text="🎮 Tower Clash: Diamonds & Kings 🎮", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
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
            self.update_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start game: {e}")
    
    def update_display(self):
        """Update the entire display"""
        if not self.state:
            return
        
        # Update status
        self.update_status()
        
        # Update hand
        self.update_hand()
        
        # Update actions
        self.update_actions()
    
    def update_status(self):
        """Update game status display"""
        self.status_text.delete("1.0", tk.END)
        
        player = self.state.current_player()
        text = f"""
=== Game Status ===
Round: {self.state.round_index}
Turn: {self.state.turns_completed_total}

Current Player: {player.name}
Steps: {player.steps}/20

Players:
"""
        for p in self.state.players:
            diamonds = sum(1 for c in p.hand if c.suit == Suit.DIAMONDS)
            text += f"  {p.name}: {p.steps} steps ({len(p.hand)} cards, {diamonds}♦)\n"
        
        text += f"""
Deck: {len(self.state.draw_pile)} cards
Discard: {len(self.state.discard_pile)} cards
Public ♦: {len(self.state.public_diamonds)}
"""
        
        self.status_text.insert("1.0", text)
        self.status_text.config(state=tk.DISABLED)
    
    def update_hand(self):
        """Update hand display"""
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        
        self.card_buttons = {}
        player = self.state.current_player()
        
        if not player.hand:
            ttk.Label(self.hand_frame, text="(No cards in hand)").pack()
            return
        
        # Create a frame for scrolling if needed
        canvas = tk.Canvas(self.hand_frame)
        scrollbar = ttk.Scrollbar(self.hand_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)
        
        # Add cards
        for i, card in enumerate(player.hand):
            self.add_card_button(scrollable_frame, i, card)
        
        canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
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
    
    def update_actions(self):
        """Update action buttons"""
        for widget in self.action_frame.winfo_children():
            widget.destroy()
        
        ttk.Button(self.action_frame, text="Play Combo", 
                  command=self.play_combo).pack(fill=tk.X, pady=5)
        ttk.Button(self.action_frame, text="Diamond Swap", 
                  command=self.play_diamond_swap).pack(fill=tk.X, pady=5)
        ttk.Button(self.action_frame, text="Diamond Command", 
                  command=self.play_diamond_command).pack(fill=tk.X, pady=5)
        ttk.Button(self.action_frame, text="Jackpot (if available)", 
                  command=self.play_jackpot).pack(fill=tk.X, pady=5)
        ttk.Button(self.action_frame, text="End Turn", 
                  command=self.end_turn).pack(fill=tk.X, pady=5)
        
        ttk.Label(self.action_frame, text="", font=("Arial", 8)).pack()
        ttk.Button(self.action_frame, text="Undo Selection", 
                  command=self.clear_selection).pack(fill=tk.X, pady=5)
    
    def clear_selection(self):
        """Clear card selection"""
        self.selected_cards = []
        self.update_hand()
    
    def play_combo(self):
        """Play selected cards as combo"""
        if not self.selected_cards:
            messagebox.showwarning("No Selection", "Select cards first!")
            return
        
        player = self.state.current_player()
        cards = [player.hand[i] for i in sorted(self.selected_cards)]
        
        steps_gained = resolve_combo(self.state, player, cards)
        if steps_gained > 0:
            messagebox.showinfo("Combo!", f"Gained {steps_gained} steps!")
        else:
            messagebox.showwarning("Invalid Combo", "These cards don't form a valid combo.")
        
        self.selected_cards = []
        self.update_display()
    
    def play_diamond_swap(self):
        """Play diamond swap"""
        player = self.state.current_player()
        player_diamonds = [d for d in self.state.public_diamonds if d.owner_id == player.id]
        
        if not player_diamonds:
            messagebox.showwarning("No Diamonds", "You have no public diamonds!")
            return
        
        # Simple: choose first other player
        other = next((p for p in self.state.players if p.id != player.id), None)
        if not other:
            return
        
        diamond_swap(self.state, player, other)
        messagebox.showinfo("Swap!", f"Swapped with {other.name}")
        self.update_display()
    
    def play_diamond_command(self):
        """Play diamond command"""
        player = self.state.current_player()
        
        if player.count_diamonds_in_hand() == 0 and len(player.public_diamonds) == 0:
            messagebox.showwarning("No Diamonds", "You have no diamonds to pay!")
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
        diamond_command(self.state, player, target)
        messagebox.showinfo("Command!", f"Used on {target.name}")
        self.update_display()
    
    def play_jackpot(self):
        """Play jackpot"""
        player = self.state.current_player()
        
        if jackpot_six_diamonds(self.state, player):
            messagebox.showinfo("Jackpot!", "Gained 6 steps!")
            self.update_display()
        else:
            messagebox.showinfo("No Jackpot", "You don't have 6 diamonds.")
    
    def end_turn(self):
        """End current turn"""
        player = self.state.current_player()
        
        # Draw card first if this is start of turn
        if len(player.hand) < 6:  # Simplified check
            draw_card(self.state, player)
        
        # End of turn
        apply_empty_hand_penalty_if_needed(self.state, player)
        end_of_turn_reveal_diamonds(self.state, player)
        
        self.state.turns_completed_total += 1
        if self.state.turns_completed_total == len(self.state.players):
            self.state.round_index = 2
        
        # Check victory
        winner = check_victory(self.state)
        if winner:
            messagebox.showinfo("Victory!", f"{winner.name} wins with {winner.steps} steps!")
            self.new_game()
            return
        
        # Next player
        self.state.next_player()
        self.selected_cards = []
        self.update_display()


def main():
    """Main GUI entry point"""
    root = tk.Tk()
    app = TowerClashGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
