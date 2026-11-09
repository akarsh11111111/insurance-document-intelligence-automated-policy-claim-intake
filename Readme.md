# Insurance Document Intelligence for Automated Policy and Claim Intake

An insurance operations workspace for automated policy and claim intake. Upload an ACORD 125 form or supported image to extract policyholder, coverage, location, and loss details with Gemini. Review the structured results in a Streamlit dashboard backed by FastAPI.

## Features

- **Complete ACORD 125 Processing**: Extracts all major sections from commercial insurance applications:
  - **Document Information**: Form version, title, and metadata
  - **Agency Information**: Agency details and codes (agency-level only)
  - **Transaction Details**: Transaction type, policy status (new/renewal), submission info
  - **Carrier Information**: Carrier name, policy number, NAIC code, program details
  - **Underwriter Information**: Underwriter name, office, company, contact details
  - **Contacts**: Individual contacts organized by type (Sales, Support, Service, etc.) with dropdown interface
  - **Named Insureds**: First named insured and additional insureds with full business details
  - **Business Information**: Nature of business, operations, relationships
  - **Policy Details**: Effective dates, billing plans, payment methods
  - **Premium Information**: Stated and calculated total verification
  - **Lines of Business**: Property, liability, auto, umbrella, and specialty lines
  - **Premises/Locations**: Detailed location information with square footage and revenues
  - **Additional Interests**: Mortgagees, loss payees, and other interested parties
  - **Prior Insurance**: Historical carrier and premium information
  - **Loss History**: Claims history with amounts and status
  - **General Information**: Safety programs, regulatory compliance, Q&A sections
  - **Signatures**: Producer and applicant signature details

- **Premium Analysis**:
  - Brief explanation of extracted premium totals
  - Displays stated totals and available comparison values for review
  - Individual line premium breakdown and analysis
  - Deposit and minimum premiums included when found in the document

- **Intelligent Entity Extraction**:
  - Schema-guided document extraction
  - Structured JSON output for review and integration
  - Clear API errors for missing configuration or failed requests

- **Gemini Document Processing**:
  - Sends PDF and image uploads directly to Gemini for visual and text extraction
  - Returns structured JSON matching the Streamlit frontend's expected schema

- **Upload Support**: PDF and image formats
- **Professional Claim Review**: Summary metrics and organized tabs for policy, coverage, locations, losses, and contacts

## Project Structure

```
.
├── api/                  # FastAPI routes
│   └── routes.py
├── services/
│   └── entity_extraction.py  # Gemini document and entity extraction
├── config.py             # Loads Gemini settings from .env
├── main.py               # FastAPI app entry point
├── streamlit_app.py      # Streamlit frontend
├── requirements.txt      # Python dependencies
├── .env                  # Gemini API key (not committed)
└── Readme.md             # Project documentation
```

## Setup

1. **Clone the repository**
   ```sh
   git clone https://github.com/akarsh11111111/insurance-document-intelligence-automated-policy-claim-intake.git
   cd insurance-document-intelligence-automated-policy-claim-intake
   ```
2. **Create Virtual Environment**
   ```sh
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Create a `.env` file with your Gemini API key:
     ```
     GEMINI_API_KEY=your_gemini_api_key
     GEMINI_MODEL=gemini-3.8-flash
     ```

   `GEMINI_MODEL` is optional; it defaults to `gemini-3.8-flash`.

5. **Run the backend (optional)**
   ```sh
   uvicorn main:app --reload
   ```

   The Streamlit dashboard can call Gemini directly. Set `API_URL` only when you want it to use a separately running FastAPI server.

6. **Run the frontend**
   ```sh
   streamlit run streamlit_app.py
   ```

## Free deployment to Streamlit Community Cloud

The dashboard calls Gemini directly, so the free Community Cloud deployment does not require a separate FastAPI service.

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
2. Select **Create app**, then choose this repository, the `main` branch, and `streamlit_app.py`.
3. In **Advanced settings → Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key"
   ```
4. Deploy the app. Keep the key in Streamlit Secrets; do not commit it to GitHub.

Streamlit Community Cloud stores app secrets separately from the repository. See the [official secrets guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).

## Sample ACORD 125 Forms

Sample documents are intentionally kept out of the public GitHub repository. Use a document you are authorized to process for local testing.

## Usage

- Open the Streamlit app in your browser.
- Upload an ACORD 125 PDF or PNG/JPEG/WEBP image.
- View comprehensive extracted entities organized by sections.
- Review premium totals and their comparison.
- Review all business details, locations, and insurance lines.

## API Endpoint

- `POST /extract`
  Upload an ACORD 125 form and receive extracted entities as structured JSON.

## Key ACORD 125 Entities Extracted

The system extracts comprehensive information including:
- Document title and ACORD form/version
- Agency name, address, code/subcode (agency-level information only)
- Individual contacts organized by type (Sales, Support, Service, etc.) with names, phones, emails
- Carrier name, policy number, NAIC code, program details
- Underwriter name, office, company, contact information
- Transaction type and policy status (new business, renewal, etc.)
- Status of transaction, submission date/time
- First Named Insured: legal name, mailing address, FEIN/SSN, NAICS/SIC/GL code, phone, website
- Other Named Insureds list with the same fields
- Organization type (corp/LLC/partnership/individual/sub‑S/trust/JV/not‑for‑profit)
- Nature of business / description of operations; date business started
- Parent/subsidiary relationships and percent owned; other ventures (Y/N + description)
- Proposed effective and expiration dates
- Billing plan, payment plan, method of payment, audit flag/basis
- Premium fields: policy premium, deposit, minimum, and total comparison
- Lines of business selected (property, CGL, auto, umbrella, crime, B&M, inland marine, garage, truckers, cyber, etc.) with limits/premiums
- Contacts: type, name, primary/secondary phones and emails
- Premises/locations: loc #, bld #, full address, inside/outside city limits, owner/tenant, any area leased, occupied/total/open‑to‑public area (sq ft), annual revenues, employees, operations description
- Additional interests: interest type, name/address, item/location/building reference, evidence/certificate/bill flags, dates, lien/loan numbers
- Prior carriers by year and line/category: carrier, policy number, effective/expiration dates, premium
- Loss history: line/type/description, occurrence date, claim date, paid, reserved, subrogation Y/N, claim open Y/N, totals/years covered
- General information Q&A: safety program/OSHA/manual/meetings, hazardous exposures, foreign operations, cancellations/non‑renewals, bankruptcy/judgments/liens, drones, other insurance, trust placement
- Regulatory acknowledgments and state fraud notices; applicant initials where applicable
- Signatures: producer name/signature/NPN/license, applicant signature/date
- Remarks/processing instructions and list of attached supplements

## License

MIT License

---

**Note:** You need a valid Gemini API key in `GEMINI_API_KEY`. Set `GEMINI_MODEL` to another supported model if needed.
