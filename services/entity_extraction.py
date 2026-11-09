import json
import os

from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL


class GeminiConfigurationError(RuntimeError):
    """Raised when Gemini credentials are not configured."""


ENTITY_SCHEMA = {
    "Document Information": {},
    "Agency Information": {},
    "Transaction Details": {},
    "Named Insureds": {},
    "Business Information": {},
    "Policy Details": {},
    "Premium Information": {},
    "Lines of Business": {},
    "Contacts": [],
    "Carrier Information": {},
    "Underwriter Information": {},
    "Premises/Locations": [],
    "Additional Interests": [],
    "Prior Insurance": [],
    "Loss History": [],
    "General Information": {},
    "Signatures": {},
    "Remarks": "",
}

EXTRACTION_PROMPT = """
Extract the information actually visible in this ACORD 125 commercial insurance
application. Do not guess or invent values. Use "N/A" for unavailable scalar
values and [] for lists with no entries. Return only one JSON object with exactly
these top-level sections and the field names listed below:

{
  "Document Information": {
    "Document Title": "", "ACORD Form": "", "Form Version": "", "Form Date": ""
  },
  "Agency Information": {
    "Agency Name": "", "Agency Address": "", "Agency Code": "",
    "Agency Subcode": "", "Agency Main Phone": "", "Agency Main Email": "",
    "Agency Fax": ""
  },
  "Transaction Details": {
    "Transaction Type": "", "Policy Status": "", "Submission Date": "",
    "Submission Time": "", "Transaction Notes": ""
  },
  "Named Insureds": {
    "First Named Insured": {
      "Legal Name": "", "Mailing Address": "", "FEIN": "", "SSN": "",
      "Phone": "", "Website": ""
    },
    "Other Named Insureds": [{
      "Legal Name": "", "Mailing Address": "", "FEIN": "", "SSN": "",
      "Phone": "", "Website": ""
    }],
    "Organization Type": ""
  },
  "Business Information": {
    "Nature of Business": "", "Date Business Started": "",
    "Business Description": ""
  },
  "Policy Details": {
    "Proposed Effective Date": "", "Proposed Expiration Date": "",
    "Billing Plan": "", "Method of Payment": ""
  },
  "Premium Information": {
    "policy_premium": "", "deposit_premium": "", "minimum_premium": "",
    "reasoning": "", "premium_analysis": {
      "stated_total": "", "calculated_sum": "", "matches": false
    },
    "individual_line_premiums": [{"line": "", "premium": ""}]
  },
  "Lines of Business": {},
  "Contacts": [{
    "Contact Type": "", "Name": "", "Phone": "", "Email": "",
    "Title": "", "Department": ""
  }],
  "Carrier Information": {
    "Carrier Name": "", "Policy Number": "", "NAIC Code": "",
    "Program Name": "", "Carrier Contact": "", "Carrier Phone": "",
    "Carrier Email": ""
  },
  "Underwriter Information": {
    "Underwriter Name": "", "Underwriter Office": "",
    "Underwriting Company": "", "Underwriter Phone": "",
    "Underwriter Email": "", "Underwriter Address": ""
  },
  "Premises/Locations": [{
    "Location Number": "", "Building Number": "", "Full Address": "",
    "Inside City Limits": "", "Outside City Limits": "",
    "Owner/Tenant": "", "Area Leased": "", "Occupied Area (sq ft)": "",
    "Total Area (sq ft)": "", "Open to Public Area (sq ft)": "",
    "Annual Revenues": "", "Number of Employees": "",
    "Operations Description": ""
  }],
  "Additional Interests": [{
    "Interest Type": "", "Name": "", "Address": "", "Item Reference": "",
    "Building Reference": "", "Evidence Flag": "", "Certificate Flag": "",
    "Bill Flag": "", "Effective Date": "", "Expiration Date": "",
    "Lien Number": "", "Loan Number": ""
  }],
  "Prior Insurance": [{
    "Year": "", "Line/Category": "", "Carrier": "", "Policy Number": "",
    "Effective Date": "", "Expiration Date": "", "Premium": ""
  }],
  "Loss History": [{
    "Line/Type": "", "Description": "", "Occurrence Date": "",
    "Claim Date": "", "Paid Amount": "", "Reserved Amount": "",
    "Subrogation": "", "Claim Open": "", "Total Amount": "",
    "Years Covered": ""
  }],
  "General Information": {
    "Safety Program": "", "OSHA Compliance": "", "Safety Manual": "",
    "Safety Meetings": "", "Hazardous Exposures": "",
    "Foreign Operations": "", "Cancellations/Non-renewals": "",
    "Bankruptcy/Judgments/Liens": "", "Drones": "", "Other Insurance": "",
    "Trust Placement": "", "Regulatory Acknowledgments": "",
    "State Fraud Notices": "", "Applicant Initials": ""
  },
  "Signatures": {
    "Producer Name": "", "Producer Signature": "", "Producer NPN": "",
    "Producer License": "", "Applicant Signature": "", "Applicant Date": "",
    "Signature Date": ""
  },
  "Remarks": ""
}

For "Lines of Business", use each line name as a key and an object with
"Selected", "Limits", and "Premium" fields as its value. Do not return markdown
or explanatory text. For premium reasoning, provide a short summary only; do not
include private chain-of-thought.
"""


def extract_entities(file_bytes: bytes, mime_type: str) -> str:
    """Send an uploaded PDF or image to Gemini and return frontend-compatible JSON."""
    api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GeminiConfigurationError(
            "GEMINI_API_KEY is not set. Add it to the .env file before extracting."
        )

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
            EXTRACTION_PROMPT,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )
    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    entities = json.loads(response.text)
    if not isinstance(entities, dict):
        raise ValueError("Gemini returned JSON with an unexpected top-level type.")

    for section, default in ENTITY_SCHEMA.items():
        entities.setdefault(section, default)
    for section, default in ENTITY_SCHEMA.items():
        if not isinstance(entities[section], type(default)):
            raise ValueError(f"Gemini returned an invalid '{section}' section.")

    return json.dumps(entities, indent=2)