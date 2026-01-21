#!/bin/bash
# Tower Clash Game Launcher

cd /workspaces/towerDeck
export DISPLAY=:99
python -m src.gui 2>&1 | tee /tmp/gui.log
