# Demo 3 — Interview Angle

Roughly 30 minutes. The topics from today are exactly the ones early Python/CS interviews probe.
Run this as a **dialogue**: ask the class each question first, take a real answer, *then* show a
model answer and use Claude to critique it.

## 1. The questions (15 min)

Put these up one at a time. Let a student answer out loud before revealing the model answer.

| Question | What a good answer hits |
|---|---|
| What's the difference between a list and a tuple? | List is mutable and ordered; tuple is immutable. Use a tuple for fixed groupings (an OHLC bar) and when you want a hashable key. |
| What does "mutable" mean and why does it matter? | Can be changed in place. Matters because a function can modify a mutable argument the caller still holds — a common source of bugs. |
| What happens when you assign a list to a new variable (`b = a`)? | `b` is another *name* for the same list, not a copy. Mutating through one is visible through the other. Use `a.copy()` for a real copy. |
| What does `try/except` do and when would you use it? | Runs risky code and handles failure instead of crashing. Use it for I/O, network calls, parsing — anything that can fail for reasons outside your control (like scraping). |
| What's the difference between a list and a dict? | List is indexed by position; dict is keyed by label and gives fast lookup by key. Use a dict when you look things up *by* something meaningful. |
| What is a function and why do we use them? | A named, reusable block that takes inputs and returns an output. We use them to avoid repetition, name intent, and test pieces in isolation. |

**Framing to teach:** answer in two beats — a one-sentence definition, then one concrete example.
Interviewers reward clarity and a real example over a memorized paragraph.

**On memory questions:** interviewers often probe references-vs-copies to see if you understand what
Python is *doing*, not just syntax. "A variable is a name pointing at an object" is the sentence that
signals you get it.

## 2. Claude as a mock interviewer (15 min)

Prompt Claude live:

```
Act as an interviewer for an entry-level quant/dev role. Ask me one Python fundamentals question
at a time — lists vs tuples, mutability, references, try/except. Wait for my answer, then ask a
harder follow-up based on what I said. Don't give me the answer up front.
```

Take a volunteer answer, let Claude ask its follow-up, then critique **together as a class**:

```
Here's how a student answered "what happens when you do b = a for a list". Critique it like an
interviewer: what's missing, what's wrong, would you be satisfied?

Student answer: [paste the volunteer's answer]
```

Watch for Claude to flag the specifics: did the answer say "same object, not a copy"? Did it mention
`.copy()`? Did it connect it to the passing-into-a-function bug?

## Talking points

- The value is in explaining out loud — gaps you can hide while reading a definition surface the
  moment you have to say it. That's the same Plan/Code/Review instinct applied to studying.
- AI as a mock interviewer is low-stakes reps: be wrong here for free, not in the real interview.
- Encourage students to run this on their own for the homework's optional reflection.
