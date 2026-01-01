# Mission Buddy (Streamlit) — Chat Only (V2)

Versi ini lebih robust:
- Auto-detect fail .md untuk 4 tamadun (termasuk variasi nama fail seperti `huanghe.md`).
- Jika tiada chunk ID ditemui dalam fail, ia auto-chunk (AUTO-001...) supaya bot masih boleh jawab.

## Letak fail syllabus
Letakkan 4 fail .md dalam folder `data/syllabus/` (nama boleh fleksibel, tapi disyorkan):
- mesopotamia.md
- egypt.md
- indus.md
- huang_he.md

Format terbaik (dengan chunk ID):
- [EGY-LOC-001] [#lokasi] Tamadun Mesir Purba terletak di lembah Sungai Nil.

## Run local (Windows) — tanpa activate
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:OPENAI_API_KEY="sk-..."
.\.venv\Scripts\python.exe -m streamlit run app.py
