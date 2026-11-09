import html
import json
import os

import httpx
import requests
import streamlit as st
from google.genai.errors import APIError
from streamlit.errors import StreamlitSecretNotFoundError

from services.entity_extraction import (
    GeminiConfigurationError,
    extract_entities,
)


API_URL = os.getenv("API_URL")
MISSING_VALUES = {"", "n/a", "na", "none", "null", "not available"}

st.set_page_config(
    page_title="Insurance Document Intelligence for Automated Policy and Claim Intake",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def get_gemini_secret():
    if os.getenv("GEMINI_API_KEY"):
        return None
    try:
        return st.secrets["GEMINI_API_KEY"]
    except (StreamlitSecretNotFoundError, KeyError):
        return None


st.markdown(
    """
    <style>
    :root {
        --ink: #1e293b;
        --muted: #64748b;
        --line: #e2e8f0;
        --brand: #0f766e;
        --brand-dark: #115e59;
        --canvas: #f8f9fa;
    }

    html, body, [class*="css"], button, input, textarea {
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
            "Segoe UI", sans-serif;
        color: var(--ink);
    }
    .stApp {
        background: var(--canvas);
        color-scheme: light;
    }
    [data-testid="stAppViewContainer"] {
        background: var(--canvas);
        color: var(--ink);
    }
    [data-testid="stWidgetLabel"] p,
    [data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stFileUploaderDropzoneInstructions"] > div,
    [data-testid="stFileUploaderDropzoneInstructions"] small {
        color: var(--ink) !important;
    }
    [data-testid="stHeader"] { background: rgba(248, 249, 250, 0.88); }
    [data-testid="stSidebar"] {
        background: #f1f5f9;
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] > div:first-child {
        padding: 1.4rem 1rem 1rem;
    }
    .block-container {
        max-width: 1160px;
        margin: 0 auto;
        padding-top: 2.25rem;
        padding-bottom: 3rem;
    }
    h1, h2, h3 {
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
            "Segoe UI", sans-serif !important;
        color: var(--ink) !important;
        letter-spacing: -0.035em;
    }
    h1 {
        font-size: clamp(2rem, 3.2vw, 2.85rem) !important;
        font-weight: 800 !important;
        line-height: 1.12 !important;
    }
    h2 { font-size: 1.35rem !important; }
    h3 { font-size: 1.05rem !important; }
    [data-testid="stMetric"] {
        background: #fff;
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        box-shadow: 0 2px 8px rgba(27, 55, 75, 0.035);
    }
    [data-testid="stMetricLabel"] p {
        color: var(--muted);
        font-weight: 600;
    }
    [data-testid="stMetricValue"] {
        color: var(--ink);
        font-family: Inter, ui-sans-serif, system-ui, sans-serif;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #fff;
        border-color: var(--line) !important;
        border-radius: 18px;
        box-shadow: 0 8px 28px rgba(15, 23, 42, 0.045);
    }
    [data-testid="stFileUploader"] section {
        background: #f8fafc;
        border: 1px dashed #94a3b8;
        border-radius: 12px;
    }
    [data-testid="stFormSubmitButton"] button,
    [data-testid="stDownloadButton"] button {
        background: var(--brand);
        color: #fff;
        border: 1px solid var(--brand);
        border-radius: 8px;
        min-height: 3rem;
        font-weight: 700;
        transition: transform 180ms ease, box-shadow 180ms ease, background 180ms ease;
    }
    [data-testid="stFormSubmitButton"] button:hover,
    [data-testid="stDownloadButton"] button:hover {
        background: var(--brand-dark);
        color: #fff;
        border-color: var(--brand-dark);
        box-shadow: 0 7px 16px rgba(17, 100, 93, 0.2);
        transform: translateY(-1px);
    }
    [data-testid="stTabs"] button { font-weight: 600; }
    .brand-lockup {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        margin: 0.2rem 0 1.8rem;
        color: var(--ink);
        font: 800 1rem 'Aptos', 'Segoe UI', sans-serif;
    }
    .brand-mark {
        display: grid;
        place-items: center;
        width: 2.35rem;
        height: 2.35rem;
        border-radius: 10px;
        color: white;
        background: var(--brand);
        font-size: 1.15rem;
    }
    .eyebrow {
        margin: 0 0 0.5rem;
        color: var(--brand-dark);
        font-size: 0.74rem;
        font-weight: 800;
        letter-spacing: 0.13em;
        text-transform: uppercase;
    }
    .hero-copy {
        max-width: 760px;
        margin: 0.15rem auto 0;
        color: var(--muted);
        font-size: 1.03rem;
        line-height: 1.7;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.42rem 0.75rem;
        border: 1px solid #cde7dc;
        border-radius: 999px;
        background: #eff9f3;
        color: #23734c;
        font-size: 0.8rem;
        font-weight: 700;
    }
    .section-label {
        margin: 0 0 0.9rem;
        color: var(--muted);
        font-size: 0.74rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    .field-label {
        margin-bottom: 0.2rem;
        color: var(--muted);
        font-size: 0.78rem;
        font-weight: 600;
    }
    .field-value {
        overflow-wrap: anywhere;
        color: var(--ink);
        font-size: 0.94rem;
        font-weight: 600;
    }
    .sidebar-note {
        padding: 0.9rem;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: #fff;
        color: var(--muted);
        font-size: 0.83rem;
        line-height: 1.55;
    }
    .github-link {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        color: var(--brand-dark) !important;
        font-size: 0.88rem;
        font-weight: 700;
        text-decoration: none !important;
    }
    .github-link:hover { text-decoration: underline !important; }
    @media (max-width: 640px) {
        .block-container {
            padding: 1.25rem 1rem 2rem;
        }
        h1 { font-size: 2rem !important; }
        .eyebrow { font-size: 0.66rem; }
    }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def has_value(value):
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip().lower() not in MISSING_VALUES
    if isinstance(value, (dict, list, tuple)):
        return bool(value)
    return True


def display_value(value):
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def render_fields(data, columns=3):
    if not isinstance(data, dict):
        st.write(display_value(data))
        return

    fields = [(key, value) for key, value in data.items() if has_value(value)]
    if not fields:
        st.caption("No details were found in this section.")
        return

    for start in range(0, len(fields), columns):
        row = st.columns(columns)
        for column, (label, value) in zip(row, fields[start : start + columns]):
            with column:
                st.markdown(
                    f'<div class="field-label">{html.escape(str(label))}</div>'
                    f'<div class="field-value">{html.escape(display_value(value))}</div>',
                    unsafe_allow_html=True,
                )


def render_card(title, data, columns=3):
    if not has_value(data):
        return
    with st.container(border=True):
        st.markdown(f'<div class="section-label">{title}</div>', unsafe_allow_html=True)
        render_fields(data, columns=columns)


def render_records(title, records):
    records = [record for record in records if isinstance(record, dict)]
    if not records:
        st.caption(f"No {title.lower()} found.")
        return

    st.markdown(f"#### {title}")
    st.dataframe(records, hide_index=True, width="stretch")


def render_record_details(title, record, index):
    if not isinstance(record, dict):
        return
    with st.expander(f"{title} {index + 1}", expanded=index == 0):
        render_fields(record)


def parse_entities(raw_entities):
    if isinstance(raw_entities, dict):
        return raw_entities
    if not isinstance(raw_entities, str):
        raise ValueError("The backend returned an unexpected entities format.")
    cleaned = raw_entities.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "", 1).replace("```", "").strip()
    result = json.loads(cleaned)
    if not isinstance(result, dict):
        raise ValueError("The extracted result is not a JSON object.")
    return result


with st.sidebar:
    st.markdown(
        '<div class="brand-lockup"><span class="brand-mark">+</span>'
        "<span>Policy Intelligence</span></div>",
        unsafe_allow_html=True,
    )
    st.markdown("### Claim workspace")
    st.caption("Automated intake and policy document review")
    st.divider()
    st.markdown("**New claim intake**")
    st.caption("Upload a form to extract policyholder, coverage, and loss details.")
    st.markdown(
        """
        <div class="sidebar-note">
        <strong>Supported files</strong><br>
        PDF, PNG, JPG, and JPEG<br><br>
        Documents are analyzed by the configured Gemini API.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown(
        '<a class="github-link" href="https://github.com/akarsh11111111" '
        'target="_blank" rel="noopener noreferrer">GitHub profile <span>↗</span></a>',
        unsafe_allow_html=True,
    )
    st.write("")
    st.caption("Insurance Document Intelligence")

_, hero_column, _ = st.columns([1, 8, 1])
with hero_column:
    st.markdown(
        '<div class="eyebrow">Claims operations · Document intelligence</div>',
        unsafe_allow_html=True,
    )
    st.title("Insurance Document Intelligence for Automated Policy and Claim Intake")
    st.markdown(
        '<div class="hero-copy">Automated policy and claim intake, built to turn '
        "insurance documents into structured information your team can review.</div>",
        unsafe_allow_html=True,
    )
    st.write("")

_, intake_column, _ = st.columns([1, 8, 1])
with intake_column:
    with st.container(border=True):
        with st.form("claim_intake_form", clear_on_submit=False):
            uploaded_file = st.file_uploader(
                "Upload a claim or policy document",
                type=["pdf", "png", "jpg", "jpeg"],
                help="Choose a PDF or image. Maximum file size is 200 MB.",
            )
            submitted = st.form_submit_button(
                "Analyze document",
                type="primary",
                width="stretch",
            )

if submitted:
    if uploaded_file is None:
        st.warning("Choose a document before starting analysis.")
    else:
        try:
            entities_result = None
            with st.spinner("Analyzing the document and extracting claim details..."):
                file_bytes = uploaded_file.getvalue()
                mime_type = uploaded_file.type or "application/octet-stream"
                if API_URL:
                    response = requests.post(
                        API_URL,
                        files={"file": (uploaded_file.name, file_bytes, mime_type)},
                        timeout=(60, 300),
                    )
                    if not response.ok:
                        try:
                            detail = response.json().get("detail", response.text)
                        except ValueError:
                            detail = response.text
                        st.error(
                            f"Document analysis failed ({response.status_code}): {detail}"
                        )
                    else:
                        entities_result = parse_entities(response.json().get("entities"))
                else:
                    entities_result = parse_entities(
                        extract_entities(
                            file_bytes,
                            mime_type,
                            api_key=get_gemini_secret(),
                        )
                    )

            if entities_result:
                st.session_state["claim_result"] = entities_result
                st.session_state["claim_filename"] = uploaded_file.name
                st.success("Document analyzed. Review the extracted information below.")
        except GeminiConfigurationError:
            st.error(
                "Gemini API key is missing. Add GEMINI_API_KEY to your local .env "
                "file or to this app's Streamlit Community Cloud secrets."
            )
        except APIError as exc:
            st.error(f"Gemini could not analyze the document: {exc}")
        except httpx.HTTPError as exc:
            st.error(f"Could not connect to Gemini: {exc}")
        except requests.exceptions.ConnectionError:
            st.error("The configured claim intake API is not reachable.")
        except requests.exceptions.Timeout:
            st.error("Analysis timed out. Check the API and retry the document.")
        except requests.exceptions.RequestException as exc:
            st.error(f"Could not reach the claim intake API: {exc}")
        except ValueError as exc:
            st.error(f"The extraction service returned invalid data: {exc}")

entities = st.session_state.get("claim_result")
if entities:
    st.write("")
    filename = st.session_state.get("claim_filename", "Uploaded document")
    doc_info = entities.get("Document Information", {})
    insured = entities.get("Named Insureds", {})
    first_insured = insured.get("First Named Insured", {}) if isinstance(insured, dict) else {}
    business = entities.get("Business Information", {})
    policy = entities.get("Policy Details", {})
    premium = entities.get("Premium Information", {})
    contacts = entities.get("Contacts", [])
    locations = entities.get("Premises/Locations", [])
    claims = entities.get("Loss History", [])
    lines = entities.get("Lines of Business", {})
    selected_lines = [
        name
        for name, details in lines.items()
        if isinstance(details, dict) and details.get("Selected")
    ] if isinstance(lines, dict) else []

    st.markdown(
        f'<div class="status-pill">● Analysis complete</div> '
        f'<span style="color:#647789;margin-left:.5rem">{html.escape(filename)}</span>',
        unsafe_allow_html=True,
    )
    st.write("")

    metric_columns = st.columns(4)
    metric_columns[0].metric(
        "Named insured",
        first_insured.get("Legal Name", "Not identified")
        if isinstance(first_insured, dict)
        else "Not identified",
    )
    metric_columns[1].metric("Coverage lines", len(selected_lines))
    metric_columns[2].metric("Locations", len(locations) if isinstance(locations, list) else 0)
    metric_columns[3].metric("Loss records", len(claims) if isinstance(claims, list) else 0)

    overview_tab, policy_tab, exposure_tab, contacts_tab, raw_tab = st.tabs(
        ["Overview", "Policy & coverage", "Locations & losses", "People & notes", "Extracted JSON"]
    )

    with overview_tab:
        left, right = st.columns(2, gap="large")
        with left:
            render_card("Named insured", first_insured)
            render_card("Business profile", business)
            render_card("Agency", entities.get("Agency Information", {}))
        with right:
            render_card("Policy period", policy)
            render_card("Premium summary", premium)
            render_card("Carrier", entities.get("Carrier Information", {}))
        if has_value(doc_info):
            with st.expander("Document details"):
                render_fields(doc_info)
        with st.expander("Transaction details"):
            render_fields(entities.get("Transaction Details", {}))

    with policy_tab:
        render_card("Policy details", policy)
        render_card("Transaction", entities.get("Transaction Details", {}))
        if selected_lines:
            render_records(
                "Selected coverage",
                [
                    {
                        "Coverage": name,
                        "Limits": details.get("Limits", "N/A"),
                        "Premium": details.get("Premium", "N/A"),
                    }
                    for name, details in lines.items()
                    if isinstance(details, dict) and details.get("Selected")
                ],
            )
        else:
            st.info("No selected coverage lines were identified.")
        render_card("Premium analysis", premium)

    with exposure_tab:
        render_records("Premises and locations", locations if isinstance(locations, list) else [])
        if isinstance(locations, list):
            for index, location in enumerate(locations):
                render_record_details("Location", location, index)
        render_records(
            "Loss history",
            claims if isinstance(claims, list) else [],
        )
        if isinstance(claims, list):
            for index, claim in enumerate(claims):
                render_record_details("Loss record", claim, index)
        render_records(
            "Prior insurance",
            entities.get("Prior Insurance", [])
            if isinstance(entities.get("Prior Insurance"), list)
            else [],
        )
        render_records(
            "Additional interests",
            entities.get("Additional Interests", [])
            if isinstance(entities.get("Additional Interests"), list)
            else [],
        )

    with contacts_tab:
        render_records("Contacts", contacts if isinstance(contacts, list) else [])
        render_card("Underwriter", entities.get("Underwriter Information", {}))
        render_card("Signatures", entities.get("Signatures", {}))
        render_card("General information", entities.get("General Information", {}))
        remarks = entities.get("Remarks")
        if has_value(remarks):
            render_card("Remarks", {"Notes": remarks})

    with raw_tab:
        st.caption("Review or download the structured extraction returned by the API.")
        st.download_button(
            "Download extracted JSON",
            data=json.dumps(entities, indent=2, ensure_ascii=False),
            file_name="claim-extraction.json",
            mime="application/json",
        )
        st.json(entities)

st.markdown(
    "<div style='padding-top:2rem;color:#80909c;font-size:.8rem'>"
    "Insurance Document Intelligence for Automated Policy and Claim Intake"
    " &nbsp;·&nbsp; "
    '<a href="https://github.com/akarsh11111111" target="_blank" '
    'rel="noopener noreferrer" style="color:#115e59;text-decoration:none;font-weight:700">'
    "GitHub profile ↗</a>"
    "</div>",
    unsafe_allow_html=True,
)
