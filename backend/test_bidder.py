import json
import os
import sys
import tempfile
from pathlib import Path

import app.ai.pipeline as pipeline
from app.ai.explain import cross_checks
from app.ai.extract_bidder import extract_bidder

folder = sys.argv[1]
pdfs = sorted(f for f in os.listdir(folder) if f.lower().endswith(".pdf"))
bidder = extract_bidder([(f, os.path.join(folder, f)) for f in pdfs])

if "--debar" in sys.argv:
    # Use a temporary debarment list, so the shared data file is not changed.
    gstin = pipeline._field(bidder, "GST", "gstin")
    temp = Path(tempfile.gettempdir()) / "debarred_test.json"
    temp.write_text(json.dumps({"debarred": [gstin]}), encoding="utf-8")
    pipeline.DEBARRED_FILE = temp

print(pipeline.engine_inputs(bidder))
for c in cross_checks(bidder):
    print(c["status"], "-", c["name"], "-", c["evidence"])