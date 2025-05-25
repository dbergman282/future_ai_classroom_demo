import streamlit as st

st.set_page_config(page_title="UConn Syllabus Assistant", layout="wide")
st.title("📘 AI-Powered Syllabus Assistant for UConn School of Business")

from openai import OpenAI
import pandas as pd
import uuid
import sqlite3
from datetime import datetime

# ========== Secure Login ==========
def require_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.markdown("### 🔐 Secure Access")
        with st.form("password_form"):
            col1, _ = st.columns([1, 5])
            with col1:
                user_pw = st.text_input("Enter password to access the app:", type="password")
            submitted = st.form_submit_button("Go")

        if submitted:
            if user_pw == st.secrets.get("app_password"):
                st.session_state.logged_in = True
            else:
                st.markdown(
                    "<div style='background-color:#1E232A;padding:1rem;border-radius:0.5rem;color:#FF6666;'>⚠️ <strong>Invalid password.</strong></div>",
                    unsafe_allow_html=True
                )
                st.stop()
        else:
            st.stop()

# ========== Logging Helper ==========
def log_message(role, message):
    conn = sqlite3.connect("chat_log.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            session_id TEXT,
            name TEXT,
            email TEXT,
            role TEXT,
            message TEXT
        )
    """)
    cursor.execute("""
        INSERT INTO messages (timestamp, session_id, name, email, role, message)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        st.session_state.session_id,
        st.session_state.user_name,
        st.session_state.user_email,
        role,
        message
    ))
    conn.commit()
    conn.close()

# ========== Main App ==========
def run_app_ui():


    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""
    if "info_submitted" not in st.session_state:
        st.session_state.info_submitted = False

    if not st.session_state.info_submitted:
        with st.form(key="user_info_form"):
            st.session_state.user_name = st.text_input("Your name")
            st.session_state.user_email = st.text_input("Your UConn email")
            submit = st.form_submit_button("Start Building My Syllabus")

            if submit and st.session_state.user_name and st.session_state.user_email:
                st.session_state.info_submitted = True
                st.session_state.messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are an AI assistant helping UConn School of Business faculty create a syllabus. "
                            "Ask questions step-by-step to collect: course title, level, goals, grading, schedule, and policies. "
                            "Be conversational and helpful. Ask follow-up questions if answers are vague or incomplete. "
                            "Encourage inclusion of compliance, sexual harassment, ADA, and academic integrity policies."
                        )
                    }
                ]
                st.rerun()

    if st.session_state.info_submitted:
        st.markdown(f"**Welcome, {st.session_state.user_name}!** Let's build your syllabus.")

        for msg in st.session_state.messages:
            if msg["role"] != "system":
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        user_input = st.chat_input("Ask or answer something to get started...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            log_message("user", user_input)

            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                response = client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=st.session_state.messages,
                    temperature=0.5
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                log_message("assistant", reply)

        st.divider()


# ========== Entry Point ==========
def main():
    require_login()
    run_app_ui()

if __name__ == "__main__":
    main()
