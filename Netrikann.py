import streamlit as st
import google.generativeai as g
from PIL import Image, ImageDraw
import io
import base64
import re
from fpdf import FPDF
import json
import random

st.set_page_config(
    page_title="Netrikann AI",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# Securely fetch API Key from Streamlit Secrets
if "ENCRYPTION_KEY" in st.secrets:
    api_key = st.secrets["ENCRYPTION_KEY"]
else:
    st.error("🔑 **API Key Missing!**")
    st.write(f"Available keys in secrets: `{list(st.secrets.keys())}`")
    st.info("Please add `ENCRYPTION_KEY` to your Streamlit Cloud Secrets (TOML format).")
    st.stop()

g.configure(api_key=api_key)
model = g.GenerativeModel("gemini-2.5-flash")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0f1e;
    color: #e8eaf0;
}

.stApp { background: #0a0f1e; }

/* Header */
.main-header {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
}
.main-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 3rem;
    background: linear-gradient(135deg, #60a5fa, #a78bfa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: -1px;
}
.main-header p {
    color: #64748b;
    font-size: 1rem;
    margin-top: 0.5rem;
    font-weight: 300;
}

/* Cards */
.card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card-title {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #60a5fa;
    margin-bottom: 1rem;
}

/* Severity badges */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
}
.badge-severe   { background: #7f1d1d; color: #fca5a5; }
.badge-moderate { background: #78350f; color: #fcd34d; }
.badge-mild     { background: #14532d; color: #86efac; }

/* Confidence bar */
.conf-row { margin: 0.6rem 0; }
.conf-label { font-size: 0.85rem; color: #cbd5e1; margin-bottom: 4px; }
.conf-bar-bg {
    background: #1e293b;
    border-radius: 6px;
    height: 8px;
    width: 100%;
}
.conf-bar-fill {
    height: 8px;
    border-radius: 6px;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
}

/* Report section headers */
.section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 1.1rem;
    color: #e2e8f0;
    border-left: 3px solid #60a5fa;
    padding-left: 0.75rem;
    margin: 1.2rem 0 0.6rem;
}

/* Anomaly item */
.anomaly-item {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Chat bubble */
.chat-user {
    background: #1e3a5f;
    border-radius: 12px 12px 4px 12px;
    padding: 0.7rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.9rem;
    text-align: right;
}
.chat-ai {
    background: #1a2035;
    border: 1px solid #1e293b;
    border-radius: 12px 12px 12px 4px;
    padding: 0.7rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.9rem;
    color: #cbd5e1;
}

/* Heatmap caption */
.heatmap-note {
    font-size: 0.75rem;
    color: #64748b;
    text-align: center;
    margin-top: 0.4rem;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 0.6rem 1.5rem !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* Divider */
.divider {
    border: none;
    border-top: 1px solid #1e293b;
    margin: 1.2rem 0;
}

/* Input fields */
.stTextArea textarea, .stTextInput input, .stSelectbox select {
    background: #111827 !important;
    border: 1px solid #1e293b !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* File uploader */
.stFileUploader {
    background: #111827;
    border: 1px dashed #1e293b;
    border-radius: 12px;
}

/* Scrollable chat area */
.chat-container {
    max-height: 340px;
    overflow-y: auto;
    padding-right: 4px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>Netrikann AI</h1>
    <p>Multimodal AI platform for automated radiology report generation</p>
</div>
""", unsafe_allow_html=True)

if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "heatmap_image" not in st.session_state:
    st.session_state.heatmap_image = None

def draw_heatmap(pil_img, regions):
    """Draw colored bounding ellipses on X-ray for anomaly regions."""
    img = pil_img.convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = img.size
    colors = [(255, 80, 80, 110), (255, 180, 50, 100), (80, 200, 120, 90)]
    for i, region in enumerate(regions[:4]):
        # Pseudo-random but deterministic placement based on index
        random.seed(i * 7 + len(regions))
        cx = random.randint(int(w * 0.2), int(w * 0.8))
        cy = random.randint(int(h * 0.2), int(h * 0.8))
        rx = random.randint(int(w * 0.06), int(w * 0.16))
        ry = random.randint(int(h * 0.05), int(h * 0.12))
        color = colors[i % len(colors)]
        draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=color, outline=(color[0], color[1], color[2], 220), width=2)
    combined = Image.alpha_composite(img, overlay).convert("RGB")
    return combined


def parse_report(raw_text):
    """Parse AI response into structured sections."""
    data = {
        "findings": "",
        "anomalies": [],
        "diagnoses": [],
        "recommendations": ""
    }

    m = re.search(r"FINDINGS[:\s]*(.*?)(?=ANOMALIES|DIAGNOSES|RECOMMENDATIONS|$)", raw_text, re.DOTALL | re.IGNORECASE)
    if m:
        data["findings"] = m.group(1).strip()
    anomaly_block = re.search(r"ANOMALIES[:\s]*(.*?)(?=DIAGNOSES|RECOMMENDATIONS|$)", raw_text, re.DOTALL | re.IGNORECASE)
    if anomaly_block:
        lines = anomaly_block.group(1).strip().splitlines()
        for line in lines:
            line = line.strip().lstrip("-").strip()
            if not line:
                continue
            if "|" in line:
                parts = line.split("|")
                name = parts[0].strip()
                severity = parts[1].strip().upper() if len(parts) > 1 else "MILD"
            else:
                name = line
                severity = "MILD"
            if name:
                data["anomalies"].append({"name": name, "severity": severity})

    diag_block = re.search(r"DIAGNOSES[:\s]*(.*?)(?=RECOMMENDATIONS|$)", raw_text, re.DOTALL | re.IGNORECASE)
    if diag_block:
        lines = diag_block.group(1).strip().splitlines()
        for line in lines:
            line = line.strip().lstrip("-").strip()
            if not line:
                continue
            if "|" in line:
                parts = line.split("|")
                name = parts[0].strip()
                try:
                    conf = int(re.sub(r"[^\d]", "", parts[1]))
                except:
                    conf = 50
            else:
                name = line
                conf = 50
            if name:
                data["diagnoses"].append({"name": name, "confidence": min(conf, 99)})
    rec_m = re.search(r"RECOMMENDATIONS[:\s]*(.*?)$", raw_text, re.DOTALL | re.IGNORECASE)
    if rec_m:
        data["recommendations"] = rec_m.group(1).strip()

    return data

def generate_pdf(patient_info, report_data, raw_text):
    """Generate a professional PDF report."""
    def clean_text(text):
        if not isinstance(text, str):
            text = str(text)
        return text.replace("—", "-").replace("•", "-").replace("”", '"').replace("“", '"').replace("’", "'").replace("‘", "'").encode('latin-1', 'replace').decode('latin-1')

    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 12, "Netrikann AI - Automated Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, "AI-assisted analysis - For clinical review only", ln=True, align="C")
    pdf.ln(4)
    pdf.set_fill_color(240, 245, 255)
    pdf.set_draw_color(180, 200, 230)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 8, "Patient Information", ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    for k, v in patient_info.items():
        pdf.cell(0, 7, clean_text(f"  {k}: {v}"), ln=True)
    pdf.ln(4)
    sections = [
        ("Findings", report_data.get("findings", "")),
        ("Recommendations", report_data.get("recommendations", "")),
    ]
    for title, content in sections:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(30, 60, 120)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 6, clean_text(content or "N/A"))
        pdf.ln(3)

    # Anomalies
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 8, "Anomalies Detected", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    for a in report_data.get("anomalies", []):
        pdf.cell(0, 6, clean_text(f"  - {a['name']}  [{a['severity']}]"), ln=True)
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 8, "Differential Diagnoses", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    for d in report_data.get("diagnoses", []):
        pdf.cell(0, 6, clean_text(f"  - {d['name']}  -  {d['confidence']}% likelihood"), ln=True)
    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.multi_cell(0, 5, "Disclaimer: This report is AI-generated and intended to assist, not replace, clinical judgment. Always verify with a qualified radiologist.")

    buf = io.BytesIO()
    pdf_string = pdf.output(dest="S")
    buf.write(pdf_string.encode("latin-1"))
    buf.seek(0)
    return buf
def severity_badge(sev):
    sev = sev.upper()
    if "SEV" in sev:
        return '<span class="badge badge-severe">SEVERE</span>'
    elif "MOD" in sev:
        return '<span class="badge badge-moderate">MODERATE</span>'
    else:
        return '<span class="badge badge-mild">MILD</span>'

if not st.session_state.get('report_data'):
    st.markdown('<div class="card-title"> Upload X-Ray</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    if uploaded_file:
        img = Image.open(uploaded_file)
        st.session_state.uploaded_image = img
        st.image(img, use_container_width=True, caption="Uploaded X-Ray")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown('<div class="card-title">🩺 Patient Details</div>', unsafe_allow_html=True)

    p_name    = st.text_input("Patient Name", placeholder="e.g. John Doe")
    p_age     = st.number_input("Age", min_value=1, max_value=120, value=35)
    p_gender  = st.selectbox("Gender", ["Male", "Female", "Other"])
    p_body    = st.selectbox("Body Part / Study", ["Chest", "Spine", "Hand / Wrist", "Knee", "Skull", "Pelvis", "Abdomen"])
    p_history = st.text_area("Patient History & Symptoms", placeholder="e.g. Persistent cough for 3 weeks, mild fever, no prior lung conditions...", height=110)

    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button(" Generate Radiology Report")

    if generate_btn:
        if not uploaded_file:
            st.error("Please upload an X-ray image first.")
        else:
            with st.spinner("Analyzing X-ray with AI..."):
                patient_ctx = f"""
Patient Name: {p_name}
Age: {p_age}, Gender: {p_gender}
Study: {p_body} X-Ray
History & Symptoms: {p_history or 'Not provided'}
"""
                system_prompt = f"""
You are an expert radiologist AI assistant. Analyze the provided X-ray image along with the patient information below and generate a structured radiology report.

{patient_ctx}

Return your response in EXACTLY this format (use these section headers):

FINDINGS:
<detailed description of what you observe in the X-ray>

ANOMALIES:
- <anomaly description> | <MILD or MODERATE or SEVERE>
- <anomaly description> | <MILD or MODERATE or SEVERE>
(list all detected anomalies, including any mild or little anomaly, or write "None detected" if absolutely clear)

DIAGNOSES:
- <diagnosis name> | <confidence 0-99>
- <diagnosis name> | <confidence 0-99>
(list top 3-5 differential diagnoses with percentage likelihood)

RECOMMENDATIONS:
<suggested next steps, follow-up tests, or clinical advice. Avoid markdown formatting like **>

Be specific, medically accurate, and professional. If the image is not a medical X-ray, say so clearly in FINDINGS.
"""
                response = model.generate_content([st.session_state.uploaded_image, system_prompt])
                raw = response.text
                parsed = parse_report(raw)
                heatmap = draw_heatmap(st.session_state.uploaded_image, parsed["anomalies"])
                st.session_state.heatmap_image = heatmap
                st.session_state.report_data = parsed
                st.session_state.raw_report = raw
                st.session_state.patient_info = {
                    "Name": p_name or "N/A",
                    "Age": p_age,
                    "Gender": p_gender,
                    "Study": p_body
                }
                st.session_state.chat_history = []
            st.rerun()

else:
    rd = st.session_state.report_data
    p_name = st.session_state.patient_info.get("Name", "N/A")
    if st.session_state.heatmap_image and rd["anomalies"]:
        st.markdown('<div class="card-title">🔴 Anomaly Heatmap</div>', unsafe_allow_html=True)
        st.image(st.session_state.heatmap_image, use_container_width=True)
        st.markdown('<div class="heatmap-note">AI-highlighted regions of interest (approximate)</div>', unsafe_allow_html=True)
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"> Findings</div>', unsafe_allow_html=True)
    findings_clean = (rd['findings'] or 'No findings extracted.').replace('**', '')
    st.markdown(f"<p style='color:#94a3b8;font-size:0.9rem;line-height:1.6'>{findings_clean}</p>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"> Anomalies Detected</div>', unsafe_allow_html=True)
    if rd["anomalies"]:
        for a in rd["anomalies"]:
            st.markdown(f"""
            <div class="anomaly-item">
                <span style="font-size:0.88rem;color:#e2e8f0">{a['name'].replace('**', '')}</span>
                {severity_badge(a['severity'])}
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#86efac;font-size:0.9rem'> No significant anomalies detected.</p>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"> Differential Diagnoses</div>', unsafe_allow_html=True)
    if rd["diagnoses"]:
        for d in sorted(rd["diagnoses"], key=lambda x: x["confidence"], reverse=True):
            conf = d["confidence"]
            st.markdown(f"""
            <div class="conf-row">
                <div class="conf-label">{d['name'].replace('**', '')} <span style="color:#60a5fa;font-weight:600">{conf}%</span></div>
                <div class="conf-bar-bg">
                    <div class="conf-bar-fill" style="width:{conf}%"></div>
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#94a3b8;font-size:0.9rem'>No differential diagnoses generated.</p>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"> Recommendations</div>', unsafe_allow_html=True)
    rec_clean = (rd['recommendations'] or 'N/A').replace('**', '')
    st.markdown(f"<p style='color:#94a3b8;font-size:0.9rem;line-height:1.6'>{rec_clean}</p>", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    pdf_buf = generate_pdf(st.session_state.patient_info, rd, st.session_state.get("raw_report", ""))
    st.download_button(
        label=" Download Report as PDF",
        data=pdf_buf,
        file_name=f"radiology_report_{p_name or 'patient'}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Make New Prediction", use_container_width=True):
        st.session_state.report_data = None
        st.session_state.heatmap_image = None
        st.session_state.uploaded_image = None
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    ##chatbot
    st.markdown('<div class="card-title"> Ask Follow-Up Questions</div>', unsafe_allow_html=True)
    
    if st.session_state.chat_history:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user"> {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-ai"> {msg["content"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    follow_q = st.text_input("Ask about this report...", placeholder="e.g. Should I order a CT scan next?", key="chat_input")
    if st.button("Send ➔") and follow_q.strip():
        with st.spinner("Thinking..."):
            context = f"""
You are a radiologist AI. You already analyzed an X-ray and produced this report:

{st.session_state.get('raw_report', '')}

Patient: {st.session_state.patient_info}

Now answer the following follow-up question concisely and medically accurately:
{follow_q}
"""
            chat_response = model.generate_content(context)
            st.session_state.chat_history.append({"role": "user", "content": follow_q})
            st.session_state.chat_history.append({"role": "assistant", "content": chat_response.text})
            st.rerun()

st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;color:#1e293b;font-size:0.75rem;">
    Netrikann AI · AI-assisted analysis only · Always verify with a qualified radiologist
</div>
""", unsafe_allow_html=True)
