# Tower Clash: Diamonds & Kings 🎮

A strategic card game implementation in Python with multiple interfaces.

## Features

✅ **Complete Game Engine** - Full implementation of all game rules
✅ **Interactive CLI** - Play with keyboard input
✅ **Simple AI** - Computer players with strategy
✅ **Graphical Interface** - Tkinter-based GUI
✅ **Unit Tests** - Comprehensive test suite with pytest
✅ **PDF Printables** - Game track and cheat sheet
✅ **YAML Config** - Flexible game configuration

## Installation

```bash
pip install -r requirements.txt
```

## Running the Game

### 1. Interactive CLI
```bash
python -m src.cli
```
Play the game in the terminal with full control over actions.

### 2. Graphical Interface (GUI)
```bash
python -m src.gui
```
Play with a visual interface.

### 3. Simple Demo
```bash
python -m src.main
```
Watch an automated game demo.

### 4. Generate PDF Printables
```bash
python -c "from src.pdf_generator import generate_printables; generate_printables('Tower_Clash.pdf')"
```

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run specific tests:
```bash
pytest tests/test_engine.py::TestComboDetection -v
```

## Game Rules

### Overview
- **Players**: 2-4
- **Goal**: Reach 20 steps first
- **Deck**: Standard 52-card deck (use 2 decks for 4 players)

### Key Mechanics

**Combos** (all require same rank):
- Two blacks (♠ + ♣): +1 step
- Heart + black (♥ + ♠/♣): +2 steps
- Heart + both blacks (♥ + ♠ + ♣): +3 steps
- Heart + diamond (♥ + ♦): +1 step, draw 1
- Diamond + black (♦ + ♠/♣): discard 1, draw 1
- Three of a kind (+ ♦): +1 step, discard 1, draw 1
- Four of a kind: +3 steps, draw 1
- **Four Kings** (♥♠♣♦): +6 steps, draw 2

**Diamonds** 🔷:
- Automatically revealed at end of turn
- **Diamond Swap**: Exchange ownership with another player (once/turn)
- **Diamond Command**: Pay 1 ♦ to force opponent to discard
- **Jackpot**: 6 diamonds → +6 steps + redraw

**Kings** 👑:
- Double step gains on combos
- Discard effects:
  - Black King: -2 steps
  - Heart King: +2 steps
  - Diamond King: draw 2

### Turn Sequence
1. **Draw Phase**: Draw 1 card
2. **Action Phase** (choose one or more):
   - Play cards / cash-in combos
   - Diamond Swap (once)
   - Diamond Command
   - Jackpot check
3. **End of Turn**:
   - Empty hand penalty (-1 step, draw 6)
   - Reveal all diamonds to public row
   - Check for winner

## Project Structure

```
towerDeck/
├── game.yaml              # Game configuration
├── requirements.txt       # Dependencies
├── README.md             # This file
├── src/
│   ├── __init__.py       # Package exports
│   ├── models.py         # Game data classes
│   ├── engine.py         # Core game logic
│   ├── game_loader.py    # YAML loading
│   ├── ai.py             # AI player strategy
│   ├── cli.py            # Interactive CLI interface
│   ├── gui.py            # Tkinter GUI
│   ├── pdf_generator.py  # PDF generation
│   └── main.py           # Simple demo
└── tests/
    └── test_engine.py    # Unit tests
```

## Development

### Adding New Features

1. **New Game Rules**: Update `game.yaml` and modify `src/engine.py`
2. **AI Strategy**: Enhance `src/ai.py` with better logic
3. **GUI**: Improve `src/gui.py` (Tkinter or other frameworks)
4. **Tests**: Add to `tests/test_engine.py`

### Code Organization

- **Models** (`models.py`): Data structures (Card, Player, GameState)
- **Engine** (`engine.py`): Game logic (draw, discard, combos, penalties)
- **Loader** (`game_loader.py`): YAML configuration parsing
- **AI** (`ai.py`): Computer player decision-making
- **UI** (`cli.py`, `gui.py`): User interfaces

## Testing Examples

```python
# Test combo detection
from src.models import Card, Rank, Suit
from src.engine import identify_combo

cards = [
    Card(Rank.ACE, Suit.HEARTS),
    Card(Rank.ACE, Suit.SPADES)
]
assert identify_combo(cards) == "heart_plus_black"

# Test player diamonds
player = Player(id=0, name="Alice")
player.hand = [Card(Rank.ACE, Suit.DIAMONDS)]
assert player.count_diamonds_in_hand() == 1
```

## Future Enhancements

- [ ] Web-based interface (Flask/React)
- [ ] Network multiplayer
- [ ] Advanced AI with learning
- [ ] Mobile app
- [ ] Tournament mode
- [ ] Game replays/logging

## License

MIT License - Feel free to use and modify!

## Contributing

Pull requests welcome! Please ensure tests pass before submitting.