{
  "tender_id": "T-001",
  "title": "Supply of 100 Laptops",
  "requirements": [
    { "id": "R1", "text": "Valid PAN card of the bidder", "type": "PAN", "mandatory": true },
    { "id": "R2", "text": "Valid GST registration certificate", "type": "GST", "mandatory": true },
    { "id": "R3", "text": "Udyam (MSME) registration certificate", "type": "UDYAM", "mandatory": true },
    { "id": "R4", "text": "OEM authorization letter", "type": "OEM", "mandatory": true },
    { "id": "R5", "text": "Local content of at least 50%", "type": "LOCAL_CONTENT", "mandatory": true },
    { "id": "R6", "text": "Bidder must not be debarred or blacklisted", "type": "BLACKLIST", "mandatory": true }
  ]
}

{
  "bidder_id": "B-001",
  "company_name": "Sunrise Technologies Pvt Ltd",
  "documents": [
    { "doc_type": "PAN", "source_file": "pan.pdf", "confidence": 0.97,
      "fields": { "pan_number": "ABCDE1234F", "name": "Sunrise Technologies Pvt Ltd" } },
    { "doc_type": "GST", "source_file": "gst.pdf", "confidence": 0.94,
      "fields": { "gstin": "29ABCDE1234F1Z5", "legal_name": "Sunrise Technologies Pvt Ltd", "valid_till": "2027-03-31" } },
    { "doc_type": "UDYAM", "source_file": "udyam.pdf", "confidence": 0.91,
      "fields": { "udyam_number": "UDYAM-KA-01-0012345", "category": "Small" } },
    { "doc_type": "OEM", "source_file": "oem.pdf", "confidence": 0.78,
      "fields": { "oem_name": "Dell India", "authorized_for": "Laptops", "valid_till": "2026-12-31" } },
    { "doc_type": "LOCAL_CONTENT", "source_file": "lc.pdf", "confidence": 0.88,
      "fields": { "local_content_percent": "45" } }
  ]
}
{
  "bidder_id": "B-001",
  "tender_id": "T-001",
  "score": 67,
  "risk": "MEDIUM",
  "recommendation": "REVIEW",
  "summary": "4 of 6 requirements passed. Local content is below the required 50%. The OEM letter was read with low confidence and needs a manual check.",
  "checks": [
    { "requirement_id": "R1", "requirement": "Valid PAN card of the bidder", "status": "PASS",
      "evidence": "PAN ABCDE1234F is in valid format and the name matches the company.", "source": "pan.pdf", "rule": "PAN_FORMAT" },
    { "requirement_id": "R2", "requirement": "Valid GST registration certificate", "status": "PASS",
      "evidence": "GSTIN 29ABCDE1234F1Z5 is valid and active until 2027-03-31.", "source": "gst.pdf", "rule": "GST_VALID" },
    { "requirement_id": "R3", "requirement": "Udyam (MSME) registration certificate", "status": "PASS",
      "evidence": "Udyam number found, category Small.", "source": "udyam.pdf", "rule": "UDYAM_PRESENT" },
    { "requirement_id": "R4", "requirement": "OEM authorization letter", "status": "REVIEW",
      "evidence": "OEM name read as 'Dell India' but extraction confidence was only 78%.", "source": "oem.pdf", "rule": "OEM_PRESENT" },
    { "requirement_id": "R5", "requirement": "Local content of at least 50%", "status": "FAIL",
      "evidence": "Declared local content is 45%, below the 50% minimum.", "source": "lc.pdf", "rule": "LOCAL_CONTENT_MIN" },
    { "requirement_id": "R6", "requirement": "Bidder must not be debarred or blacklisted", "status": "PASS",
      "evidence": "GSTIN not found in the debarred list.", "source": "mock_debarred.json", "rule": "NOT_DEBARRED" }
  ]
}