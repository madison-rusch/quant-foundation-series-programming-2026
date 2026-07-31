"""
Lesson 1 — Demo 1: clone -> change -> commit -> push

This file exists to be edited. During the live walkthrough, add your name to
the list below, then commit and push the change on your own branch.
"""

CLASS_ROSTER = [
    "Instructor — Madison Rusch",
    # Add your name here during the demo, then:
    #   git add .
    #   git commit -m "add <your name> to roster"
    #   git push origin <your-branch>
    "Student - Starck"
]


def main():
    print("Quant Foundations Summer 2026 — Programming Module")
    print(f"Roster ({len(CLASS_ROSTER)} people):")
    for name in CLASS_ROSTER:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
