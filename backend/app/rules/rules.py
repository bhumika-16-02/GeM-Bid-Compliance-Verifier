RULES = {
    "PAN": {
        "description": "Valid PAN card of the bidder",
        "mandatory": True,
        "weight": 15,
    },
    "GST": {
        "description": "Valid GST registration certificate",
        "mandatory": True,
        "weight": 20,
    },
    "UDYAM": {
        "description": "Udyam (MSME) registration certificate",
        "mandatory": True,
        "weight": 15,
    },
    "OEM": {
        "description": "OEM authorization letter",
        "mandatory": True,
        "weight": 20,
    },
    "LOCAL_CONTENT": {
        "description": "Local content of at least 50%",
        "mandatory": True,
        "weight": 20,
    },
    "BLACKLIST": {
        "description": "Bidder must not be debarred or blacklisted",
        "mandatory": True,
        "weight": 10,
    },
}