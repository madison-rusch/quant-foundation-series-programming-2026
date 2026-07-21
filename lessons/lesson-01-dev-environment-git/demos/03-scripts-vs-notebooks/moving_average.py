"""
Lesson 1 — Demo 3a: the same analysis as a SCRIPT.

Runs top to bottom, same result every time. Diffs cleanly in Git.
Compare with hidden_state.ipynb next door.
"""

PRICES = [101.2, 100.8, 102.5, 103.1, 102.7, 104.0, 105.3, 104.8]
WINDOW = 3


def moving_average(values, window):
    """Simple moving average — one value per full window."""
    return [
        sum(values[i : i + window]) / window
        for i in range(len(values) - window + 1)
    ]


def main():
    averages = moving_average(PRICES, WINDOW)
    print(f"{len(PRICES)} prices, window = {WINDOW}")
    for i, avg in enumerate(averages, start=WINDOW):
        print(f"  day {i}: {avg:.2f}")


if __name__ == "__main__":
    main()
