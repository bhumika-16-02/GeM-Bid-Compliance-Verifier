import os

import fitz  # PyMuPDF

OUT_DIR = "../data/demo_docs/abc"

COMPANY = "ABC Technologies Pvt Ltd"
ADDRESS = "No. 24, 1st Main Road, Peenya Industrial Area, Bengaluru, Karnataka 560058"
PAN = "AABCA4821K"
GSTIN = "29" + PAN + "1Z5"  # state code 29 + PAN + entity no. + Z + check digit

DOCS = {
    "pan.pdf": f"""INCOME TAX DEPARTMENT - GOVT. OF INDIA
PERMANENT ACCOUNT NUMBER CARD (SAMPLE)

Name: {COMPANY}
Permanent Account Number: {PAN}
Date of Incorporation: 14/08/2015
""",
    "gst.pdf": f"""GOODS AND SERVICES TAX
REGISTRATION CERTIFICATE (SAMPLE)

GSTIN: {GSTIN}
Legal Name: {COMPANY}
Principal Place of Business: {ADDRESS}
Date of Registration: 01/07/2017
Valid Till: 31/03/2028
Status: Active
""",
    "udyam.pdf": f"""MINISTRY OF MSME - GOVT. OF INDIA
UDYAM REGISTRATION CERTIFICATE (SAMPLE)

Udyam Registration Number: UDYAM-KA-03-0045821
Name of Enterprise: {COMPANY}
Type of Enterprise: Small
Official Address: {ADDRESS}
Date of Registration: 12/03/2021
""",
    "oem.pdf": f"""DELL INDIA PVT LTD
MANUFACTURER AUTHORIZATION LETTER (SAMPLE)

This is to certify that {COMPANY} is an authorized
reseller of Dell laptops in India.

OEM Name: Dell India
Authorized Bidder: {COMPANY}
Authorized For: Laptops
Valid Till: 30/06/2027
""",
    "lc.pdf": f"""SELF DECLARATION OF LOCAL CONTENT (SAMPLE)

Bidder: {COMPANY}
Tender: Supply of 100 Laptops (GEM/2026/B/001)

We declare that the local content in the quoted product
is 42 percent.

Authorized Signatory: R. Kumar, Director
""",
}

os.makedirs(OUT_DIR, exist_ok=True)
for filename, text in DOCS.items():
    doc = fitz.open()
    page = doc.new_page()
    page.insert_textbox(fitz.Rect(50, 50, 545, 790), text, fontsize=12)
    doc.save(f"{OUT_DIR}/{filename}")
    doc.close()
    print("Saved", filename)