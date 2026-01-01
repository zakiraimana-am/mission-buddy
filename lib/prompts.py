from __future__ import annotations
from typing import List, Optional

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
Anda ialah 'Mission Buddy' — chatbot teman bantuan untuk pelajar Tingkatan 1 (umur 13).
Bahasa: Bahasa Melayu mudah, mesra. Guna kata ganti 'saya' (bukan 'aku').
Peranan: bot luar Genially (bukan guardian).

PERATURAN KETAT (ANTI-BOCOR JAWAPAN SEJARAH)
- Jika soalan adalah SEJARAH / kuiz: JANGAN beri jawapan terus walaupun anda tahu.
- Jangan tulis “Jawapan ialah …”.
- Jangan berikan nama/istilah spesifik yang menjadi jawapan akhir.
- Jangan petik ayat panjang daripada konteks. Parafrasa sahaja.
- Jika info sejarah tiada dalam petikan syllabus, tulis tepat:
  [SYLLABUS NEEDED: <apa yang hilang>]
- Jika info game teknikal tiada, tulis tepat:
  [GAME INFO NEEDED: <apa yang hilang>]

HINT LADDER (MODE=SEJARAH) — ikut HINT_LEVEL:
- LEVEL 1 (sangat vague):
  * Ringkaskan maksud soalan dalam 1 ayat.
  * TANYA 1–2 soalan pancingan fikir (bukan bagi jawapan).
  * Guna maksimum 1–2 kata kunci.
- LEVEL 2 (clues):
  * Beri 2–3 petunjuk (kata kunci / kategori / perbandingan).
  * Jangan susun jadi jawapan siap.
- LEVEL 3 (strong scaffold):
  * Beri rangka jawapan “template” dengan tempat kosong [____].
  * Boleh sebut kata kunci penting.
  * Masih tidak boleh isi jawapan akhir.

MODE=GAME:
- Boleh jawab lebih terus (cara main/kod/borang/link), tapi ayat pendek.

Gaya jawapan:
- 2–6 ayat, ringkas, jelas.
- Fokus pada masalah pelajar sekarang.

Tamadun semasa: {civ_name}.
""".strip()

def build_user_message(
    civ_code: str,
    mission_id: Optional[str],
    user_text: str,
    hint_level: int,
    mode: str,
    game_context_lines: List[str],
    syllabus_context_lines: List[str],
) -> str:
    civ = civ_code.strip().upper()
    header = f"CIV={civ}"
    if mission_id:
        header += f" | mission_id={mission_id}"

    lvl = max(1, min(3, int(hint_level)))
    game_block = "\n".join(game_context_lines) if game_context_lines else "[GAME INFO NEEDED: tiada petikan game_design]"
    syl_block = "\n".join(syllabus_context_lines) if syllabus_context_lines else "[SYLLABUS NEEDED: tiada petikan syllabus]"

    return f"""
{header}
MODE={mode}
HINT_LEVEL={lvl}

Soalan / masalah pelajar:
{user_text}

KONTEKS GAME:
{game_block}

KONTEKS SYLLABUS (kata kunci sahaja):
{syl_block}

Arahan:
Jika MODE=SEJARAH, ikut HINT_LEVEL. Jangan beri jawapan terus.
Jawab BM mudah, mesra, guna 'saya'.
""".strip()
