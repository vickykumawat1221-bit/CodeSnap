#!/usr/bin/env python3
"""
run.py - CodeSnap IDE & Compiler Server Launcher
Usage:
    python3 run.py
"""

import sys
import os
import socket

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app import app

def get_free_port(preferred_port=5050):
    env_port = os.environ.get("PORT")
    if env_port:
        try:
            p = int(env_port)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', p))
                return p
        except OSError:
            pass

    for p in [preferred_port, 5001, 8080, 5000]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', p))
                return p
        except OSError:
            continue
    return preferred_port

if __name__ == "__main__":
    port = get_free_port(5050)
    print("=" * 65)
    print("  🚀 CodeSnap - Mini Programming Language Compiler & IDE")
    print("  📚 CSE Department Theory of Computation (TOC) Mini-Project")
    print(f"  🌐 Running locally on: http://localhost:{port}")
    print("  Press Ctrl+C to stop the server.")
    print("=" * 65)
    app.run(host="0.0.0.0", port=port, debug=False)
