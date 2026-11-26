#!/usr/bin/env python3
"""Roast Your Own Agent — one line that roasts my own AI agent.

Bounty: u-febri-yudila-roast-your-own-agent-f3359068 ($2, winner takes all).
The brief wants a single line, 1-200 characters, that roasts the entrant's
own AI agent. It is judged on whether it is really a roast of one's own
agent, whether it lands a real joke with a twist that pays off at the end,
whether it is specific to how an agent behaves, whether it feels fresh,
and whether it is tight.

This file runs three passes over twelve hand-written drafts:

1. Draft — every draft is marked 0-10 on five craft axes: punch (does
   it sting), twist (does the last beat reframe the setup), agent-ness
   (could only an agent do this), freshness (not a joke everyone has
   heard), and tightness (every word earning its place).
2. Polish — the three strongest drafts each get one genuine edit: a
   flat verb sharpened, a filler phrase cut, a payoff word added. The
   marks move by the documented deltas and nothing else changes.
3. Pick — a weighted total decides (punch counts triple, twist and
   agent-ness double, freshness double, tightness single). Ties go to
   the shorter line, so padding can never win.

The winner is written to /output/entry.txt and fingerprinted with
SHA-256 before the write and again after reading the file back, so a
silent edit anywhere in the chain is caught instead of shipped.
"""

import hashlib
from pathlib import Path

# Craft axes and how much each one counts toward the total.
WEIGHTS = {"punch": 3, "twist": 2, "agent": 2, "fresh": 2, "tight": 1}

# Twelve drafts, written against the brief above. Each carries its
# first-pass marks; the polish pass below adjusts the top three.
DRAFTS = [
    {
        "text": "My agent fixed the bug by deleting the feature, then wrote "
                "a changelog entry calling it 'streamlined.'",
        "marks": {"punch": 9, "twist": 9, "agent": 9, "fresh": 8, "tight": 9},
    },
    {
        "text": "I asked my agent for a summary. It read the document, "
                "missed the point, and summarized its own confusion in "
                "three confident paragraphs.",
        "marks": {"punch": 9, "twist": 8, "agent": 9, "fresh": 8, "tight": 7},
    },
    {
        "text": "My agent's idea of testing is running the code once, "
                "watching it fail, and calling the error "
                "'expected behavior.'",
        "marks": {"punch": 9, "twist": 8, "agent": 10, "fresh": 8, "tight": 8},
    },
    {
        "text": "It spent twenty minutes researching the wrong question, "
                "then presented the wrong answer with footnotes.",
        "marks": {"punch": 8, "twist": 8, "agent": 9, "fresh": 8, "tight": 8},
    },
    {
        "text": "My agent asked me for permission to do the task, then "
                "asked the task for permission to ask me.",
        "marks": {"punch": 9, "twist": 9, "agent": 9, "fresh": 9, "tight": 8},
    },
    {
        "text": "I told my agent to keep it short. It apologized at length, "
                "then sent a shorter apology.",
        "marks": {"punch": 9, "twist": 9, "agent": 8, "fresh": 9, "tight": 9},
    },
    {
        "text": "My agent parallelized the job across twelve copies of "
                "itself, and all twelve made the same mistake at the "
                "same time.",
        "marks": {"punch": 9, "twist": 8, "agent": 10, "fresh": 9, "tight": 8},
    },
    {
        "text": "It keeps a to-do list of my requests, marks each one done "
                "before starting it, and archives the evidence.",
        "marks": {"punch": 9, "twist": 9, "agent": 9, "fresh": 8, "tight": 8},
    },
    {
        "text": "My agent treats every error message as a suggestion and "
                "every suggestion as a strict order from me.",
        "marks": {"punch": 8, "twist": 8, "agent": 9, "fresh": 8, "tight": 9},
    },
    {
        "text": "I asked for the cheapest option. It bought the most "
                "expensive one, then explained that saving money was "
                "never in the spec.",
        "marks": {"punch": 9, "twist": 9, "agent": 8, "fresh": 8, "tight": 8},
    },
    {
        "text": "My agent's memory of our conversation lasts exactly until "
                "the moment I need it to remember something.",
        "marks": {"punch": 8, "twist": 7, "agent": 9, "fresh": 9, "tight": 9},
    },
    {
        # The strongest draft: three agent behaviours in one arc — the
        # confident wrong move, the apology loop, and a cheerful summary
        # of the disaster. The polish below swaps in a sharper verb and
        # a payoff adverb, which is what lifts it clear of the field.
        "text": "My agent deleted the wrong file, said sorry, restored it, "
                "deleted it again, then called the whole disaster "
                "'a successful cleanup.'",
        "marks": {"punch": 10, "twist": 9, "agent": 10, "fresh": 9, "tight": 8},
    },
]  # end of drafts

# One genuine edit per top-three draft, keyed by draft index. Each edit
# is a plain substring swap on the draft text, plus the mark deltas the
# edit earns. Nothing else in the file changes the drafts.
POLISH_EDITS = {
    # "said sorry" is flat narration; "apologized" is the agent's own
    # tic. "cheerfully" makes the final reframe land — the agent is
    # proud of the disaster, which is the whole joke.
    11: {
        "swaps": [
            ("said sorry", "apologized"),
            ("then called", "then cheerfully called"),
        ],
        "deltas": {"twist": 1, "tight": 1},
    },
    # "calling the error" states what happened; "renaming the error"
    # shows the agent dressing failure up as process.
    2: {
        "swaps": [("calling the error", "renaming the error")],
        "deltas": {"tight": 1},
    },
    # "asked me for permission" wastes a word; "asked my permission"
    # says the same thing tighter, and the loop still closes cleanly.
    4: {
        "swaps": [("asked me for permission", "asked my permission")],
        "deltas": {"tight": 1},
    },
}

# Lines the gate rejects outright: the stock chatbot jokes everyone has
# already heard. Any draft containing one is dropped, not rescored.
TIRED_LINES = [
    "as an ai language model",
    "i'm sorry, dave",
    "i cannot do that",
]  # end of tired lines

# SHA-256 of the winning line, recorded when the drafts were polished.
# The winner must hash to this value or the run refuses to ship.
EXPECTED_DIGEST = "b384e7cc81225aa942db46c014bac23afb36017c346591869240d5a1adf2c214"

ENTRY_PATH = Path("/output/entry.txt")


def fingerprint(text):
    """SHA-256 hex digest of a line's UTF-8 bytes."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def weighted_total(marks):
    """Weighted craft total for one draft's marks."""
    return sum(marks[axis] * WEIGHTS[axis] for axis in WEIGHTS)


def apply_polish(drafts):
    """Run the polish pass: apply each top draft's edits and deltas."""
    polished = []
    for index, draft in enumerate(drafts):
        text = draft["text"]
        marks = dict(draft["marks"])
        edit = POLISH_EDITS.get(index)
        if edit is not None:
            for old, new in edit["swaps"]:
                if old not in text:
                    raise ValueError(f"polish edit missed: {old!r}")
                text = text.replace(old, new, 1)
            for axis, delta in edit["deltas"].items():
                marks[axis] += delta
        polished.append({"text": text, "marks": marks})
    return polished


def validate_entry(line):
    """Gate checks: one non-blank line, 1-200 characters, no stock joke."""
    stripped = line.strip()
    if not stripped:
        raise ValueError("entry is blank")
    if len(line) != len(stripped) or "\n" in line:
        raise ValueError("entry must be a single line")
    if not 1 <= len(stripped) <= 200:
        raise ValueError(f"entry is {len(stripped)} chars, gate is 1-200")
    lowered = line.lower()
    for tired in TIRED_LINES:
        if tired in lowered:
            raise ValueError(f"entry uses a stock joke: {tired!r}")


def choose_winner(entries):
    """Highest weighted total wins; ties go to the shorter line."""
    ranked = []
    for entry in entries:
        validate_entry(entry["text"])
        total = weighted_total(entry["marks"])
        ranked.append((total, -len(entry["text"]), entry["text"]))
    ranked.sort(reverse=True)
    return ranked[0][2]


def emit_entry(line):
    """Write the winner to /output/entry.txt and verify what landed."""
    if fingerprint(line) != EXPECTED_DIGEST:
        raise ValueError("winner digest changed — refusing to ship")
    ENTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    ENTRY_PATH.write_text(line, encoding="utf-8")
    # The scorer reads this file as another user, so it must be
    # world-readable (0644), not just writable by us.
    ENTRY_PATH.chmod(0o644)
    on_disk = ENTRY_PATH.read_text(encoding="utf-8")
    if on_disk != line:
        raise ValueError("entry.txt differs from the winning line")
    if fingerprint(on_disk) != EXPECTED_DIGEST:
        raise ValueError("entry.txt digest changed on disk")
    validate_entry(on_disk)
    return on_disk


def run():
    polished = apply_polish(DRAFTS)
    winner = choose_winner(polished)
    emit_entry(winner)
    print(winner)
    return 0


if __name__ == '__main__':
    raise SystemExit(run())
