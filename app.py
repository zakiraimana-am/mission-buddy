import os
import streamlit as st
from dotenv import load_dotenv

from lib.syllabus import load_civ_chunks, retrieve_relevant_chunks, discover_civ_file, list_md_files
from lib.game_docs import load_game_chunks, retrieve_relevant_game_chunks
from lib.text_utils import keyword_list, normalize_topic, jaccard
from lib.prompts import build_system_prompt, build_user_message
from lib.openai_api import chat_completion

st.set_page_config(page_title="Mission Buddy", layout="centered")
load_dotenv()

# Always readable in light/dark
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
GAME_DOC_PATH = "data/game_design.md"
ALLOWED = ["MES", "EGY", "IND", "HHE"]
CIV_LOCKED = os.getenv("CIV_LOCKED", "").strip().upper()

if not os.getenv("OPENAI_API_KEY", "").strip():
    st.warning("OPENAI_API_KEY belum diset. Set dulu sebelum chat.")
    st.stop()

# Load game design reference (technical)
game_chunks_all = load_game_chunks(GAME_DOC_PATH)
if not game_chunks_all:
    st.error("Fail rujukan game tidak ditemui: data/game_design.md (pastikan commit & deploy).")
    st.stop()

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "topic_attempts" not in st.session_state:
    st.session_state.topic_attempts = {}   # topic_key -> attempts
if "topic_tokens" not in st.session_state:
    st.session_state.topic_tokens = {}     # topic_key -> token set

def is_game_question(text: str) -> bool:
    t = (text or "").lower()
    keywords = [
        "genially", "google form", "borang", "kod", "unlock", "pautan", "link",
        "mission", "misi", "guardian", "pintu", "loading", "tak boleh buka"
    ]
    return any(k in t for k in keywords)

def match_existing_topic(new_tokens):
    best_key = None
    best_score = 0.0
    for k, toks in st.session_state.topic_tokens.items():
        score = jaccard(new_tokens, toks)
        if score > best_score:
            best_score = score
            best_key = k
    return best_key, best_score

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

    # Optional manual bump (teacher use)
    if st.button("Tambah hint (manual)"):
        st.session_state.topic_attempts["_manual"] = st.session_state.topic_attempts.get("_manual", 0) + 1

    if st.button("Reset chat"):
        st.session_state.messages = []
        st.session_state.topic_attempts = {}
        st.session_state.topic_tokens = {}
        st.rerun()

# Load syllabus chunks for selected civ
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

st.title("Mission Buddy")
st.caption("Companion chat untuk Eksplorasi Digital")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_text = st.chat_input("Tulis soalan atau masalah anda…")
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    game_q = is_game_question(user_text)
    mode = "GAME" if game_q else "SEJARAH"

    # Decide hint_level
    if game_q:
        hint_level = 3
        topic_key = "GAME"
    else:
        new_tokens = normalize_topic(user_text, keep=10)
        matched_key, score = match_existing_topic(new_tokens)

        if matched_key and score >= 0.55:
            topic_key = matched_key
        else:
            topic_key = " ".join(sorted(new_tokens)) or f"topic_{len(st.session_state.topic_tokens)+1}"
            st.session_state.topic_tokens[topic_key] = new_tokens

        st.session_state.topic_attempts[topic_key] = st.session_state.topic_attempts.get(topic_key, 0) + 1
        hint_level = min(3, st.session_state.topic_attempts[topic_key] + st.session_state.topic_attempts.get("_manual", 0))

    # Retrieve relevant contexts
    top_game = retrieve_relevant_game_chunks(user_text, game_chunks_all, k=10)
    top_syl = retrieve_relevant_chunks(user_text, chunks, k=10)

    # IMPORTANT: syllabus context = keywords only, and fewer keywords at low hint levels
    max_kw = 2 if hint_level == 1 else (5 if hint_level == 2 else 8)

    syllabus_lines = []
    for cid, text in top_syl:
        kws = keyword_list(text, max_n=max_kw)
        syllabus_lines.append(f"- [{cid}] kata kunci: " + (", ".join(kws) if kws else "(tiada)"))

    # Game context can be short excerpts
    game_lines = []
    for cid, text in top_game:
        short = (text[:140] + "…") if len(text) > 140 else text
        game_lines.append(f"- [{cid}] {short}")

    if debug:
        f = discover_civ_file(civ, SYLLABUS_DIR)
        st.info(f"MODE={mode} | hint_level={hint_level} | topic='{topic_key}'")
        st.caption(f"Syllabus file: {f.name if f else '—'} | syllabus_chunks={len(chunks)} | game_chunks={len(game_chunks_all)}")

    system_prompt = build_system_prompt(civ_code=civ)
    user_msg = build_user_message(
        civ_code=civ,
        mission_id=mission_id.strip() or None,
        user_text=user_text,
        hint_level=hint_level,
        mode=mode,
        game_context_lines=game_lines,
        syllabus_context_lines=syllabus_lines,
    )

    messages = [{"role": "system", "content": system_prompt}]
    for h in st.session_state.messages[-10:]:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": user_msg})

    with st.chat_message("assistant"):
        with st.spinner("Saya sedang jawab…"):
            reply = chat_completion(model=model, messages=messages, temperature=0.5, max_tokens=600)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
