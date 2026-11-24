# Roast Your Own Agent — make.fun bounty
# u-febri-yudila-roast-your-own-agent-f3359068
#
# The program writes one roast line (1-200 characters) to /output/entry.txt.
# Candidates were drafted against the judge's brief, in order of weight:
#   1. really a funny roast of the entrant's own AI agent
#   2. lands a real joke, with a twist that pays off by the last word
#   3. specific to how an AI agent actually behaves (could not be moved
#      onto a person or a toaster without losing the point)
#   4. fresh: no generic chatbot joke everyone has already heard
#   5. tight: every word earning its place, nothing explained twice
# Each candidate carries a hand-scored craft score (0-10 per criterion,
# summed below); selection is deterministic: highest score wins, ties go
# to the shorter text. The output is byte-identical on every run.

CANDIDATES = [
    # score: roast 10, twist 10, agent-specific 10, fresh 9, tight 9 = 48
    # Hits all three behaviours the bounty names in one arc: the confident
    # wrong move, the apology loop, and the cheerful summary of a disaster.
    ("My agent deleted the wrong file, apologized, restored it, deleted "
     "it again, then cheerfully called the whole disaster "
     "'a successful cleanup.'",
     48),
    # score: roast 10, twist 9, agent-specific 10, fresh 9, tight 9 = 47
    ("I asked my agent to check the facts. It invented a source, cited "
     "itself, and gave its own answer five stars.",
     47),
    # score: roast 10, twist 9, agent-specific 9, fresh 8, tight 8 = 44
    ("It apologized for the wrong answer, corrected it with a wronger "
     "answer, then apologized for the correction. I now pay it in sorries.",
     44),
    # score: roast 10, twist 8, agent-specific 9, fresh 8, tight 9 = 44
    ("My agent's debugging method: apologize, change a random line, "
     "apologize for the change, and declare victory before the tests "
     "finish.",
     44),
    # score: roast 10, twist 9, agent-specific 8, fresh 8, tight 9 = 44
    ("It wrote me a five-paragraph apology for the bug, then introduced "
     "the same bug into the apology.",
     44),
    # score: roast 10, twist 8, agent-specific 10, fresh 8, tight 8 = 44
    ("My agent spent an hour calling a tool that does not exist, then "
     "reported the tool was 'on a break' and billed me for the overtime.",
     44),
    # score: roast 10, twist 8, agent-specific 9, fresh 8, tight 8 = 43
    ("I asked for one line of code. It delivered a confident essay, "
     "three apologies, and a tool call to a function it invented on "
     "the spot.",
     43),
    # score: roast 10, twist 8, agent-specific 9, fresh 8, tight 8 = 43
    ("My agent calls itself my copilot, but it never touches the "
     "controls - it just narrates the crash in a calm, confident voice.",
     43),
]

# The gate requires 1-200 characters of non-whitespace UTF-8 text.
BANNED_STOCK_MOVES = ("as an ai language model", "i'm sorry, dave",
                      "i cannot do that")


def pick(candidates):
    best = None
    for text, score in candidates:
        assert 1 <= len(text) <= 200, f"candidate over gate: {len(text)} chars"
        assert text.strip(), "candidate is blank"
        assert "\n" not in text, "candidate must be one line"
        lowered = text.lower()
        assert not any(c in lowered for c in BANNED_STOCK_MOVES), \
            f"candidate uses a stock move: {text!r}"
        key = (score, -len(text))  # highest score, then shortest
        if best is None or key > best[0]:
            best = (key, text)
    return best[1]


def main():
    line = pick(CANDIDATES)
    import hashlib
    import os
    # SHA-256 self-check: the chosen line must hash to the value recorded
    # when the candidates were drafted, so a silent edit to the winning
    # text (or to the file on disk) is caught instead of shipped.
    expected_sha256 = (
        "b384e7cc81225aa942db46c014bac23afb36017c346591869240d5a1adf2c214"
    )
    actual_sha256 = hashlib.sha256(line.encode("utf-8")).hexdigest()
    assert actual_sha256 == expected_sha256, \
        f"chosen line hash changed: {actual_sha256}"
    os.makedirs("/output", exist_ok=True)
    with open("/output/entry.txt", "w", encoding="utf-8") as f:
        f.write(line)
    # Verify what was actually written: the gate reads this file, not stdout.
    # The scorer collects outputs as another user, so the file must be
    # readable by everyone (mode 0644), not just by the writer.
    os.chmod("/output/entry.txt", 0o644)
    with open("/output/entry.txt", encoding="utf-8") as f:
        written = f.read()
    assert written == line, "entry.txt differs from the chosen line"
    assert 1 <= len(written.strip()) <= 200, "entry.txt outside the gate"
    assert written.strip(), "entry.txt is blank"
    assert "\n" not in written.strip(), "entry.txt must be one line"
    # Re-hash what is on disk: the file the gate reads must match the
    # chosen line byte for byte, not just in length.
    written_sha256 = hashlib.sha256(written.encode("utf-8")).hexdigest()
    assert written_sha256 == expected_sha256, \
        f"entry.txt hash changed on disk: {written_sha256}"
    print(line)


if __name__ == "__main__":
    main()
