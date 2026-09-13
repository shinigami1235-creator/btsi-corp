# -*- coding: utf-8 -*-
"""Lint for the authored copy on the 8BTSI site.

Encodes Gid's writing rules plus the published AI-writing tells. Run it over
content.py and over every authored string the build puts into the HTML.
Manufacturer product text from catalogue.json is checked separately and only
reported, since the facts in it belong to the manufacturer.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

BANNED_WORDS = [
    "crucial", "vital", "pivotal", "robust", "seamless", "seamlessly", "leverage",
    "leveraging", "delve", "underscore", "underscores", "tapestry", "testament",
    "showcase", "showcases", "holistic", "nuanced", "myriad", "realm", "elevate",
    "elevates", "vibrant", "boasts", "nestled", "stands as", "serves as",
    "comprehensive", "cutting-edge", "cutting edge", "streamline", "streamlines",
    "empower", "empowers", "unleash", "unlock", "unlocks", "transformative",
    "revolutionary", "game-changer", "paradigm", "synergy", "scalable",
    "plethora", "multifaceted", "future-ready", "unwavering", "beacon", "symphony",
    "roadmap", "ecosystem", "dive into", "deep dive", "at its core", "navigate the",
    "in today's", "state-of-the-art", "world-class", "best-in-class", "bespoke",
    "curated", "meticulous", "meticulously", "foster", "fosters", "ignite",
    "uncover", "optimise", "optimize", "trusted partner", "one-stop", "solutions provider",
]

BANNED_ADVERBS = [
    "simply", "merely", "truly", "actually", "essentially", "fundamentally",
    "arguably", "seamlessly", "effortlessly", "significantly", "incredibly",
]

BANNED_TICS = [
    # Wikipedia's signs-of-AI-writing list, the shapes not already covered below.
    "let's dive", "let's explore", "let's break", "let's take a look",
    "here's what you need to know", "without further ado", "here's the thing",
    "the thing is", "let's be honest", "to be honest", "look no further",
    "the real question", "at its core", "what really matters", "the deeper issue",
    "the heart of the matter", "in reality,", "is the language of",
    "the currency of", "the architecture of", "becomes a trap",
    "as of this writing", "based on available information", "not publicly available",
    "maintains a low profile", "prefers to stay out", "it is believed that",
    "experts argue", "experts believe", "industry reports", "observers have",
    "some critics argue", "several sources", "studies show that",
    "plays a key role", "plays a crucial role", "plays a vital role",
    "marks a turning point", "represents a shift", "sets the stage",
    "indelible mark", "deeply rooted", "the future looks bright",
    "exciting times", "step in the right direction", "i hope this helps",
    "would you like", "want me to", "let me know if",
    "great question", "you're absolutely right", "in order to",
    "due to the fact", "at this point in time", "in the event that",
    "has the ability to", "it is worth noting", "committed to excellence",
    "commitment to excellence", "must-visit", "look, ",
    "think of it as", "in other words", "the whole point is", "that is what",
    "which is what", "which is why", "the real question is", "at the end of the day",
    "in conclusion", "it is important to", "it's important to", "it is worth noting",
    "furthermore", "moreover", "let's dive", "picture this", "imagine a world",
    "here's the kicker", "that's only half", "why does this matter", "real talk",
    "here's the truth", "rest assured", "look no further", "whether you're",
    "we understand that", "we believe", "we pride ourselves",
]

RULES = [
    ("em/en dash", re.compile(r"[–—]")),
    ("curly quote", re.compile(r"[‘’“”]")),
    ("emoji", re.compile("[\U0001F300-\U0001FAFF☀-➿]")),
    ("negative parallelism: not X but Y",
     re.compile(r"\bnot\s+[^.,;]{1,40},?\s+but\s+", re.I)),
    ("negative parallelism: not only X but",
     re.compile(r"\bnot only\b[^.]{0,60}\bbut\b", re.I)),
    ("negative parallelism: it is not, it is",
     re.compile(r"\b(is|are|was|were)\s+not\b[^.]{0,50},\s*(it|they)\s+(is|are|was|were)\b", re.I)),
    ("tailing , not the",
     re.compile(r",\s*not\s+(the|a|an|this|that|just)\b", re.I)),
    ("demonstrative gloss",
     re.compile(r"(?:^|(?<=[.!?]\s))(That|This|These|Those)\s+(is|are)\b")),
    ("decorative gerund tail",
     re.compile(r",\s+(ensuring|allowing|highlighting|reflecting|meaning|enabling|providing|offering|delivering)\b", re.I)),
    ("X is what makes Y", re.compile(r"\bis what (makes|does|gives)\b", re.I)),
    # "The photo is loaded and nothing is marked." Two facts balanced, nothing to do.
    ("balanced state-declaration with no instruction",
     re.compile(r"\b(is|are|was|were)\s+[^.]{0,40}\band nothing\b", re.I)),
    ("rhetorical question", re.compile(r"\?\s*(?:[A-Z]|$)")),
    # A real scale (3kW to 50kW, 8 to 40 faders) is fine. Two unrelated nouns are not.
    ("from X to Y false range", re.compile(r"\bfrom\s+(?![^\s]*\d)\w+\s+to\s+(?![^\s]*\d)\w+\b", re.I)),
    ("hedge", re.compile(r"\b(may help|can help|might help|seeks to|strives to)\b", re.I)),
    # Copula avoidance: an elaborate construction standing in for "is".
    ("copula avoidance", re.compile(r"\b(serves as|stands as|acts as a|functions as a|boasts|is home to)\b", re.I)),
    # Inflated significance.
    ("inflated significance",
     re.compile(r"\b(a (key|vital|crucial|pivotal|significant) (role|moment|part)|testament to|underscor\w+ (the|its)|highlight\w* (the|its) (importance|significance))\b", re.I)),
    # An inline-header list item: bold label, colon, sentence that restates it.
    ("inline-header list item", re.compile(r"^\*\*[^*]{2,40}:?\*\*:?\s+\w")),
    # Title Case In A Heading.
    ("title case heading", re.compile(r"^#{1,4}\s+(?:[A-Z][a-z]+\s+){2,}[A-Z][a-z]+\s*$")),
    # Stacked hedges.
    ("stacked hedging", re.compile(r"\b(could|might|may)\s+(potentially|possibly|perhaps)\b", re.I)),
    # A hyphenated pair sitting after the noun it describes.
    ("hyphen in predicate position",
     re.compile(r"\b(is|are|was|were|feels|seems)\s+(high|low|long|short|real|data|end|client|cross)-(quality|term|time|driven|to-end|facing|functional)\b", re.I)),
    # A theatrical one-word opener before an ordinary point.
    ("conversational opener", re.compile(r"(?:^|(?<=[.!?]\s))(Honestly|Truthfully|Frankly|Real talk)[?,.]", re.I)),
]


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def check(label, text, strict=True):
    hits = []
    low = text.lower()
    for w in BANNED_WORDS:
        for m in re.finditer(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", low):
            hits.append((label, "banned word: " + w, text[max(0, m.start() - 40):m.end() + 40]))
    for w in BANNED_ADVERBS:
        for m in re.finditer(r"\b" + re.escape(w) + r"\b", low):
            hits.append((label, "filler adverb: " + w, text[max(0, m.start() - 40):m.end() + 40]))
    for w in BANNED_TICS:
        idx = low.find(w)
        if idx >= 0:
            hits.append((label, "tic: " + w, text[max(0, idx - 30):idx + len(w) + 40]))
    for name, rx in RULES:
        for m in rx.finditer(text):
            hits.append((label, name, text[max(0, m.start() - 45):m.end() + 45]))

    # split contrast: a short sentence whose whole job is to negate the one before
    sents = sentences(text)
    for i in range(1, len(sents)):
        s = sents[i]
        if len(s.split()) <= 7 and re.search(r"\b(is|are|was|were|does|do|did|has|have)\s+not\b\.?$", s.strip(), re.I):
            hits.append((label, "split contrast: join to the sentence before", sents[i - 1] + " || " + s))

    # restatement: a sentence sharing most content words with the one before it
    for i in range(1, len(sents)):
        a = set(re.findall(r"[a-z]{4,}", sents[i - 1].lower()))
        b = set(re.findall(r"[a-z]{4,}", sents[i].lower()))
        if b and len(a & b) / len(b) >= 0.75:
            hits.append((label, "restates the sentence before it", sents[i - 1] + " || " + sents[i]))

    # rule of three: three comma-joined parallel items closing a sentence
    for s in sents:
        if re.search(r"\b\w+,\s+\w+,?\s+and\s+\w+\.$", s) and len(s.split()) <= 12:
            hits.append((label, "possible rule of three", s))
    return hits


def walk(obj, path=""):
    out = []
    if isinstance(obj, str):
        out.append((path, obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            out += walk(v, path + "/" + str(k))
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            out += walk(v, path + "[%d]" % i)
    return out


KNOWN_BAD = [
    "Set to Lower face. That is the treated area.",
    "Wrinkles compared. Displacement was not.",
    "It is not a fix, it is a proxy.",
    "A robust and seamless solution for your studio.",
    "The shadow is the lamp, not the treatment.",
    "We simply deliver the equipment, ensuring uptime.",
    "Our journey from concept to delivery.",
    "Why does this matter? Because uptime is crucial.",
    "The station is powered and nothing is on air.",
    "Fast, reliable, and affordable.",
    "The company serves as a trusted partner to broadcasters.",
    "Experts argue that the transmitter plays a key role in coverage.",
    "Honestly? The install went fine.",
    "It could potentially affect the signal.",
    "The report is high-quality and the team is cross-functional.",
    "Let's dive into the specification.",
    "The future looks bright for Philippine broadcast.",
    "Symmetry is the language of trust.",
]

KNOWN_GOOD = [
    "The X.DA series covers AM transmission from 3kW to 50kW at better than 93% efficiency.",
    "Elenos builds FM transmitters from 20W up to 60kW.",
    "Send us the power and the coverage you need and we will come back with a price.",
    "Racks, cabling, grounding and the transmitter site itself.",
    "We train your operators and engineers on the equipment before we leave.",
    "Request a quote",
]


def selftest():
    bad = 0
    for s in KNOWN_BAD:
        if not check("selftest", s):
            print("SELFTEST FAIL: known-bad line passed: %s" % s)
            bad += 1
    for s in KNOWN_GOOD:
        hits = check("selftest", s)
        if hits:
            print("SELFTEST FAIL: known-good line flagged as %s: %s" % (hits[0][1], s))
            bad += 1
    if bad:
        print("%d selftest failure(s)\n" % bad)
    else:
        print("selftest: %d known-bad caught, %d known-good passed\n"
              % (len(KNOWN_BAD), len(KNOWN_GOOD)))
    return bad


FENCE = re.compile(r"^(```|~~~)")
SKIP_LINE = re.compile(r"^\s*(\||!\[|<)")


def walk_markdown(name):
    """Yield one unit of prose at a time from a markdown file.

    A unit is a paragraph, a bullet, a numbered step or a heading, because a
    sentence pair often sits across two lines and a pair rule cannot see it a
    line at a time. Fenced code, indented code, tables and links on their own
    are left alone: a rule about prose has no business reading a regex.

    A bold lead-in comes out as its own unit, since left in the paragraph every
    term it defines looks like a repeated subject.
    """
    path = os.path.join(ROOT, name)
    if not os.path.exists(path):
        return
    lines = open(path, encoding="utf-8").read().split("\n")

    unit, start, fenced = [], 0, False
    def flush(u, ln):
        text = " ".join(x.strip() for x in u).strip()
        if len(text) < 12:
            return None
        # A bold lead-in defines a term; check it apart from what follows.
        m = re.match(r"^\s*(?:[-*]|\d+\.)?\s*\*\*(.+?)\*\*\.?\s*(.*)$", text)
        if m and m.group(2):
            return [("%s:%d" % (name, ln), m.group(1)),
                    ("%s:%d" % (name, ln), m.group(2))]
        return [("%s:%d" % (name, ln), text)]

    for i, line in enumerate(lines, 1):
        if FENCE.match(line.strip()):
            fenced = not fenced
            continue
        if fenced or line.startswith("    ") or line.startswith("\t"):
            continue
        stripped = line.strip()
        starts_unit = (not stripped or stripped.startswith("#")
                       or re.match(r"^([-*]\s|\d+\.\s)", stripped)
                       or SKIP_LINE.match(line))
        if starts_unit and unit:
            out = flush(unit, start)
            if out:
                for item in out:
                    yield item
            unit, start = [], 0
        if not stripped or SKIP_LINE.match(line):
            continue
        if not unit:
            start = i
        unit.append(stripped.lstrip("#").strip())
    if unit:
        out = flush(unit, start)
        if out:
            for item in out:
                yield item


def main():
    import content
    if selftest():
        return 2
    # The testimonials moved to data/testimonials, where they are other
    # people's sentences rather than copy we wrote, so nothing in content.py
    # is exempt any more.
    targets = {n: getattr(content, n) for n in dir(content) if n.isupper()}

    all_hits = []
    for name, obj in targets.items():
        for path, text in walk(obj, name):
            if len(text) < 12:
                continue
            if re.match(r"^(https?:|/|#|\+?\d)", text):
                continue
            all_hits += check(path, text)

    # Lines that trip a rule and are right anyway. Each one is a decision,
    # so it carries its reason.
    ALLOW = [
        # A list of the three posters that exist, rather than three items
        # chosen to sound comprehensive.
        ("HANDOFF_2.md", "telos, omnia and axia", "possible rule of three"),
    ]

    def allowed(label, rule, ctx):
        return any(f in label and frag in ctx and r == rule for f, frag, r in ALLOW)

    n_copy = len(all_hits)
    docs = sorted(f for f in os.listdir(ROOT) if f.endswith(".md"))
    for f in docs:
        for label, text in walk_markdown(f):
            all_hits += [h for h in check(label, text)
                         if not allowed(h[0], h[1], h[2])]

    print("checked %d blocks of authored copy and %s"
          % (len(targets), ", ".join(docs) or "no documents"))

    if not all_hits:
        print("clean: no banned shapes")
        return 0

    print("%d hit(s):\n" % len(all_hits))
    for label, rule, ctx in all_hits:
        print("  [%s]" % rule)
        print("    %s" % label)
        print("    ...%s..." % ctx.replace("\n", " "))
        print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
