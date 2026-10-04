import smtplib
from email.mime.text import MIMEText

import streamlit as st
from google import genai
from google.genai import types

from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE, SUMMARY_REQUEST_PROMPT

# -----------------------------
# Basic configuration
# -----------------------------
MODEL_NAME = "gemini-3.5-flash"

st.set_page_config(
    page_title="SnapStudy AI",
    page_icon="📚",
    layout="centered",
)

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = st.secrets["GMAIL_APP_PASSWORD"]


# -----------------------------
# Create Gemini client once
# -----------------------------
@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


gemini_client = get_gemini_client()


# -----------------------------
# Gmail sending function
# -----------------------------
def send_email(to_address, subject, body):
    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = GMAIL_ADDRESS
    message["To"] = to_address

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(message)


# -----------------------------
# Chat UI helpers
# -----------------------------
def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"])


def add_message(role, kind, content):
    st.session_state.messages.append(
        {
            "role": role,
            "kind": kind,
            "content": content,
        }
    )


def ask_gemini(parts):
    try:
        response = st.session_state.chat.send_message(parts)
        return response.text
    except Exception as error:
        return f"Sorry, something went wrong: {error}"


# -----------------------------
# Onboarding
# -----------------------------
if "onboarded" not in st.session_state:
    st.title("📚 SnapStudy AI")
    st.caption("Snap it. Understand it. Save the explanation.")

    with st.form("onboarding_form"):
        name = st.text_input("Your name")
        email = st.text_input(
            "Email address",
            placeholder="you@example.com",
            help="The study summary will be sent to this address.",
        )

        submitted = st.form_submit_button("Let's study 🚀")

    if submitted:
        if not name.strip() or not email.strip():
            st.warning("Please enter both your name and email address.")
        else:
            st.session_state.name = name.strip()
            st.session_state.email = email.strip()

            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                ),
            )

            st.session_state.messages = []
            st.session_state.onboarded = True
            st.rerun()

    st.stop()


# -----------------------------
# Main screen
# -----------------------------
header_col, button_col = st.columns([5, 2], vertical_alignment="center")

with header_col:
    st.title("📚 SnapStudy AI")

with button_col:
    send_disabled = len(st.session_state.messages) <= 1

    if st.button(
        "📧 Send Notes",
        disabled=send_disabled,
        use_container_width=True,
    ):
        with st.spinner("Creating your study summary..."):
            summary = ask_gemini([SUMMARY_REQUEST_PROMPT])

        try:
            send_email(
                st.session_state.email,
                "Your SnapStudy AI Summary",
                summary,
            )
            st.success("Sent! Check your email 📧")
        except Exception as error:
            st.error(f"Couldn't send the email: {error}")


st.caption(
    f"Student: {st.session_state.name} • "
    f"Summary destination: {st.session_state.email}"
)


# -----------------------------
# Display chat history
# -----------------------------
if not st.session_state.messages:
    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name),
    )

for message in st.session_state.messages:
    render_message(message)


# -----------------------------
# Text + image input
# -----------------------------
user_input = st.chat_input(
    "Ask a question, or attach a study photo",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()

        add_message("user", "image", photo_bytes)

        parts.append(
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type,
            )
        )

    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        parts.append(
            "Analyze this study image. Identify the question or concept "
            "and explain it step-by-step in simple language."
        )

    with st.spinner("Gemini is studying the image..."):
        answer = ask_gemini(parts)

    add_message("assistant", "text", answer)
    st.rerun()
