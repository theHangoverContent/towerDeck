#!/usr/bin/env python3
"""
Tower Clash: Diamonds & Kings - Quick Start Guide
Execute this file to choose your preferred interface.
"""

import subprocess
import sys
import os


def main():
    print("\n" + "="*70)
    print("  🎮 TOWER CLASH: DIAMONDS & KINGS 🎮")
    print("="*70)
    print("\nChoose how to play:\n")
    print("  1. Interactive CLI (terminal-based, full control)")
    print("  2. Graphical Interface (Tkinter, visual)")
    print("  3. Quick Demo (auto-play demo)")
    print("  4. Generate PDF (create printable sheets)")
    print("  5. Run Tests (unit test suite)")
    print("  0. Exit\n")
    
    choice = input("Select option (0-5): ").strip()
    
    if choice == "0":
        print("\nGoodbye! 👋\n")
        return
    
    elif choice == "1":
        print("\n🎮 Starting Interactive CLI...\n")
        subprocess.run([sys.executable, "-m", "src.cli"])
    
    elif choice == "2":
        print("\n🎨 Starting GUI...\n")
        subprocess.run([sys.executable, "-m", "src.gui"])
    
    elif choice == "3":
        print("\n⚡ Running Demo...\n")
        subprocess.run([sys.executable, "-m", "src.main"])
    
    elif choice == "4":
        print("\n📄 Generating PDF...\n")
        subprocess.run([
            sys.executable, "-c",
            "from src.pdf_generator import generate_printables; "
            "path = generate_printables('Tower_Clash_Printables.pdf'); "
            "print(f'✓ PDF created: {path}')"
        ])
    
    elif choice == "5":
        print("\n🧪 Running Tests...\n")
        subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])
    
    else:
        print("\n❌ Invalid option!\n")
        main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAborted! 👋\n")
        sys.exit(0)
