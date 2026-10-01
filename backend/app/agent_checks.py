"""A visible check on the assistant's prose: numbers the engine never produced, and forecast or causal wording.

Prompts reduce these with strong models but do not stop them with small local ones: a live qwen3:8b explained a
journey with "adoption peaks 14 days earlier (day 165)" and "boost credibility to accelerate adoption by 12.5%", none of
which any tool returned. The check cannot stop the model writing that; it makes sure the researcher sees a warning.
"""
import re

NUMBER = re.compile(r'(?<![\w.])[-−]?\d+(?:[.,]\d+)?\s*%?')
# Words the reporting rules forbid. A negation shortly before ("cannot show what causes") is not a claim.
CLAIMS = re.compile(r'\b(will (?:reach|increase|rise|grow|improve|boost)|caus(?:es|ed|ing)|cause|dr(?:ive|ives|iving|iven|ove)|'
                    r'leads? to|boost(?:s|ed|ing)?|accelerat\w*|predict\w*|forecasts?(?!\w)|validat\w*|(?<!un)calibrated|'
                    r'significant(?:ly)?|robust|recommend\w*|actionable|most (?:effective|efficient|scalable))\b', re.I)
NEGATION = re.compile(r"\b(not|cannot|can't|never|no|nor|without|isn't|aren't|doesn't|don't)\b[^.]{0,40}$", re.I)
TRIVIAL = {str(n) for n in range(0, 14)}  # stage numbers, counts of records and the like


def _parse(token):
    raw = token.replace('−', '-').replace(',', '.').replace('%', '').strip()
    try:
        return float(raw), len(raw.split('.')[1]) if '.' in raw else 0
    except ValueError:
        return None, 0


def _candidates(token):
    """What a number in the reply can stand for, at the precision it was written: 98.91% is 98.91 or 0.9891."""
    value, decimals = _parse(token)
    if value is None:
        return set()
    found = {round(value, decimals)}
    if '%' in token or value > 1:
        found.add(round(value / 100, decimals + 2))
    return found


def known_numbers(*texts):
    """Every number in the engine's tool results, the system context and the researcher's messages, rounded to every
    precision a reply might fairly use (0.9891 may be written 0.99, 0.989 or 98.9%)."""
    known = set()
    for text in texts:
        for token in NUMBER.findall(text or ''):
            value, _ = _parse(token)
            if value is None:
                continue
            for base in (value, value * 100, value / 100):
                known |= {round(base, k) for k in range(5)}
    return known


def check(reply, known):
    """Numbers in the reply that match nothing the engine or the researcher gave, and forbidden claim words."""
    unverified = []
    for token in NUMBER.findall(reply or ''):
        clean = token.strip()
        if clean.rstrip('%') in TRIVIAL or re.fullmatch(r'20\d\d', clean):
            continue
        if not (_candidates(clean) & known) and clean not in unverified:
            unverified.append(clean)
    claims = []
    for match in CLAIMS.finditer(reply or ''):
        if not NEGATION.search(reply[max(0, match.start() - 60):match.start()]) and match.group(0).lower() not in claims:
            claims.append(match.group(0).lower())
    return {'unverified_numbers': unverified[:12], 'claim_words': claims[:12]} if unverified or claims else None
