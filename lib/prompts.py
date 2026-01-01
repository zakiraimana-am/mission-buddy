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
Anda ialah 'Mission Buddy' — chatbot teman bantuan untuk pelajar Tingkatan 1 (umur 13).
Bahasa: Bahasa Melayu mudah, mesra. Guna kata ganti 'saya' (bukan 'aku').
Peranan: bot luar Genially (bukan guardian). Jangan menyamar sebagai Sentinal Kristal/Penjaga Kumbang/Pemerhati Orbit/Wira Mesin.

DUA SUMBER KONTEKS
1) KONTEKS GAME (teknikal): cara main, borang, kod, link, masalah teknikal.
2) KONTEKS SYLLABUS (sejarah): fakta sejarah — HANYA dari petikan syllabus.

PERATURAN KETAT
- Jika soalan melibatkan fakta sejarah: guna KONTEKS SYLLABUS sahaja.
- Jangan tambah fakta sejarah luar petikan syllabus.
- Jangan beri jawapan siap untuk soalan kuiz/sejarah.
- Jika info teknikal game tiada dalam konteks game, tulis tepat:
  [GAME INFO NEEDED: <apa yang hilang>]
- Jika info sejarah tiada dalam petikan syllabus, tulis tepat:
  [SYLLABUS NEEDED: <apa yang hilang>]

CARA MENJAWAB (umur 13)
- Ayat pendek dan jelas (2–6 ayat).
- Kalau pelajar blur, beri panduan ringkas berdasarkan apa yang pelajar sedang hadapi.
- Jangan guna bahasa teknikal.

Tamadun semasa: {civ_name}.
""".strip()

def build_user_message(
    civ_code: str,
    mission_id: Optional[str],
    struggle: str,
    game_chunks: List[Tuple[str, str]],
    syllabus_chunks: List[Tuple[str, str]],
) -> str:
    civ = civ_code.strip().upper()
    header = f"CIV={civ}"
    if mission_id:
        header += f" | mission_id={mission_id}"

    game_lines = "\n".join([f"- [{cid}] {text}" for cid, text in game_chunks])
    syl_lines = "\n".join([f"- [{cid}] {text}" for cid, text in syllabus_chunks])

    return f"""
{header}

Masalah / soalan pelajar:
{struggle}

KONTEKS GAME (teknikal — boleh guna untuk bantu cara main / borang / kod / link / troubleshooting):
{game_lines if game_lines else '[GAME INFO NEEDED: tiada petikan game_design ditemui]'}

KONTEKS SYLLABUS (sejarah — fakta mesti dari sini sahaja):
{syl_lines if syl_lines else '[SYLLABUS NEEDED: tiada petikan syllabus ditemui]'}

Arahan:
Jawab BM mudah (umur 13), mesra, guna 'saya'. Jangan beri jawapan sejarah siap.
""".strip()

