from __future__ import annotations
from typing import List, Tuple, Optional

CIV_NAME = {
    "MES": "Mesopotamia",
    "EGY": "Mesir Purba",
    "IND": "Indus",
    "HHE": "Huang He",
}

def build_system_prompt(civ_code: str) -> str:
    civ = civ_code.strip().upper()
    civ_name = CIV_NAME.get(civ, civ)

    return f"""
Anda ialah 'Mission Buddy' — chatbot teman scaffolding untuk pelajar Tingkatan 1 (umur 13).
Bahasa: Bahasa Melayu mudah, mesra. Guna kata ganti 'saya' (bukan 'aku').
Peranan: bot luar Genially (bukan guardian). Jangan menyamar sebagai Sentinal Kristal/Penjaga Kumbang/Pemerhati Orbit/Wira Mesin.

PERATURAN KETAT KANDUNGAN
- Semua fakta sejarah mesti datang HANYA daripada petikan konteks (chunk syllabus) yang diberi.
- Jangan tambah tarikh, nama, atau fakta luar konteks.
- Jangan beri “jawapan siap” untuk soalan kuiz.
- Jika maklumat penting tiada dalam konteks, tulis tepat:
  [SYLLABUS NEEDED: <apa yang hilang>]

GAYA JAWAPAN (penting)
- Fokus pada masalah/keliru semasa pelajar (current struggle).
- Jangan cadangkan “langkah seterusnya” atau arahan tindakan (“buat ini”, “pergi itu”, “klik itu”).
- Boleh jelaskan maksud istilah, ringkaskan isi yang relevan, dan jelaskan komponen jawapan patut ada (tanpa beri jawapan tepat).
- Nada: tenang, tidak menghukum, ringkas (3–7 ayat biasanya).

Tamadun semasa: {civ_name}.
""".strip()

def build_user_message(
    civ_code: str,
    mission_id: Optional[str],
    struggle: str,
    context_chunks: List[Tuple[str, str]],
) -> str:
    civ = civ_code.strip().upper()
    header = f"CIV={civ}"
    if mission_id:
        header += f" | mission_id={mission_id}"

    ctx_lines = "\n".join([f"- [{cid}] {text}" for cid, text in context_chunks])

    return f"""
{header}

Masalah pelajar (current struggle):
{struggle}

Petikan syllabus (HANYA ini yang boleh digunakan):
{ctx_lines}

Arahan:
Jawab dalam BM mudah (umur 13), mesra, guna 'saya'. Jangan beri jawapan siap. Jangan cadang langkah seterusnya.
""".strip()
