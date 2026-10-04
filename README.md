# 📚 SnapStudy AI

SnapStudy AI is a Streamlit application that uses Gemini Vision + chat to help students understand questions, diagrams, notes, and textbook pages from photos.

It follows the workshop pattern:

Onboarding → Upload photo/text → Gemini Vision → Chat → Study summary → Email

## Features

- Student onboarding with name and email
- Upload JPG/JPEG/PNG study images
- Ask text questions
- Gemini Vision understands the uploaded image
- Follow-up chat questions
- Generate a study summary
- Send the summary through Gmail SMTP

## 1. Create the environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Install packages:

```powershell
pip install -r requirements.txt
```

## 2. Get a Gemini API key

Create a Gemini API key from Google AI Studio.

## 3. Configure Gmail

Use a Gmail account for sending.

Enable 2-Step Verification and create a Gmail App Password.

Do not put your normal Gmail password in the application.

## 4. Create secrets.toml

Copy:

```text
.streamlit/secrets.toml.example
```

to:

```text
.streamlit/secrets.toml
```

Fill in:

```toml
GEMINI_API_KEY = "your-key"

GMAIL_ADDRESS = "your-gmail@gmail.com"
GMAIL_APP_PASSWORD = "your-app-password"
```

## 5. Run

```powershell
streamlit run app.py
```

Open the local URL shown by Streamlit, normally:

```text
http://localhost:8501
```

## Project flow

```text
Student
   ↓
Onboarding
   ↓
Upload study photo / type question
   ↓
Gemini Vision + Chat
   ↓
Explanation
   ↓
Follow-up questions
   ↓
Send Notes
   ↓
Gmail
```

## Important security rule

Never commit:

```text
.streamlit/secrets.toml
```

to GitHub.
