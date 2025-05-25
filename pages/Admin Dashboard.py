import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="Admin Dashboard", layout="wide")
st.title("📊 Admin Dashboard – View Faculty Chat Logs")

# ========= Password Protection =========
with st.sidebar:
    st.markdown("### 🔐 Admin Access")
    password = st.text_input("Enter admin password:", type="password")
    if password != st.secrets.get("admin_dashboard_password"):
        st.warning("Enter the correct admin password to view logs.")
        st.stop()

# ========= Check if DB Exists =========
DB_PATH = "chat_log.db"

if not os.path.exists(DB_PATH):
    st.info("The chat log database has not been created yet.")
    st.stop()

# ========= Connect to DB and Try to Load Table =========
try:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    df = pd.read_sql("SELECT * FROM messages ORDER BY timestamp ASC", conn)
    conn.close()
except Exception as e:
    st.error("No chat data yet — the messages table may not exist.")
    st.stop()

# ========= Main UI =========
if df.empty:
    st.info("No chat logs found yet.")
    st.stop()

# Drop null/empty emails
df = df[df["email"].notnull() & (df["email"] != "")]

# Select user by email
user_emails = sorted(df["email"].unique())
selected_email = st.selectbox("Select a user by email:", user_emails)

# Filter to selected user
user_df = df[df["email"] == selected_email]

st.markdown(f"### 👤 Showing chat for: `{selected_email}`")
for _, row in user_df.iterrows():
    with st.chat_message(row["role"]):
        st.markdown(row["message"])
