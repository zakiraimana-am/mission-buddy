from __future__ import annotations
from pathlib import Path
import re
from typing import Dict, List, Tuple, Optional

# Candidate filenames per civ (we try these in order)
CIV_CANDIDATES = {
    "MES": ["mesopotamia.md", "mesopotamia_syllabus.md", "meso.md", "mesopotamia_bab5.md"],
    "EGY": ["egypt.md", "mesir.md", "mesir_purba.md", "egypt_bab5.md"],
    "IND": ["indus.md", "indus_valley.md", "lembah_indus.md", "indus_bab5.md"],
    "HHE": ["huang_he.md", "huanghe.md", "hwang_ho.md", "hwangho.md", "huang_he_hwang_ho.md"],
}

# Accept common bullet markers: -, *, •
CHUNK_RE = re.compile(r"^[\-\*\u2022]\s*\[(?P<id>[A-Za-z0-9]{2,8}\-[A-Za-z0-9]{2,8}\-\d{3})\]\s*(?P<rest>.*)$")

def discover_civ_file(civ_code: str, syllabus_dir: str) -> Optional[Path]:
    """
    Find the best matching .md file for a civ_code using candidate names,
    then fallback to fuzzy scanning in directory.
    """
    civ_code = civ_code.strip().upper()
    base = Path(syllabus_dir)

    # 1) direct candidate names
    for fname in CIV_CANDIDATES.get(civ_code, []):
        p = base / fname
        if p.exists():
            return p

    # 2) fallback: scan directory and match keywords
    md_files = list(base.glob("*.md"))
    if not md_files:
        return None

    keywords = {
        "MES": ["meso", "mesopotamia", "sumer", "babylon"],
        "EGY": ["egypt", "mesir", "firaun", "nil"],
        "IND": ["indus", "harappa", "mohenjo", "lembah"],
        "HHE": ["huang", "huanghe", "hwang", "ho", "kuning", "yellow"],
    }.get(civ_code, [])

    # score by keyword hits in filename
    best = None
    best_score = 0
    for f in md_files:
        name = f.name.lower()
        score = sum(1 for k in keywords if k in name)
        if score > best_score:
            best_score = score
            best = f

    return best

def _strip_tags(text: str) -> str:
    # Remove tag markers like [#lokasi]
    return re.sub(r"\[\#.+?\]\s*", "", text).strip()

def load_civ_chunks(civ_code: str, syllabus_dir: str) -> Dict[str, str]:
    """
    Loads chunks from civ markdown.
    Preferred format per line:
      - [EGY-LOC-001] [#lokasi] ...
    If no chunk IDs are found, auto-chunk into:
      CIV-AUTO-001, CIV-AUTO-002, ...
    Returns: dict {chunk_id: chunk_text}
    """
    path = discover_civ_file(civ_code=civ_code, syllabus_dir=syllabus_dir)
    if not path or not path.exists():
        return {}

    raw_lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

    # Pass 1: parse explicit chunk IDs
    chunks: Dict[str, str] = {}
    for raw in raw_lines:
        line = raw.strip()
        m = CHUNK_RE.match(line)
        if not m:
            continue
        chunk_id = m.group("id").strip().upper()
        rest = _strip_tags(m.group("rest"))
        if rest:
            chunks[chunk_id] = rest

    if chunks:
        return chunks

    # Pass 2: auto-chunk fallback
    # Collect meaningful lines (ignore headings that are empty, images, page numbers, etc.)
    civ = civ_code.strip().upper()
    cleaned: List[str] = []
    for raw in raw_lines:
        line = raw.strip()
        if not line:
            continue
        # ignore markdown headings / separators
        if line.startswith("#") or line.startswith("---"):
            continue
        # ignore obvious page markers / urls
        if line.lower().startswith("http"):
            continue
        if re.fullmatch(r"\d{1,4}", line):
            continue
        # remove leading bullets
        line = re.sub(r"^[\-\*\u2022]\s*", "", line).strip()
        line = _strip_tags(line)
        if line:
            cleaned.append(line)

    auto_chunks: Dict[str, str] = {}
    idx = 1
    for line in cleaned:
        cid = f"{civ}-AUTO-{idx:03d}"
        auto_chunks[cid] = line
        idx += 1

    return auto_chunks

def _tokenize(s: str) -> List[str]:
    return re.findall(r"[A-Za-zÀ-ÿ0-9]+", (s or "").lower())

def retrieve_relevant_chunks(query: str, chunks: Dict[str, str], k: int = 12) -> List[Tuple[str, str]]:
    """
    Keyword overlap retrieval (no embeddings).
    More robust: if weak match, return a broader slice so bot can still answer.
    """
    q_tokens = set(_tokenize(query))
    scored = []
    for cid, text in chunks.items():
        t_tokens = set(_tokenize(text))
        # overlap score
        score = len(q_tokens & t_tokens)
        # small bonus for partial substring matches (handles 'huanghe' vs 'huang he')
        if score == 0 and query and text:
            q = (query or "").lower().replace(" ", "")
            t = (text or "").lower().replace(" ", "")
            if q and q in t:
                score = 1
        if score > 0:
            scored.append((score, cid, text))

    scored.sort(reverse=True, key=lambda x: x[0])

    items = list(chunks.items())
    if not scored:
        # if nothing matches, return first k (or all if small)
        return items[:min(k, len(items))]

    # If top score is low, broaden context
    top_score = scored[0][0]
    if top_score <= 1:
        return [(cid, text) for _, cid, text in scored[:min(max(k, 20), len(scored))]]

    return [(cid, text) for _, cid, text in scored[:min(k, len(scored))]]

def available_civs(syllabus_dir: str) -> Dict[str, Path]:
    """
    Returns civ_code -> detected file path for civs that exist.
    """
    out: Dict[str, Path] = {}
    for civ in ["MES", "EGY", "IND", "HHE"]:
        p = discover_civ_file(civ, syllabus_dir)
        if p and p.exists():
            out[civ] = p
    return out
