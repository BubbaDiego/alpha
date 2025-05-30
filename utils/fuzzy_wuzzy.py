import re
from enum import Enum
from typing import Optional, Type, List, Dict, Any
try:
    from rapidfuzz import process, fuzz  # type: ignore
except Exception:  # pragma: no cover - fallback for minimal env
    # Very small fallback implementations using difflib so tests can run
    from difflib import SequenceMatcher

    def _ratio(a: str, b: str) -> int:
        return int(SequenceMatcher(None, a, b).ratio() * 100)

    class _Fuzz:
        @staticmethod
        def partial_ratio(a: str, b: str) -> int:
            return _ratio(a, b)

        @staticmethod
        def token_set_ratio(a: str, b: str) -> int:
            return _ratio(" ".join(sorted(a.split())), " ".join(sorted(b.split())))

        @staticmethod
        def partial_token_ratio(a: str, b: str) -> int:
            return _ratio(a, b)

    class _Process:
        @staticmethod
        def extractOne(query: str, choices: List[str], scorer=_Fuzz.partial_token_ratio):
            best_choice = None
            best_score = -1
            for choice in choices:
                score = scorer(query, choice)
                if score > best_score:
                    best_score = score
                    best_choice = choice
            return best_choice, best_score, None

    fuzz = _Fuzz()
    process = _Process()

# 🔕 Toggle to disable console output
FUZZY_LOGGING_ENABLED = False


def normalize(text: str) -> str:
    return re.sub(r'[\W_]+', '', text.lower())


def hybrid_score(a: str, b: str) -> int:
    return max(
        fuzz.partial_ratio(a, b),
        fuzz.token_set_ratio(a, b)
    )


def scrub_mask(input_str: str, mask_key: str) -> str:
    """Keep only characters from input_str that appear in mask_key."""
    allowed = set(mask_key)
    return ''.join(c for c in input_str if c in allowed)


def fuzzy_match_key(
    input_str: str,
    target_dict: Dict[str, Any],
    aliases: Optional[Dict[str, List[str]]] = None,
    threshold: float = 70.0
) -> Optional[str]:
    norm_input = normalize(input_str)
    keys = list(target_dict.keys())
    candidate_list = keys[:]

    alias_map = {}
    if aliases:
        for k, v_list in aliases.items():
            for alias in v_list:
                candidate_list.append(alias)
                alias_map[alias] = k

    best_match = None
    best_score = 0

    for candidate in candidate_list:
        scrubbed = scrub_mask(norm_input, candidate)
        score = fuzz.partial_token_ratio(scrubbed, candidate)

        if score > best_score:
            best_match = candidate
            best_score = score

    if best_match is None:
        if FUZZY_LOGGING_ENABLED:
            print(f"🐻 [FUZZY] No match found for '{input_str}'")
        return None

    if FUZZY_LOGGING_ENABLED:
        print(f"🐻 [FUZZY KEY MATCH] '{input_str}' → '{best_match}' ({best_score}%)")

    if best_score < threshold:
        if FUZZY_LOGGING_ENABLED:
            print(f"⚠️  Low confidence key match for '{input_str}' → {best_score}%")
        return None

    return alias_map.get(best_match, best_match)


def fuzzy_match_enum(
    input_str: str,
    enum_class: Type[Enum],
    aliases: Optional[Dict[str, List[str]]] = None,
    threshold: float = 60.0
) -> Optional[Enum]:
    norm_input = normalize(input_str)
    enum_names = [e.name for e in enum_class]
    candidate_list = enum_names[:]

    alias_map = {}
    if aliases:
        for k, v_list in aliases.items():
            for alias in v_list:
                candidate_list.append(alias)
                alias_map[alias] = k

    best_match, score, _ = process.extractOne(norm_input, candidate_list, scorer=fuzz.partial_token_ratio)

    #FUZZY_LOGGING_ENABLED = False

    if FUZZY_LOGGING_ENABLED:
        print(f"🐻 [FUZZY ENUM MATCH] '{input_str}' → '{best_match}' ({score}%)")

    if score < threshold:
        if FUZZY_LOGGING_ENABLED:
            print(f"⚠️  Low confidence match for '{input_str}' → {score}%")
        return None

    resolved = alias_map.get(best_match, best_match)
    try:
        return enum_class[resolved]
    except KeyError:
        if FUZZY_LOGGING_ENABLED:
           print(f"❌ Resolved match '{resolved}' not in enum {enum_class.__name__}")
        return None
