import html
import json
import os

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/extract")
MISSING_VALUES = {"", "n/a", "na", "none", "null", "not available"}

st.set_page_config(
    page_title="Insurance Document Intelligence for Automated Policy and Claim Intake",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #172a3a;
        --muted: #647789;
        --line: #e4ebf0;
        --brand: #167c72;
        --brand-dark: #11645d;
        --canvas: #f5f8fa;
    }

    html, body, [class*="css"] {
        font-family: 'Aptos', 'Segoe UI', sans-serif;
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
    [data-testid="stHeader"] { background: rgba(245, 248, 250, 0.88); }
    [data-testid="stSidebar"] {
        background: #f0f4f6;
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.4rem; }
    .block-container {
        max-width: 1120px;
        margin: 0 auto;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    h1, h2, h3 {
        font-family: 'Aptos Display', 'Segoe UI', sans-serif !important;
        color: var(--ink) !important;
        letter-spacing: -0.035em;
    }
    h1 { font-size: clamp(2rem, 3vw, 2.8rem) !important; }
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
        font-family: 'Aptos Display', 'Segoe UI', sans-serif;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #fff;
        border-color: var(--line) !important;
        border-radius: 16px;
        box-shadow: 0 3px 12px rgba(27, 55, 75, 0.035);
    }
    [data-testid="stFileUploader"] section {
        background: #f9fbfc;
        border: 1px dashed #9bb9b4;
        border-radius: 14px;
    }
    [data-testid="stFormSubmitButton"] button,
    [data-testid="stDownloadButton"] button {
        background: var(--brand);
        color: #fff;
        border: 1px solid var(--brand);
        border-radius: 10px;
        min-height: 2.8rem;
        font-weight: 700;
        transition: transform 160ms ease, box-shadow 160ms ease, background 160ms ease;
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
        max-width: 800px;
        margin-top: -0.65rem;
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
        background: #f9fbfc;
        color: var(--muted);
        font-size: 0.83rem;
        line-height: 1.55;
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
    st.caption("Insurance Document Intelligence")

st.markdown('<div class="eyebrow">Claims operations · Document intelligence</div>', unsafe_allow_html=True)
st.title("Insurance Document Intelligence for Automated Policy and Claim Intake")
st.markdown(
    '<div class="hero-copy">Automated policy and claim intake, built to turn insurance '
    "documents into structured information your team can review.</div>",
    unsafe_allow_html=True,
)
st.write("")

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
            with st.spinner("Analyzing the document and extracting claim details..."):
                response = requests.post(
                    API_URL,
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type or "application/octet-stream",
                        )
                    },
                    timeout=(60, 300),
                )
            if not response.ok:
                try:
                    detail = response.json().get("detail", response.text)
                except ValueError:
                    detail = response.text
                st.error(f"Document analysis failed ({response.status_code}): {detail}")
            else:
                payload = response.json()
                st.session_state["claim_result"] = parse_entities(payload.get("entities"))
                st.session_state["claim_filename"] = uploaded_file.name
                st.success("Document analyzed. Review the extracted information below.")
        except requests.exceptions.ConnectionError:
            st.error(
                "The claim intake API is not reachable. Start the FastAPI backend in "
                "a second terminal: `.venv\\Scripts\\python.exe -m uvicorn "
                "main:app --reload --port 8000`."
            )
        except requests.exceptions.Timeout:
            st.error("Analysis timed out. Check the backend and retry the document.")
        except requests.exceptions.RequestException as exc:
            st.error(f"Could not reach the claim intake API: {exc}")
        except (ValueError, json.JSONDecodeError) as exc:
            st.error(f"The backend returned an invalid extraction result: {exc}")

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
    "</div>",
    unsafe_allow_html=True,
)
