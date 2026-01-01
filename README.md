# Mission Buddy — 4 Civilization Deploy (Render Blueprint)

Repo ini deploy **4 URL** (MES/EGY/IND/HHE) daripada **1 codebase** menggunakan `render.yaml`.

## 1) Letak fail syllabus
Letak 4 fail `.md` dalam `data/syllabus/` (nama disyorkan):
- `mesopotamia.md`
- `egypt.md`
- `indus.md`
- `huang_he.md`

✅ Best format (dengan chunk ID):
- [EGY-LOC-001] [#lokasi] ...

Kalau fail anda tak ada chunk ID, sistem akan auto-chunk (CIV-AUTO-001...) supaya bot masih boleh jawab.

## 2) Run local (Windows) — tanpa activate venv
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:OPENAI_API_KEY="sk-..."
.\.venv\Scripts\python.exe -m streamlit run app.py

Optional (kunci civ masa local):
$env:CIV_LOCKED="MES"   # atau EGY/IND/HHE

## 3) Deploy Render (Blueprint)
1. Push repo ke GitHub
2. Render → New → Blueprint → pilih repo
3. Render akan create 4 services (mission-buddy-mes/egy/ind/hhe)
4. Untuk setiap service, set `OPENAI_API_KEY` di Environment
