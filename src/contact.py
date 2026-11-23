import re

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PROFESSOR_PATTERN = re.compile(r"\b(professor|instructor|lecturer|prof|dr|faculty)\b", re.IGNORECASE)
TA_PATTERN = re.compile(r"\b(teaching assistants?|tas?|readers?|tutors?|graders?)\b", re.IGNORECASE)


def find_professor_email(text):
    if not text:
        return None

    best_email = None
    best_score = None

    for position, match in enumerate(EMAIL_PATTERN.finditer(text)):
        email = match.group().rstrip(".")
        before = text[max(0, match.start() - 150):match.start()]

        score = -position
        if PROFESSOR_PATTERN.search(before):
            score += 100
        if TA_PATTERN.search(before[-60:]):
            score -= 200

        if best_score is None or score > best_score:
            best_email = email
            best_score = score

    return best_email
