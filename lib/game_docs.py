from __future__ import annotations
from pathlib import Path
import re
from typing import Dict, List, Tuple

# Supports optional chunk IDs like:
# - [GD-001] ...
# - [GAME-001] ...
CHUNK_RE = re.compile(r"^[\-\*\u2022]\s*\[(?P<id>[A-Za-z0-9]{2,12}\-\d{3})\]\s*(?P<rest>.*)$")

def load_game_chunks(game_doc_path: str) -> Dict[str, str]:
    """
    Loads chunks from data/game_design.md.
    If no chunk IDs exist, auto-chunk each meaningful line into GD-AUTO-001...
    """
    p = Path(game_doc_path)
    if not p.exists():
        return {}

    raw_lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()

    chunks: Dict[str, str] = {}
    for raw in raw_lines:
        line = raw.strip()
        m = CHUNK_RE.match(line)
        if not m:
            continue
        cid = m.group("id").strip().upper()
        rest = m.group("rest").strip()
        if rest:
            chunks[cid] = rest

    if chunks:
        return chunks

    # auto-chunk fallback
    cleaned: List[str] = []
    for raw in raw_lines:
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith(">") or line.startswith("---"):
            continue
        line = re.sub(r"^[\-\*\u2022]\s*", "", line).strip()
        if line:
            cleaned.append(line)

    out: Dict[str, str] = {}
    for i, line in enumerate(cleaned, start=1):
        out[f"GD-AUTO-{i:03d}"] = line
    return out

def _tokenize(s: str) -> List[str]:
    return re.findall(r"[A-Za-zÀ-ÿ0-9]+", (s or "").lower())

def retrieve_relevant_game_chunks(query: str, chunks: Dict[str, str], k: int = 10) -> List[Tuple[str, str]]:
    q_tokens = set(_tokenize(query))
    scored = []
    for cid, text in chunks.items():
        t_tokens = set(_tokenize(text))
        score = len(q_tokens & t_tokens)
        if score == 0 and query and text:
            q = query.lower().replace(" ", "")
            t = text.lower().replace(" ", "")
            if q and q in t:
                score = 1
        if score > 0:
            scored.append((score, cid, text))

    scored.sort(reverse=True, key=lambda x: x[0])
    items = list(chunks.items())

    if not scored:
        return items[:min(k, len(items))]

    top_score = scored[0][0]
    if top_score <= 1:
        return [(cid, text) for _, cid, text in scored[:min(max(k, 18), len(scored))]]

    return [(cid, text) for _, cid, text in scored[:min(k, len(scored))]]
