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

# ========= Database Path and Refresh =========
DB_PATH = "chat_log.db"

if not os.path.exists(DB_PATH):
    st.info("The chat log database has not been created yet.")
    st.stop()

# ========= Load Logs (function) =========
@st.cache_data(show_spinner=False)
def load_logs():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    df = pd.read_sql("SELECT * FROM messages ORDER BY timestamp ASC", conn)
    conn.close()
    return df

# ========= Refresh Button =========
if st.button("🔁 Refresh Log View"):
    st.cache_data.clear()
    st.rerun()

df = load_logs()

if df.empty:
    st.info("No chat logs found yet.")
    st.stop()

df = df[df["email"].notnull() & (df["email"] != "")]

# ========= Delete User Interface =========
with st.expander("🗑️ Delete User Chat History", expanded=False):
    delete_emails = sorted(df["email"].unique())
    selected_delete_email = st.selectbox("Select a user to delete:", delete_emails, key="delete_user")
    if st.button("🚨 Delete This User's Chat History"):
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.execute("DELETE FROM messages WHERE email = ?", (selected_delete_email,))
        conn.commit()
        conn.close()
        st.success(f"Deleted all chat messages for `{selected_delete_email}`.")
        st.cache_data.clear()
        st.rerun()

# ========= Select and View User =========
user_emails = sorted(df["email"].unique())
selected_email = st.selectbox("📧 Select a user to view:", user_emails)
user_df = df[df["email"] == selected_email]

st.markdown(f"### 👤 Showing chat for: `{selected_email}`")
for _, row in user_df.iterrows():
    with st.chat_message(row["role"]):
        st.markdown(row["message"])

# ========= Download Button =========
st.divider()
csv = user_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download This User's Conversation as CSV",
    data=csv,
    file_name=f"{selected_email.replace('@','_')}_chatlog.csv",
    mime="text/csv"
)
