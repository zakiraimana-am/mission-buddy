from __future__ import annotations
import re
from collections import Counter
from typing import List, Set

STOPWORDS = set([
    # Malay
    "yang","dan","atau","dalam","di","ke","dari","pada","untuk","dengan","ini","itu","oleh","sebagai",
    "ialah","adalah","akan","sudah","tidak","tak","bukan","saya","awak","anda","kami","kita","mereka",
    "apa","siapa","bila","mana","mengapa","kenapa","bagaimana","sila","tolong",
    # English
    "the","a","an","and","or","in","on","to","from","of","for","with","is","are","was","were","be","been",
])

def tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-zÀ-ÿ0-9]+", (text or "").lower())

def keyword_list(text: str, max_n: int = 8) -> List[str]:
    toks = [t for t in tokenize(text) if len(t) >= 3 and t not in STOPWORDS]
    if not toks:
        return []
    cnt = Counter(toks)
    items = sorted(cnt.items(), key=lambda x: (-x[1], x[0]))
    return [w for w,_ in items[:max_n]]

def normalize_topic(text: str, keep: int = 10) -> Set[str]:
    toks = [t for t in tokenize(text) if len(t) >= 3 and t not in STOPWORDS]
    if not toks:
        return set()
    cnt = Counter(toks)
    items = sorted(cnt.items(), key=lambda x: (-x[1], x[0]))
    return set([w for w,_ in items[:keep]])

def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0
