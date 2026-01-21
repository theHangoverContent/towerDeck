"""
Tower Clash: Diamonds & Kings - Quick Start Guide
Get up and running in 60 seconds!
"""

# INSTALLATION
# ============================================================================
# pip install -r requirements.txt

# RUNNING THE GAME
# ============================================================================

# 1. QUICK START (Interactive Menu)
#    python run.py
#    Choose from:
#      - Interactive CLI (play in terminal)
#      - Graphical GUI (visual interface)
#      - Watch Demo (auto-play)
#      - Generate PDF (printable sheets)
#      - Run Tests (unit tests)

# 2. INTERACTIVE CLI (Recommended for first-time players)
#    python -m src.cli
#
#    Features:
#    - Human vs AI or Human vs Human
#    - Full control over card selection
#    - Clear action menus
#    - Real-time game status
#
#    How to play:
#    1. Choose if each player is Human or AI
#    2. Cards are displayed in your hand
#    3. Select actions from menu
#    4. Select cards by number for combos
#    5. See game state update in real-time

# 3. GRAPHICAL GUI (Easiest interface)
#    python -m src.gui
#
#    Features:
#    - Visual card display
#    - Click to select cards
#    - Button-based actions
#    - Game status panel
#
#    How to play:
#    1. Cards shown on screen
#    2. Click cards to select (highlighted when selected)
#    3. Click action buttons
#    4. Watch status panel for results

# 4. DEMO MODE (Watch the game)
#    python -m src.main
#
#    Features:
#    - Watch AI players play
#    - See game mechanics in action
#    - Learn the rules by observation

# 5. RUN TESTS (Verify everything works)
#    pytest tests/ -v
#    pytest tests/ -v --cov=src  # with coverage report

# 6. GENERATE PRINTABLES
#    python -c "from src.pdf_generator import generate_printables; generate_printables('Tower_Clash_Printables.pdf')"

# GAME RULES (TL;DR)
# ============================================================================

# WINNING: Be first to reach 20 steps

# TURN SEQUENCE:
#   1. Draw 1 card
#   2. Play cards:
#      - Combos (same rank)
#      - Diamond actions
#      - Other effects
#   3. End turn: Reveal diamonds, check penalties

# COMBOS (step gains):
#   ♠ + ♣ (two blacks)              = +1
#   ♥ + (♠ or ♣)                    = +2
#   ♥ + ♠ + ♣                       = +3
#   ♥ + ♦ (+ draw 1)                = +1
#   ♦ + (♠ or ♣) (+ discard 1)      = 0
#   3 of kind (+ ♦) (+ discard 1)   = +1
#   4 of kind (+ draw 1)             = +3
#   4 Kings Special (+ draw 2)       = +6

# DIAMOND SYSTEM:
#   - Reveal all diamonds at end of turn
#   - Swap ownership once per turn
#   - Pay diamond to force opponent discard
#   - 6 diamonds total = +6 steps jackpot

# KINGS:
#   - Double step gains on combos
#   - ♠ King discarded: -2 steps
#   - ♥ King discarded: +2 steps
#   - ♦ King discarded: draw 2

# PROJECT STRUCTURE
# ============================================================================
#
# towerDeck/
# ├── run.py              # 🚀 Main menu
# ├── game.yaml           # ⚙️ Configuration
# ├── requirements.txt    # 📦 Dependencies
# ├── README.md           # 📖 Documentation
# ├── ARCHITECTURE.md     # 🏗️ Technical guide
# │
# ├── src/
# │   ├── models.py       # 📊 Data structures
# │   ├── engine.py       # ⚙️ Game logic
# │   ├── game_loader.py  # 🔧 Config loader
# │   ├── ai.py           # 🤖 AI players
# │   ├── cli.py          # 💻 Terminal UI
# │   ├── gui.py          # 🎨 Tkinter UI
# │   ├── pdf_generator.py # 📄 PDF export
# │   └── main.py         # ▶️ Demo
# │
# └── tests/
#     └── test_engine.py  # 🧪 Unit tests

# CUSTOMIZATION
# ============================================================================

# CHANGING GAME RULES:
#   1. Edit game.yaml
#   2. Modify values under 'victory', 'combos', etc.
#   3. Restart game - it auto-loads new config

# IMPROVING AI:
#   1. Edit src/ai.py
#   2. Modify combo_value() for strategy
#   3. Extend decide_action() for new logic

# MODIFYING GUI:
#   1. Edit src/gui.py
#   2. Adjust colors, fonts, sizes
#   3. Add new buttons or displays

# TROUBLESHOOTING
# ============================================================================

# ERROR: game.yaml not found
#   → Run from project root directory
#   → cd towerDeck && python run.py

# ERROR: tkinter not found
#   → On Ubuntu: sudo apt-get install python3-tk
#   → On Mac: brew install python-tk
#   → Use CLI interface instead: python -m src.cli

# ERROR: pytest not found
#   → pip install pytest

# ERROR: Module not found
#   → pip install -r requirements.txt
#   → Check you're in correct directory

# GAME STATISTICS
# ============================================================================
#
# Total Code: ~2,200 lines
# Test Coverage: 31 unit tests
# Combos Implemented: 7 types
# King Effects: 3 types
# Interfaces: 4 different (CLI, GUI, Demo, Tests)

# FEATURES IMPLEMENTED
# ============================================================================
# ✓ Complete game engine
# ✓ 7 combo types with detection
# ✓ King mechanics with discards
# ✓ Diamond system (swap, command, jackpot, hoarding)
# ✓ AI with strategy
# ✓ Interactive CLI
# ✓ Tkinter GUI
# ✓ 31 comprehensive unit tests
# ✓ YAML configuration
# ✓ PDF generation
# ✓ Complete documentation

# SUPPORT & NEXT STEPS
# ============================================================================
#
# Want to learn more?
#   → Read README.md for full documentation
#   → Check ARCHITECTURE.md for technical details
#   → Look at test_engine.py for usage examples

# Want to extend the game?
#   → Add new combo types in game.yaml + engine.py
#   → Improve AI in ai.py with better heuristics
#   → Create web interface with Flask/React
#   → Add multiplayer networking

# Found a bug?
#   → Run pytest to verify
#   → Check the specific function in engine.py
#   → Review test cases for expected behavior

# Need help?
#   → Run: python run.py
#   → Try each interface
#   → Read documentation files
#   → Check unit tests for examples

print(__doc__)
