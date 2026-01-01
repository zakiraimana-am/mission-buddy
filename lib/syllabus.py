from __future__ import annotations
from pathlib import Path
import re
from typing import Dict, List, Tuple, Optional

CIV_CANDIDATES = {
    "MES": ["mesopotamia.md", "meso.md", "mesopotamia_syllabus.md"],
    "EGY": ["egypt.md", "mesir.md", "mesir_purba.md"],
    "IND": ["indus.md", "indus_valley.md", "lembah_indus.md"],
    "HHE": ["huang_he.md", "huanghe.md", "hwang_ho.md", "hwangho.md"],
}

CHUNK_RE = re.compile(r"^[\-\*\u2022]\s*\[(?P<id>[A-Za-z0-9]{2,8}\-[A-Za-z0-9]{2,8}\-\d{3})\]\s*(?P<rest>.*)$")

def discover_civ_file(civ_code: str, syllabus_dir: str) -> Optional[Path]:
    civ_code = civ_code.strip().upper()
    base = Path(syllabus_dir)

    for fname in CIV_CANDIDATES.get(civ_code, []):
        p = base / fname
        if p.exists():
            return p

    md_files = list(base.glob("*.md"))
    if not md_files:
        return None

    keywords = {
        "MES": ["meso", "mesopotamia", "sumer", "babylon"],
        "EGY": ["egypt", "mesir", "firaun", "nil"],
        "IND": ["indus", "harappa", "mohenjo", "lembah"],
        "HHE": ["huang", "huanghe", "hwang", "kuning", "yellow"],
    }.get(civ_code, [])

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
    return re.sub(r"\[\#.+?\]\s*", "", text).strip()

def load_civ_chunks(civ_code: str, syllabus_dir: str) -> Dict[str, str]:
    path = discover_civ_file(civ_code=civ_code, syllabus_dir=syllabus_dir)
    if not path or not path.exists():
        return {}

    raw_lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

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

    civ = civ_code.strip().upper()
    cleaned: List[str] = []
    for raw in raw_lines:
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith("---"):
            continue
        if line.lower().startswith("http"):
            continue
        if re.fullmatch(r"\d{1,4}", line):
            continue
        line = re.sub(r"^[\-\*\u2022]\s*", "", line).strip()
        line = _strip_tags(line)
        if line:
            cleaned.append(line)

    auto_chunks: Dict[str, str] = {}
    for idx, line in enumerate(cleaned, start=1):
        auto_chunks[f"{civ}-AUTO-{idx:03d}"] = line

    return auto_chunks

def _tokenize(s: str) -> List[str]:
    return re.findall(r"[A-Za-zÀ-ÿ0-9]+", (s or "").lower())

def retrieve_relevant_chunks(query: str, chunks: Dict[str, str], k: int = 12) -> List[Tuple[str, str]]:
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
        return [(cid, text) for _, cid, text in scored[:min(max(k, 20), len(scored))]]

    return [(cid, text) for _, cid, text in scored[:min(k, len(scored))]]

def list_md_files(syllabus_dir: str) -> List[str]:
    base = Path(syllabus_dir)
    return sorted([p.name for p in base.glob("*.md")])
