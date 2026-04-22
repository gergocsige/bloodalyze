import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import pandas as pd
import json

# Define the Pydantic schema for structured output
class Metric(BaseModel):
    metric_name: str
    patient_value: str
    standard_range: str
    status: str = Field(description="Must be exactly 'Normal', 'High', or 'Low'")
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

EXTRACTION AND FORMATTING RULES:
For each metric found in the uploaded test, extract the following fields and format them strictly according to the provided JSON schema:
- metric_name: The name of the test or biomarker (e.g., "Hemoglobin", "Cholesterol").
- patient_value: The value measured for the patient.
- standard_range: The reference or normal range provided on the test document.
- status: Classify the value. You MUST strictly use one of the following exact string values: "Normal", "High", or "Low".
- improvement_tip: If the status is "High" or "Low", provide a brief, general lifestyle tip. If the status is "Normal", output "N/A".
"""

def main():
    st.set_page_config(page_title="Bloodalyze", page_icon="🩸", layout="wide")

    # Strict Medical Disclaimer
    st.warning("⚠️ **Strict Medical Disclaimer:** This application is a University Proof of Concept (PoC) and does not provide medical advice. It is for educational purposes only. Always consult a qualified healthcare provider for medical diagnosis and treatment.")

    st.title("🩸 Bloodalyze")
    st.markdown("Upload your blood test results (PDF, JPG, or PNG) to extract key metrics and receive general lifestyle tips for out-of-range values.")

    # File Uploader
    uploaded_file = st.file_uploader("Choose a file", type=['png', 'jpg', 'jpeg', 'pdf'])

    if uploaded_file is not None:
        if st.button("Analyze Blood Test", type="primary"):
            if "GEMINI_API_KEY" not in st.secrets or not st.secrets["GEMINI_API_KEY"] or st.secrets["GEMINI_API_KEY"] == "YOUR_API_KEY_HERE":
                st.error("Please configure your Gemini API Key in `.streamlit/secrets.toml`.")
                return

            with st.spinner("Analyzing your blood test..."):
                try:
                    # Initialize the client
                    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                    
                    mime_type = uploaded_file.type
                    part = types.Part.from_bytes(
                        data=uploaded_file.getvalue(),
                        mime_type=mime_type,
                    )

                    # Multimodal AI Call with Structured Outputs
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[part, SYSTEM_PROMPT],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=BloodTestAnalysis,
                            temperature=0.1, # Low temperature for more deterministic extraction
                        )
                    )

                    # Parse JSON Output
                    result_json = json.loads(response.text)
                    
                    if "metrics" in result_json and len(result_json["metrics"]) > 0:
                        st.subheader("Analysis Results")
                        
                        df = pd.DataFrame(result_json["metrics"])
                        
                        # Apply styling based on status
                        def style_status(val):
                            if val == 'High' or val == 'Low':
                                return 'color: red; font-weight: bold;'
                            elif val == 'Normal':
                                return 'color: green;'
                            return ''
                        
                        # Use applymap for older pandas, map for newer.
                        # pandas >= 2.1.0 deprecated applymap in favor of map.
                        if hasattr(df.style, 'map'):
                            styled_df = df.style.map(style_status, subset=['status'])
                        else:
                            styled_df = df.style.applymap(style_status, subset=['status'])
                            
                        st.dataframe(styled_df, use_container_width=True)
                    else:
                        st.warning("No metrics could be extracted from the provided document.")

                except Exception as e:
                    st.error(f"An error occurred during analysis: {e}")

if __name__ == "__main__":
    main()
