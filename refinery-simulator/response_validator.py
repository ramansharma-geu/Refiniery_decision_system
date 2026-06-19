import re

FORBIDDEN_PHRASES = [
    "the operational significance",
    "this suggests",
    "it is important to note",
    "based on available information",
    "further analysis may be required",
    "data unavailable",
    "cannot determine",
]

# These section headers should NOT appear in default responses
# They are only allowed when the user explicitly asks for them
FORBIDDEN_DEFAULT_SECTIONS = [
    "analysis:",
    "economic impact",
    "confidence level",
]


def check_forbidden(response: str):
    if not response:
        return False, ['empty_response']
    found = [p for p in FORBIDDEN_PHRASES if p in response.lower()]
    return (len(found) == 0), found


def check_forbidden_sections(response: str, allow_sections=None):
    """Check for forbidden default sections unless explicitly allowed."""
    if not response:
        return True, []
    allow = [s.lower() for s in (allow_sections or [])]
    found = []
    for s in FORBIDDEN_DEFAULT_SECTIONS:
        if s.lower() not in allow and s.lower() in response.lower():
            found.append(s)
    return (len(found) == 0), found


def check_length(response: str, max_words=120):
    wc = len(response.split())
    return wc <= max_words, wc


def has_required_sections(response: str, required_sections):
    # Simple header-based detection (exact match of section title or title with colon)
    lower = response.lower()
    missing = []
    for s in required_sections:
        key = s.lower()
        if key not in lower and (key + ':') not in lower and ('\n' + key) not in lower:
            missing.append(s)
    return len(missing) == 0, missing


def looks_like_bullets(response: str):
    # Detect bullets using common bullet markers
    return any(ch in response for ch in ['\u2022', '•', '-', '*'])


def validate_response(response: str, required_sections=None, max_words=120, allow_sections=None):
    ok_forbidden, found = check_forbidden(response)
    ok_length, wc = check_length(response, max_words=max_words)
    ok_sections = True
    missing = []
    if required_sections:
        ok_sections, missing = has_required_sections(response, required_sections)

    ok_bullets = looks_like_bullets(response)
    
    # Check for forbidden default sections
    ok_default_sections, found_defaults = check_forbidden_sections(response, allow_sections=allow_sections)

    passed = ok_forbidden and ok_length and ok_sections
    details = {
        'forbidden_ok': ok_forbidden,
        'forbidden_found': found,
        'word_count_ok': ok_length,
        'word_count': wc,
        'sections_ok': ok_sections,
        'sections_missing': missing,
        'bullets_present': ok_bullets,
        'default_sections_ok': ok_default_sections,
        'default_sections_found': found_defaults,
    }
    return passed, details
