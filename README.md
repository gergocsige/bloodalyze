# 🩸 Bloodalyze

A lightweight, AI-powered web application that analyzes uploaded blood test results and provides personalized, conservative lifestyle tips for out-of-range metrics.

![Python](https://img.shields.io/badge/Python-3.14+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.56+-FF4B4B?logo=streamlit&logoColor=white)
![Gemini API](https://img.shields.io/badge/Google_GenAI-Gemini-4285F4?logo=google&logoColor=white)

> [!CAUTION]
> ### ⚠️ STRICT MEDICAL DISCLAIMER
> This application is an **academic Proof of Concept** created for a Prompt Engineering class. It relies on Large Language Models (LLMs) which can hallucinate and produce incorrect results. **This is NOT a medical tool.** It is strictly NOT for medical diagnostic use. Always consult a qualified healthcare provider or a real doctor for medical advice, diagnosis, and treatment.

## ✨ Key Features
- **Multimodal AI Analysis:** Seamlessly parses text and tables from PDFs and images (PNG, JPG) using the `google-genai` SDK.
- **Structured JSON Data Extraction:** Forces the Gemini API to adhere strictly to a Pydantic schema, ensuring reliable, machine-readable output.
- **Bilingual Support (i18n):** Full UI and AI-output support for both English and Hungarian (Magyar) via robust session state management.
- **State Management & Memoization:** Employs Streamlit's `@st.cache_data` and session state to preserve parsed data and user preferences across page navigation, drastically reducing API token costs.
- **Resilience Engineering:** Implements robust error handling and exponential backoff for the Gemini API using the `tenacity` library to combat rate limits and server errors.

## 🛠️ Tech Stack
- **Python** 
- **Streamlit** (Frontend & Routing)
- **Google Gemini API** (`google-genai` SDK, `gemini-3.1-flash-lite-preview` model)
- **Tenacity** (Retry logic)
- **Pydantic** (Schema validation)
- **Pandas** (Data manipulation)

## 💻 Local Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd bloodalyze
   ```

2. **Set up a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Secrets (CRITICAL):**
   You must provide a Google Gemini API key for the application to function. Create a directory named `.streamlit` and a file inside it named `secrets.toml`:
   ```bash
   mkdir .streamlit
   touch .streamlit/secrets.toml
   ```
   Add the following line to your new `secrets.toml` file:
   ```toml
   GEMINI_API_KEY = "your_actual_api_key_here"
   ```
> [!WARNING]  
> **Do NOT commit `.streamlit/secrets.toml` to Git!** This file should remain excluded in `.gitignore` to prevent leaking your private API keys.

## 🚀 Usage

1. Start the Streamlit server:
   ```bash
   streamlit run app.py
   ```
2. Open the provided Local URL in your browser (usually `http://localhost:8501`).
3. Toggle your preferred language (English or Magyar) in the top right corner.
4. Upload a blood test document (PDF, JPG, or PNG).
5. Click **Analyze Blood Test**.
6. View the extracted metrics. Out-of-range values will automatically expand into "Attention Needed" cards containing context-aware lifestyle tips!

## 🎓 Academic Context
This application was developed as a university project for a **Prompt Engineering** course. It serves to showcase advanced LLM orchestration, multimodal document reasoning, structured output generation, and agentic development workflows.
