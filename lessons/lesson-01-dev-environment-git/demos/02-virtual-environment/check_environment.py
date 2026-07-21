"""
Lesson 1 — Demo 2: prove the virtual environment is real.

Run this BEFORE creating .venv and AGAIN after installing requirements.txt.
The interpreter path changes, and the imports go from failing to working.
"""

import sys


PACKAGES = ["pandas", "numpy", "matplotlib"]


def main():
    print("Python executable:")
    print(f"  {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")
    print()
    print("Package check:")
    for name in PACKAGES:
        try:
            module = __import__(name)
            version = getattr(module, "__version__", "unknown")
            print(f"  [ok]      {name} {version}")
        except ImportError:
            print(f"  [MISSING] {name}")


if __name__ == "__main__":
    main()
