WEIGHTS = {
    "PAN": 15,
    "GST": 20,
    "Udyam": 15,
    "OEM": 20,
    "Local Content": 20,
    "Blacklist": 10,
}


def check_pan(pan: str | None) -> bool:
    return bool(pan and pan.strip())


def check_gst(gst: str | None) -> bool:
    return bool(gst and gst.strip())


def check_udyam(udyam: str | None) -> bool:
    return bool(udyam and udyam.strip())


def check_oem(oem: str | None) -> bool:
    return bool(oem and oem.strip())


def check_local_content(
    local_content: float | None,
    required_content: float = 50.0,
) -> bool:
    if local_content is None:
        return False

    return local_content >= required_content


def check_blacklist(blacklist_status: bool) -> bool:
    return not blacklist_status


def calculate_compliance(
    pan: str | None,
    gst: str | None,
    udyam: str | None,
    oem: str | None,
    local_content: float | None,
    blacklist_status: bool,
):
    checks = {
        "PAN": check_pan(pan),
        "GST": check_gst(gst),
        "Udyam": check_udyam(udyam),
        "OEM": check_oem(oem),
        "Local Content": check_local_content(local_content),
        "Blacklist": check_blacklist(blacklist_status),
    }

    score = sum(
        WEIGHTS[name]
        for name, passed in checks.items()
        if passed
    )

    failed_checks = [
        name
        for name, passed in checks.items()
        if not passed
    ]

    mandatory_missing = any(
        not checks[name]
        for name in ["PAN", "GST", "Udyam"]
    )

    if score < 60 or mandatory_missing:
        risk = "HIGH"
    elif failed_checks:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {
        "checks": checks,
        "score": score,
        "risk": risk,
        "failed_checks": failed_checks,
    }