import sqlite3
import uuid
import requests
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="MindMate AI", page_icon="💬", layout="wide")

MODEL = "qwen2.5:3b"
OLLAMA_URL = "http://localhost:11434"
DB = Path(__file__).with_name("mindmate.db")

# Database
def connect():
    return sqlite3.connect(DB)


def setup_db():
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                title TEXT
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT,
                role TEXT,
                content TEXT
            )
        """)

def new_chat():
    chat_id = str(uuid.uuid4())
    with connect() as con:
        con.execute("INSERT INTO chats VALUES (?, ?)", (chat_id, "New chat"))
    return chat_id

def get_chats():
    with connect() as con:
        return con.execute("SELECT id, title FROM chats ORDER BY rowid DESC").fetchall()

def get_messages(chat_id):
    with connect() as con:
        rows = con.execute(
            "SELECT role, content FROM messages WHERE chat_id=? ORDER BY id",
            (chat_id,)
        ).fetchall()
    return [{"role": r, "content": c} for r, c in rows]

def save_message(chat_id, role, content):
    with connect() as con:
        con.execute(
            "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
            (chat_id, role, content)
        )

def delete_chat(chat_id):
    with connect() as con:
        con.execute("DELETE FROM messages WHERE chat_id=?", (chat_id,))
        con.execute("DELETE FROM chats WHERE id=?", (chat_id,))

# Ollama
def ask_ai(messages):
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={"model": MODEL, "messages": messages, "stream": False},
        timeout=180
    )
    response.raise_for_status()
    return response.json()["message"]["content"]

def ollama_ready():
    try:
        return requests.get(f"{OLLAMA_URL}/api/tags", timeout=3).ok
    except requests.RequestException:
        return False


setup_db()

if "chat_id" not in st.session_state:
    st.session_state.chat_id = new_chat()
# Sidebar
with st.sidebar:
    st.title("MindMate AI")

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.chat_id = new_chat()
        st.rerun()

    chats = get_chats()
    chat_ids = [c[0] for c in chats]
    titles = {c[0]: c[1] for c in chats}

    if st.session_state.chat_id not in chat_ids:
        st.session_state.chat_id = new_chat()
        st.rerun()

    selected = st.selectbox(
        "Previous Chats",
        chat_ids,
        index=chat_ids.index(st.session_state.chat_id),
        format_func=lambda x: titles[x]
    )

    if selected != st.session_state.chat_id:
        st.session_state.chat_id = selected
        st.rerun()

    if st.button("Delete Current Chat", use_container_width=True):
        delete_chat(st.session_state.chat_id)
        st.session_state.chat_id = new_chat()
        st.rerun()

    st.divider()
    st.caption(f"Model: {MODEL}")
    st.caption("Storage: SQLite")

# Main page
st.title("MindMate AI Assistant")
st.write("Ask questions and explore ideas with your personal AI assistant.")

if ollama_ready():
    st.success("Ollama is connected")
else:
    st.error("Ollama is not running. Start Ollama before chatting.")

st.divider()

messages = get_messages(st.session_state.chat_id)

if not messages:
    st.subheader("Start a conversation")
    st.write("You can ask questions, learn concepts, or get programming help.")

for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Type your message...")

if prompt:
    chat_id = st.session_state.chat_id
    save_message(chat_id, "user", prompt)

    with connect() as con:
        row = con.execute("SELECT title FROM chats WHERE id=?", (chat_id,)).fetchone()
        if row and row[0] == "New chat":
            con.execute(
                "UPDATE chats SET title=? WHERE id=?",
                (prompt[:35], chat_id)
            )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            history = get_messages(chat_id)[-12:]
            answer = ask_ai([
                {"role": "system", "content": "You are MindMate, a helpful AI assistant. Give clear and simple answers."},
                *history
            ])
            st.markdown(answer)
            save_message(chat_id, "assistant", answer)

        except requests.RequestException as error:
            st.error(f"Could not connect to Ollama: {error}")

    st.rerun()
