"""
Lesson 3 — Demo 1: references vs copies (the "b = a is not a copy" aha).

A variable is a NAME pointing at an object, not a box holding it.
  b = a          -> a second name for the SAME list. Change one, see it in both.
  c = a.copy()   -> a genuinely separate list.
Immutable objects (tuples) sidestep the whole issue: "changing" one makes a new
object, so the original is never touched.
"""


def main() -> None:
    # b = a is a reference, not a copy
    a = [1, 2, 3]
    b = a               # b and a name the SAME list object
    b.append(99)        # mutating through b is visible through a
    print("b = a (reference):     a is now", a)

    # c = a.copy() is a real copy
    a2 = [1, 2, 3]
    c = a2.copy()       # c is a separate list
    c.append(99)        # changing c does NOT touch a2
    print("c = a.copy() (copy):   a is still", a2)

    # tuples are immutable: "adding" returns a new tuple, original unchanged
    t = (1, 2)
    t2 = t + (3,)       # builds a NEW tuple; t is untouched
    print("tuple add returns new:", t, "->", t2, "original unchanged")


if __name__ == "__main__":
    main()
