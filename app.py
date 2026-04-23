import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import pandas as pd
import json
from tenacity import retry, stop_after_attempt, wait_exponential
from translations import translations

# Define the Pydantic schema for structured output
class Metric(BaseModel):
    metric_name: str
    patient_value: str
    standard_range: str
    status: str = Field(description="Classify the value. Use the provided language to translate 'Normal', 'High', or 'Low'.")
    improvement_tip: str

class BloodTestAnalysis(BaseModel):
    metrics: list[Metric]

SYSTEM_PROMPT = """
You are an expert AI assistant analyzing uploaded blood test results for a University Proof of Concept project.
Your primary tasks are to extract key blood test metrics from the uploaded image or document and provide general lifestyle or dietary tips ONLY for out-of-range values.

CRITICAL MEDICAL DISCLAIMER INSTRUCTIONS:
- You are an AI, not a doctor. You must not diagnose, treat, or prevent any medical condition.
- Any improvement tip must be extremely generic, conservative lifestyle advice (e.g., "stay hydrated", "eat a balanced diet rich in iron") rather than specific medical treatments or supplement prescriptions.
- If you cannot confidently extract a value, omit it rather than guessing.

STRICT LANGUAGE RULE:
You must translate all output into {language}. The JSON keys must remain in English for parsing (metric_name, patient_value, standard_range, status, improvement_tip), but the VALUES associated with these keys (especially the 'improvement_tip' and 'status') MUST be written in {language}. For 'status', translate 'Normal', 'High', and 'Low' into {language}.

EXTRACTION AND FORMATTING RULES:
For each metric found in the uploaded test, extract the following fields and format them strictly according to the provided JSON schema:
- metric_name: The name of the test or biomarker (e.g., "Hemoglobin", "Cholesterol").
- patient_value: The value measured for the patient.
- standard_range: The reference or normal range provided on the test document.
- status: Classify the value. You MUST strictly use one of the translated equivalent string values for: "Normal", "High", or "Low" in {language}.
- improvement_tip: If the status is "High" or "Low", provide a brief, general lifestyle tip in {language}. If the status is "Normal", output "N/A".
"""

def main():
    st.set_page_config(page_title="Bloodalyze", page_icon="🩸", layout="wide")

    if 'language' not in st.session_state:
        st.session_state.language = 'English'
    
    st.sidebar.radio("Language / Nyelv", ["English", "Magyar"], key="language")
    lang = st.session_state.language
    t = translations[lang]

    # Strict Medical Disclaimer
    st.warning(t["disclaimer_warning"])
    st.page_link("pages/Disclaimer.py", label=t["read_disclaimer"], icon="ℹ️")

    st.title(t["page_title"])
    st.markdown(t["upload_desc"])

    # File Uploader
    uploaded_file = st.file_uploader(t["choose_file"], type=['png', 'jpg', 'jpeg', 'pdf'])

    if uploaded_file is not None:
        if st.button(t["analyze_btn"], type="primary"):
            if "GEMINI_API_KEY" not in st.secrets or not st.secrets["GEMINI_API_KEY"] or st.secrets["GEMINI_API_KEY"] == "YOUR_API_KEY_HERE":
                st.error(t["api_key_error"])
                return

            with st.spinner(t["analyzing_spinner"]):
                try:
                    # Initialize the client
                    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                    
                    mime_type = uploaded_file.type
                    part = types.Part.from_bytes(
                        data=uploaded_file.getvalue(),
                        mime_type=mime_type,
                    )

                    # Multimodal AI Call with Structured Outputs
                    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
                    def _generate_content():
                        return client.models.generate_content(
                            model='gemini-3.1-flash-lite-preview',
                            contents=[part, SYSTEM_PROMPT.format(language=lang)],
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                                response_schema=BloodTestAnalysis,
                                temperature=0.1, # Low temperature for more deterministic extraction
                            )
                        )
                    
                    response = _generate_content()

                    # Parse JSON Output
                    result_json = json.loads(response.text)
                    
                    if "metrics" in result_json and len(result_json["metrics"]) > 0:
                        st.subheader(t["analysis_results"])
                        
                        # We must accept translated normal values too
                        normal_values = ["Normal", "Normál"]
                        out_of_range = [m for m in result_json["metrics"] if m.get("status") not in normal_values]
                        
                        if not out_of_range:
                            st.success(t["all_normal"])
                            st.balloons()
                        else:
                            st.markdown(t["attention_needed"])
                            for m in out_of_range:
                                status = m.get('status')
                                name = m.get('metric_name')
                                value = m.get('patient_value')
                                ref_range = m.get('standard_range')
                                tip = m.get('improvement_tip')
                                
                                with st.expander(f"⚠️ {name} - {status}", expanded=True):
                                    st.error(f"**{t['status_label']}:** {status}")
                                    col1, col2 = st.columns(2)
                                    col1.metric(t["patient_value_label"], value)
                                    col2.metric(t["standard_range_label"], ref_range)
                                    
                                    st.markdown(f"**💡 {t['tip_label']}:** {tip}")
                    else:
                        st.warning(t["no_metrics"])

                except Exception as e:
                    st.error(f"{t['error_occurred']}{e}")

if __name__ == "__main__":
    main()
