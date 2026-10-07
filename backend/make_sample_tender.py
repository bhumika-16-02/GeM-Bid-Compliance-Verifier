import fitz  # this is PyMuPDF

TEXT = """GOVERNMENT e-MARKETPLACE - BID DOCUMENT (SAMPLE)

Tender Title: Supply of 100 Laptops
Tender Number: GEM/2026/B/001

ELIGIBILITY AND DOCUMENTS REQUIRED

1. The bidder must submit a valid PAN card.
2. The bidder must submit a valid GST registration certificate.
3. The bidder must submit a Udyam (MSME) registration certificate.
4. The bidder must submit an OEM authorization letter for the quoted laptops.
5. The bidder must declare local content of at least 50 percent.
6. The bidder must not be debarred or blacklisted by any government body.

Delivery within 30 days of order. Payment within 30 days of delivery.
"""

doc = fitz.open()
page = doc.new_page()
page.insert_textbox(fitz.Rect(50, 50, 545, 790), TEXT, fontsize=11)
doc.save("../data/demo_docs/tender.pdf")
print("Saved ../data/demo_docs/tender.pdf")