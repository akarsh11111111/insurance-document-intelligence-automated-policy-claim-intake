# Insurance Document Intelligence: ACORD 125 Features

## Overview
This project supports policy and claim intake by extracting structured information from ACORD 125 Commercial Insurance Application forms. The ACORD 125 is a business insurance application containing information about companies seeking commercial insurance coverage.

## Key Features Implemented

### 1. Comprehensive Entity Extraction
The system extracts all major sections of an ACORD 125 form:

#### Document Information
- Document title and ACORD form number
- Form version and edition date
- Form metadata

#### Agency Information
- Agency name and address
- Agency codes and subcodes
- Contact person details
- Phone numbers and email addresses
- Fax information

#### Transaction Details
- Transaction status (new, renewal, etc.)
- Submission date and time
- Insurance carrier information
- Program details and NAIC codes
- Underwriter office and name

#### Named Insureds
- **First Named Insured**: Complete business details including:
  - Legal name and mailing address
  - FEIN (Federal Employer Identification Number)
  - SSN (for individuals)
  - NAICS/SIC/GL industry codes
  - Phone and website information
- **Other Named Insureds**: Additional insured parties
- **Organization Type**: Corporation, LLC, partnership, individual, etc.

#### Business Information
- Nature of business and detailed operations description
- Date business was established
- Parent/subsidiary relationships and ownership percentages
- Other business ventures and joint ventures

#### Policy Details
- Proposed effective and expiration dates
- Billing plan (annual, semi-annual, quarterly, monthly)
- Payment plan and method of payment
- Audit flags and basis information

### 2. Advanced Premium Analysis
The premium summary can help reviewers compare extracted amounts:

#### Premium Extraction with Reasoning
- Identifies all monetary amounts in the document
- Organizes premium amounts and breakdowns
- Compares stated totals against calculated sums
- Cross-verifies stated totals against calculated sums
- Provides a brief summary for reviewer context

#### Premium Components
- Policy premium (total)
- Deposit premium
- Minimum premium
- Individual line premiums by coverage type

#### Verification System
- Compares stated totals with calculated sums
- Flags discrepancies for review
- Provides transparency in premium analysis

### 3. Lines of Business Coverage
Comprehensive extraction of insurance coverage lines:

#### Supported Coverage Types
- Property Insurance
- General Liability (CGL)
- Commercial Auto
- Umbrella/Excess Liability
- Crime Insurance
- Boiler & Machinery
- Inland Marine
- Garage Coverage
- Truckers Insurance
- Cyber Liability Insurance

#### Coverage Details
- Selection status (selected/not selected)
- Coverage limits
- Premium amounts
- Deductible information

### 4. Location and Premises Information
Detailed extraction of business locations:

#### Location Details
- Location and building numbers
- Complete addresses
- Inside/outside city limits designation
- Owner/tenant status
- Leased area information
- Square footage (occupied, total, open to public)
- Annual revenues per location
- Employee counts
- Operations descriptions

### 5. Additional Interests
Comprehensive tracking of interested parties:

#### Interest Types
- Mortgagees
- Loss payees
- Additional insureds
- Certificate holders

#### Interest Details
- Names and addresses
- Item/location/building references
- Evidence and certificate requirements
- Billing flags and dates
- Lien and loan numbers

### 6. Historical Information
Complete insurance and loss history:

#### Prior Insurance
- Previous carriers by year and line
- Policy numbers and dates
- Premium amounts
- Coverage categories

#### Loss History
- Loss descriptions by line of business
- Occurrence and claim dates
- Paid and reserved amounts
- Subrogation information
- Open/closed claim status
- Multi-year loss summaries

### 7. Regulatory and Compliance
Extraction of regulatory information:

#### General Information Q&A
- Safety programs and OSHA compliance
- Safety manuals and meeting schedules
- Hazardous exposures
- Foreign operations
- Cancellation/non-renewal history
- Bankruptcy, judgments, and liens
- Drone usage
- Other insurance coverage
- Trust placement information

#### Regulatory Compliance
- State fraud notices
- Regulatory acknowledgments
- Required applicant initials

### 8. Signature Information
Complete signature tracking:

#### Producer Information
- Producer name and signature status
- National Producer Number (NPN)
- License information

#### Applicant Information
- Applicant signature status
- Signature dates
- Authorization details

### 9. Remarks and Instructions
- Processing instructions
- Special remarks
- List of attached supplements
- Additional documentation references

## Technical Implementation

### Gemini Extraction
- **Direct document input**: Gemini analyzes supported PDF and image uploads
- **Schema-guided output**: A structured JSON response organizes extracted sections
- **Error handling**: API configuration and extraction failures are reported explicitly
- **Human review**: Extracted values are presented for review and are not guaranteed correct

### Premium Review
Premium values are extracted from the document and returned for reviewer comparison:

1. **Extract stated amounts**: Identify policy, deposit, minimum, and line premiums
2. **Capture available totals**: Preserve stated and model-calculated comparison values
3. **Review results**: Confirm amounts against the source form before use

### Web Interface Features
- **Claim summary**: High-level insured, coverage, location, and loss metrics
- **Review tabs**: Separate policy, exposure, contact, and raw JSON views
- **Download**: Export the extracted JSON for downstream review
- **Responsive layout**: Business-focused dashboard for intake workflows

## Benefits

### For Insurance Professionals
- **Complete Data Extraction**: No manual data entry required
- **Premium Verification**: Automatic calculation checking
- **Structured Output**: Ready for system integration
- **Reviewer Control**: Extracted details are available for inspection before downstream use

### For Underwriters
- **Comprehensive View**: All business details in one place
- **Risk Assessment**: Complete location and operations information
- **Historical Data**: Prior insurance and loss history
- **Compliance Check**: Regulatory requirement tracking

### For Agencies
- **Efficient Processing**: Automated form processing
- **Quality Control**: Built-in verification systems
- **Client Management**: Complete insured information
- **Documentation**: Systematic data organization

## Usage Scenarios

1. **New Business Processing**: Extract complete application data for new accounts
2. **Renewal Analysis**: Compare current vs. prior year information
3. **Risk Assessment**: Analyze business operations and loss history
4. **Premium Review**: Inspect extracted premium amounts and breakdowns
5. **Compliance Monitoring**: Track regulatory requirements and signatures
6. **Data Migration**: Convert paper forms to digital systems

This comprehensive ACORD 125 processing system transforms complex commercial insurance applications into structured, actionable data while maintaining accuracy and providing transparency in the extraction process.