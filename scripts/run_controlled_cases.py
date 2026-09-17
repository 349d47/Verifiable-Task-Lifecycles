#!/usr/bin/env python3
"""Run the 12 deterministic tests from the command line."""
import subprocess, sys
raise SystemExit(subprocess.call([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v']))
