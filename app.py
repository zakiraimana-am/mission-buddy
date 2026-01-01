import os
import streamlit as st
from dotenv import load_dotenv

from lib.syllabus import load_civ_chunks, retrieve_relevant_chunks, discover_civ_file, list_md_files
from lib.prompts import build_system_prompt, build_user_message
from lib.openai_api import chat_completion

st.set_page_config(page_title="Mission Buddy", layout="centered")
load_dotenv()

st.markdown("""
<style>
.block-container { padding-top: 1.0rem; padding-bottom: 2rem; max-width: 760px; }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

:root { --mb-text: #111111; }
@media (prefers-color-scheme: dark) { :root { --mb-text: #F3F4F6; } }

div[data-testid="stChatMessage"] p,
div[data-testid="stChatMessage"] li,
div[data-testid="stChatMessage"] span,
div[data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] {
  color: var(--mb-text) !important;
}
div[data-testid="stChatMessage"] a {
  color: var(--mb-text) !important;
  text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

SYLLABUS_DIR = "data/syllabus"
ALLOWED = ["MES", "EGY", "IND", "HHE"]
CIV_LOCKED = os.getenv("CIV_LOCKED", "").strip().upper()

api_key = os.getenv("OPENAI_API_KEY", "")
if not api_key:
    st.warning("OPENAI_API_KEY belum diset. Set dulu sebelum chat.")
    st.stop()

with st.sidebar:
    st.markdown("### Tetapan")
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-4.1"], index=0)

    if CIV_LOCKED in ALLOWED:
        civ = CIV_LOCKED
        st.markdown(f"**Tamadun:** {civ} (locked)")
    else:
        civ = st.selectbox("Tamadun", ALLOWED, index=1)

    mission_id = st.text_input("mission_id (optional)", value="", placeholder="contoh: EGY-A-001")
    debug = st.toggle("Debug", value=False)
    if st.button("Reset chat"):
        st.session_state.messages = []
        st.rerun()

chunks = load_civ_chunks(civ_code=civ, syllabus_dir=SYLLABUS_DIR)
if not chunks:
    files = list_md_files(SYLLABUS_DIR)
    st.error(
        "Saya tak jumpa content syllabus untuk tamadun ini.\n\n"
        f"- CIV: {civ}\n"
        f"- Fail .md dijumpai: {files if files else 'TIADA'}\n\n"
        "✅ Pastikan 4 fail .md berada dalam `data/syllabus/`.\n"
        "Nama disyorkan: mesopotamia.md, egypt.md, indus.md, huang_he.md"
    )
    st.stop()

if debug:
    f = discover_civ_file(civ, SYLLABUS_DIR)
    st.info(f"Loaded {len(chunks)} chunks untuk {civ}. Contoh ID: {list(chunks.keys())[:5]}")
    st.caption(f"Fail digunakan: {f.name if f else '—'}")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Mission Buddy")
st.caption("Companion chat untuk Eksplorasi Digital.")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_text = st.chat_input("Tulis masalah anda di sini… (contoh: “Saya keliru maksud soalan ini…”)")
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    top_chunks = retrieve_relevant_chunks(user_text, chunks, k=12)
    system_prompt = build_system_prompt(civ_code=civ)
    user_msg = build_user_message(
        civ_code=civ,
        mission_id=mission_id.strip() or None,
        struggle=user_text,
        context_chunks=top_chunks,
    )

    messages = [{"role": "system", "content": system_prompt}]
    history = st.session_state.messages[-12:]
    for h in history:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": user_msg})

    with st.chat_message("assistant"):
        with st.spinner("Saya sedang jawab…"):
            reply = chat_completion(model=model, messages=messages, temperature=0.4, max_tokens=550)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
