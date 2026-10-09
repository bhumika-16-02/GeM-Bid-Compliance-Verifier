import os

import pymupdf as fitz

TENDER = "Supply of 100 Laptops (GEM/2026/B/001)"


def make_bidder(folder, pan_card, gst_pan, name_pan, name_gst, name_udyam, name_oem,
                addr_gst, addr_udyam, udyam_no, local_pct):
    gstin = "29" + gst_pan + "1Z5"
    docs = {
        "pan.pdf": f"""INCOME TAX DEPARTMENT - GOVT. OF INDIA
PERMANENT ACCOUNT NUMBER CARD (SAMPLE)

Name: {name_pan}
Permanent Account Number: {pan_card}
""",
        "gst.pdf": f"""GOODS AND SERVICES TAX
REGISTRATION CERTIFICATE (SAMPLE)

GSTIN: {gstin}
Legal Name: {name_gst}
Principal Place of Business: {addr_gst}
Valid Till: 31/03/2028
Status: Active
""",
        "udyam.pdf": f"""MINISTRY OF MSME - GOVT. OF INDIA
UDYAM REGISTRATION CERTIFICATE (SAMPLE)

Udyam Registration Number: {udyam_no}
Name of Enterprise: {name_udyam}
Type of Enterprise: Small
Official Address: {addr_udyam}
""",
        "oem.pdf": f"""DELL INDIA PVT LTD
MANUFACTURER AUTHORIZATION LETTER (SAMPLE)

OEM Name: Dell India
Authorized Bidder: {name_oem}
Authorized For: Laptops
Valid Till: 30/06/2027
""",
        "lc.pdf": f"""SELF DECLARATION OF LOCAL CONTENT (SAMPLE)

Bidder: {name_oem}
Tender: {TENDER}

We declare that the local content in the quoted product
is {local_pct} percent.
""",
    }
    os.makedirs(folder, exist_ok=True)
    for filename, text in docs.items():
        doc = fitz.open()
        page = doc.new_page()
        page.insert_textbox(fitz.Rect(50, 50, 545, 790), text, fontsize=12)
        doc.save(f"{folder}/{filename}")
        doc.close()
    print("Saved", folder, "| GSTIN:", gstin)


BLR = "No. 7, MG Road, Bengaluru, Karnataka 560001"
CHN = "No. 12, Anna Salai, Chennai, Tamil Nadu 600002"

# Clean bidder: everything agrees, local content 60%
make_bidder("../data/demo_docs/xyz", "AABCX5678M", "AABCX5678M",
            "XYZ Systems Pvt Ltd", "XYZ Systems Pvt Ltd", "XYZ Systems Pvt Ltd",
            "XYZ Systems Pvt Ltd", BLR, BLR, "UDYAM-KA-03-0067890", 60)

# Flagged bidder: PAN card differs from the PAN inside the GSTIN, a different company
# name on the Udyam certificate, different addresses
make_bidder("../data/demo_docs/flagged", "AABCD1234F", "AABCE9999H",
            "Delta Traders Pvt Ltd", "Delta Traders Pvt Ltd", "Delta Trading Company",
            "Delta Traders Pvt Ltd", BLR, CHN, "UDYAM-KA-03-0099999", 55)