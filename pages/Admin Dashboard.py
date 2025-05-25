import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Admin Dashboard", layout="wide")
st.title("📊 Admin Dashboard – View Faculty Chat Logs")

# Connect to database
conn = sqlite3.connect("chat_log.db", check_same_thread=False)
df = pd.read_sql("SELECT * FROM messages ORDER BY timestamp ASC", conn)
conn.close()

if df.empty:
    st.info("No chat logs found yet.")
    st.stop()

# Drop null/empty emails just in case
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
