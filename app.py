"""Clario - Streamlit frontend for the Azure OpenAI chatbot."""

import streamlit as st
from openai import (
    APIConnectionError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
)

from chatbot import ConfigError, DEFAULT_SYSTEM_PROMPT, get_config, stream_reply

st.set_page_config(page_title="Clario AI Assistant", page_icon="✨", layout="centered")
# ---------- Visual styling ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    :root { --ink:#202536; --muted:#737b8d; --violet:#167c75; --violet-dark:#0f625d; --line:#e9eaf2; }
    .stApp {
        background: radial-gradient(ellipse at 50% -18%, rgba(52,166,150,.16), transparent 45%),
                    linear-gradient(180deg,#f5fbfa 0%,#f4f8f8 46%,#f7faf9 100%);
        color:var(--ink); font-family:'DM Sans',sans-serif;
    }
    [data-testid="stHeader"] { background:transparent; }
    [data-testid="stMainBlockContainer"] { max-width:850px; padding-top:3rem; }
    h1,h2,h3 { font-family:'Manrope',sans-serif!important; color:var(--ink); letter-spacing:-.04em; }
    h1 { font-weight:800!important; font-size:2.65rem!important; }
    [data-testid="stAppViewContainer"]>.main p { color:var(--muted); }
    [data-testid="stChatMessage"] {
        background:rgba(255,255,255,.9); border:1px solid rgba(219,232,229,.95);
        border-radius:20px; padding:1.05rem 1.2rem;
        box-shadow:0 8px 26px rgba(32,78,73,.055); margin:.9rem 0;
    }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p { color:#303749; line-height:1.7; }
    [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"] { background:#e1f2ef; color:var(--violet); }
    [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] { background:linear-gradient(145deg,#26a394,#12665f); color:white; }
    [data-testid="stChatInput"] {
        border:1px solid #dce9e6; border-radius:18px; background:white;
        box-shadow:0 12px 34px rgba(31,91,83,.10); padding:.22rem .35rem;
    }
    [data-testid="stChatInput"]:focus-within { border-color:#82c7bd; box-shadow:0 0 0 3px rgba(22,124,117,.14),0 12px 34px rgba(31,91,83,.10); }
    [data-testid="stChatInput"] textarea { color:var(--ink); }
    [data-testid="stChatInput"] button { background:var(--violet)!important; color:white!important; border-radius:12px!important; }
    [data-testid="stChatInput"] button:hover { background:var(--violet-dark)!important; }
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#ffffff 0%,#f4faf8 100%); border-right:1px solid var(--line); }
    [data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 { letter-spacing:-.025em; }
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color:#434a5d; font-weight:600; }
    [data-testid="stSidebar"] textarea,[data-testid="stSidebar"] [data-baseweb="select"]>div { border-radius:12px; border-color:#dce9e6; background:white; }
    [data-testid="stSidebar"] button[kind="secondary"] { border-radius:12px; border:1px solid #dce9e6; color:#535b6f; background:white; }
    [data-testid="stSidebar"] button[kind="secondary"]:hover { border-color:#8bcac1; color:var(--violet-dark); }
        [data-testid="stSidebar"] [data-testid="stAlert"] { border-radius:12px; border:1px solid #d7ebe6; }
    [data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {
        background:#167c75!important; border-color:#167c75!important;
        box-shadow:0 0 0 3px rgba(22,124,117,.14);
    }
    [data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="slider"] > div > div {
        background-color:#167c75;
    }
    [data-testid="stSidebar"] [data-testid="stTextArea"] textarea:focus {
        border-color:#82c7bd; box-shadow:0 0 0 2px rgba(22,124,117,.12);
    }
    @media(max-width:700px) {
        [data-testid="stMainBlockContainer"] { padding:2rem 1rem 1rem; }
        h1 { font-size:2.1rem!important; }
        [data-testid="stChatMessage"] { padding:.85rem; border-radius:16px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------
with st.sidebar:
    st.title("⚙️ Settings")
    accent_theme = st.selectbox(
        "Accent theme",
        ["Lagoon", "Sapphire", "Blush"],
        help="Choose the color style for Clario.",
        key="clario_accent_theme",
    )
    theme_colors = {
        "Lagoon": ("#167c75", "#0f625d", "rgba(52,166,150,.16)", "#f5fbfa", "#f4faf8", "#e1f2ef"),
        "Sapphire": ("#4867c9", "#354da7", "rgba(85,119,220,.17)", "#f5f7ff", "#f4f6fd", "#e6ecff"),
        "Blush": ("#b65c70", "#914356", "rgba(208,119,142,.16)", "#fff7f8", "#fcf5f6", "#fae8ed"),
    }
    accent, accent_dark, glow, page_tint, sidebar_tint, user_tint = theme_colors[accent_theme]
    st.markdown(
        f"""<style>
        :root{{--violet:{accent};--violet-dark:{accent_dark};}}
        .stApp {{background:radial-gradient(ellipse at 50% -18%,{glow},transparent 45%),linear-gradient(180deg,{page_tint} 0%,#f4f8f8 50%,#f7faf9 100%);}}
        [data-testid="stSidebar"] {{background:linear-gradient(180deg,#fff 0%,{sidebar_tint} 100%);}}
        [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"] {{background:{user_tint};color:{accent};}}
        [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {{background:linear-gradient(145deg,{accent}, {accent_dark});}}
        [data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {{background:{accent}!important;border-color:{accent}!important;box-shadow:0 0 0 3px {glow};}}
        [data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="slider"] > div > div {{background-color:{accent};}}
        </style>""",
        unsafe_allow_html=True,
    )
    system_prompt = st.text_area("System prompt", value=DEFAULT_SYSTEM_PROMPT, height=140, key="clario_system_prompt")
    temperature = st.slider("Temperature", 0.0, 1.5, 0.7, 0.1)
    max_tokens = st.slider("Max tokens", 100, 2000, 800, 50)

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    try:
        cfg = get_config()
        st.success("Azure OpenAI configured")
        st.caption(f"Deployment: `{cfg['deployment']}`")
    except ConfigError as e:
        st.error(str(e))

# ---------- Header ----------
st.title("✨ Clario")
st.caption("Your AI assistant powered by Azure OpenAI")

# ---------- Chat state ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- Input ----------
if prompt := st.chat_input("Ask Clario anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            reply = st.write_stream(
                stream_reply(
                    st.session_state.messages,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            )
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except ConfigError as e:
            st.error(f"Configuration error: {e}. Check your .env file or Azure app settings.")
        except NotFoundError:
            st.error(
                "Deployment not found. AZURE_OPENAI_DEPLOYMENT must match the exact "
                "deployment name shown in Azure AI Foundry > Deployments (not the model name), "
                "and the endpoint must belong to the same resource."
            )
        except AuthenticationError:
            st.error("Authentication failed. Check AZURE_OPENAI_API_KEY and the endpoint.")
        except RateLimitError:
            st.error("Rate limit reached. Wait a moment and try again.")
        except APIConnectionError:
            st.error("Could not reach Azure OpenAI. Check the endpoint URL and your internet.")
        except Exception as e:  # noqa: BLE001
            st.error(f"Unexpected error: {e}")






