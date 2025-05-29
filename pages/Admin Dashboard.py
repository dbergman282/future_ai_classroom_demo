import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# ========= Page Setup =========
st.set_page_config(page_title="Admin Dashboard", layout="wide")
st.title("📊 Admin Dashboard – View Faculty Chat Logs")

# ========= Password Protection =========
with st.sidebar:
    st.markdown("### 🔐 Admin Access")
    password = st.text_input("Enter admin password:", type="password")
    if password != st.secrets.get("admin_dashboard_password"):
        st.warning("Enter the correct admin password to view logs.")
        st.stop()

# ========= Supabase Setup =========
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# ========= Load Logs =========
@st.cache_data(show_spinner=False)
def load_logs():
    response = supabase.table("records_demo").select("*").order("timestamp", desc=False).execute()
    data = response.data
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    return df

# ========= Refresh Button =========
if st.button("🔁 Refresh Log View"):
    st.cache_data.clear()
    st.rerun()

df = load_logs()

if df.empty:
    st.info("No chat logs found yet.")
    st.stop()

# Filter out entries with no email
df = df[df["email"].notnull() & (df["email"] != "")]

# ========= Delete User Interface =========
with st.expander("🗑️ Delete User Chat History", expanded=False):
    delete_emails = sorted(df["email"].unique())
    selected_delete_email = st.selectbox("Select a user to delete:", delete_emails, key="delete_user")
    if st.button("🚨 Delete This User's Chat History"):
        # Delete all rows where email matches
        supabase.table("records_demo").delete().eq("email", selected_delete_email).execute()
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

# ========= Download This User =========
st.divider()
csv = user_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download This User's Conversation as CSV",
    data=csv,
    file_name=f"{selected_email.replace('@','_')}_chatlog.csv",
    mime="text/csv"
)

# ========= Download All Users =========
st.divider()
csv_all = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📦 Download ALL Conversations (All Users)",
    data=csv_all,
    file_name="all_chat_logs.csv",
    mime="text/csv"
)
