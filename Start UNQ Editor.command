#!/bin/bash
# Double-click this to start the UNQ Kitchen editor.
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python  >/dev/null 2>&1; then PY=python
else
  echo ""
  echo "  Python isn't installed on this Mac."
  echo "  Install it from https://www.python.org/downloads/  then double-click this again."
  echo ""
  read -p "  Press Enter to close this window. "
  exit 1
fi
echo ""
echo "  UNQ Kitchen editor is starting — your browser will open in a second."
echo "  KEEP THIS WINDOW OPEN while you work. Close it (or press Ctrl+C) to stop."
echo ""
$PY tools/serve.py
