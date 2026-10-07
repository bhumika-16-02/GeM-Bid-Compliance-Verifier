# AI module guide (Member A)

Everything in `backend/app/ai/` and `backend/app/rag/`. Please do not edit those
folders without telling Member A.

**Principle:** the AI reads and explains, plain Python decides. The AI never changes a
status or a score. If the AI is unavailable, every function still returns a result.

## 1. One-time setup

Use Python 3.12 (3.14 is too new for some libraries).

```
cd backend
py -3.12 -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn python-multipart python-dotenv pymupdf google-genai sentence-transformers chromadb sqlmodel
```

Create `backend/.env` (never commit it) with your OWN key from aistudio.google.com
(create the key in a new project):

```
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-flash-latest
```

Build the rule database once (runs locally, no quota used):

```
python -m app.rag.ingest
```

All `python -m ...` commands below run from the `backend` folder with `(venv)` on.

## 2. How the pieces connect (API flow)

```
POST /tender/upload   -> extract_tender -> saved in the store
POST /bidder/upload   -> extract_bidder -> saved in the store (ids B-001, B-002, ...)
GET  /report/{id}     -> full_report (engine + explain) for an uploaded bidder
```

- Upload the tender first, then the bidder, then ask for the report.
- The store (`app/ai/store.py`) lives in memory. **A server restart empties it** (this
  includes every file save while `uvicorn --reload` is running), so upload again.
- `GET /report/B-001?use_ai=false` skips the AI summary and uses a template sentence
  (fast, no quota).
- `PUT /bidder/{id}/fields` saves the officer's corrected documents into the store, so
  the next report uses the corrected values.
- Numeric ids (from `POST /bidders`) still use Member B's original database report.

## 3. Functions you can call

### extract_tender(source, tender_id="T-001")
`from app.ai.extract_tender import extract_tender`
`source` is a PDF path or PDF bytes (for uploads: `await file.read()`).
Returns the tender JSON from the API contract: `tender_id`, `title`, `requirements`
(each with `id`, `text`, `type`, `mandatory`). Types: PAN, GST, UDYAM, OEM,
LOCAL_CONTENT, BLACKLIST, OTHER.

### extract_bidder(files, bidder_id="B-001")
`from app.ai.extract_bidder import extract_bidder`
`files` is a list of `(file_name, path_or_bytes)`. ONE AI call for all documents. The
documents are sorted by file name first, so the upload order does not matter and the
cache is reused.
Returns the bidder JSON from the contract: `bidder_id`, `company_name`, `documents`.
Each document has `doc_type`, `source_file`, `confidence` and `fields`.

- `confidence` is computed by our code: the share of fields that have a valid format AND
  really appear in the PDF text. It is not the AI's own guess.
- Extra fields beyond the contract examples: `address` (GST, Udyam),
  `enterprise_name` (Udyam), `bidder_name` (OEM, local content).
- A document that cannot be read comes back as `doc_type: "OTHER"` with confidence 0.

### retrieve(query, n=3, req_type=None) and get_rule(rule_id)
`from app.rag.retrieve import retrieve, get_rule`
`retrieve` searches the 20 rules in `data/kb/rules.json` by meaning. `get_rule("LC-02")`
fetches one rule by exact id. Both return `rule_id`, `title`, `text`, `source`
(`retrieve` also returns `score`). Use `get_rule` when you already know which check ran.

### build_report(bidder, tender, engine_result, use_ai=True)
`from app.ai.explain import build_report`
Takes the two JSONs above plus the result of `calculate_compliance`. Returns the report
from the contract (`score`, `risk`, `recommendation`, `summary`, `checks`) plus two extra
fields:

- every check has `citation` (`rule_id`, `title`, `source`)
- `cross_checks`: PAN inside GSTIN, same company name, same address
  (each PASS or REVIEW)

Status rules: the engine's true/false gives PASS/FAIL; a PASS with confidence below 0.9
becomes REVIEW. `recommendation` is APPROVE (nothing flagged) or REVIEW. It is never
REJECT: only the Procurement Officer disqualifies a bidder.
`summary` is written by the AI (one call, cached). On any AI error a template sentence
is used.

### full_report(bidder, tender, use_ai=True)
`from app.ai.pipeline import full_report`
One call for the whole pipeline: converts the bidder JSON into engine inputs, runs
`calculate_compliance`, then `build_report`. The simulated blacklist reads
`data/mock_debarred.json` (`{"debarred": ["<GSTIN or PAN>"]}`).

### Store (app/ai/store.py)
`save_tender`, `get_tender`, `next_bidder_id`, `save_bidder`, `get_bidder`,
`update_documents`. In-memory only.

### explain_compliance(result)
Kept for backward compatibility: one-line text from an engine result.

## 4. Test each module

```
python -m app.ai.llm                 # 1 AI call, tests the key and model
python -m app.ai.extract_tender      # reads data/demo_docs/tender.pdf
python -m app.ai.extract_bidder      # reads the 5 PDFs in data/demo_docs/abc/
python -m app.rag.retrieve           # 4 sample rule searches
python -m app.ai.explain --no-ai     # full report, template summary
python -m app.ai.explain             # same, with the AI summary
python -m app.ai.pipeline            # prints the engine inputs for the demo bidder
python -m test_bidder ../data/demo_docs/flagged --debar   # blacklist + cross-checks fire
python -m test_bidder ../data/demo_docs/xyz               # clean bidder
```

Demo bidders (all synthetic), in `data/demo_docs/`:

- `abc/`: ABC Technologies, declares 42% local content against the tender's 50%
  (the planted flaw). Expected: score 80, MEDIUM, REVIEW.
- `xyz/`: XYZ Systems, everything consistent, 60% local content. Expected: all pass.
- `flagged/`: PAN mismatch with the GSTIN, different company name on the Udyam
  certificate, different addresses. Use `--debar` to put its GSTIN on a temporary
  blacklist.

Regenerate PDFs with `python make_sample_tender.py`, `python make_sample_bidder.py` and
`python make_more_bidders.py` (run from `backend`).

## 5. Cache and quota

- Every AI answer is saved in `data/cache/` (ignored by Git, so it is per laptop).
  The same question never costs a second call. The cache key includes the model name,
  so do not change `GEMINI_MODEL` after filling the cache.
- The free tier has a small daily limit per model per key (about 20 requests in our
  tests; check ai.dev/rate-limit). Failed attempts can count too. Do not share keys, and
  run each AI command once.
- Before a demo, run the full flow once on the presenting laptop so the cache is filled.

## 6. Common errors

| Message | Meaning | Fix |
|---|---|---|
| `No module named 'app'` | wrong folder | `cd backend` first |
| `No module named 'sqlmodel'` | library missing | `pip install sqlmodel python-multipart` |
| `GEMINI_API_KEY is missing` | no `.env` | create `backend/.env` |
| `503 UNAVAILABLE` / "AI busy, retrying" | Google is overloaded | wait, it retries by itself |
| `Daily free quota used up` | 429 per-day limit | change `GEMINI_MODEL`, use a key from a new project, or wait |
| `Collection gem_rules does not exist` | rule database not built | `python -m app.rag.ingest` |
| `No text found in this PDF` | scanned image PDF | not supported (digital PDFs only) |
| `citation: null` | rule database missing | run ingest |
| `{"error": "Bidder not found"}` or `Upload a tender first` | the store is empty after a restart | upload the tender and bidder again |

## 7. Honest limits

- Digital PDFs only; no OCR for scanned images or handwriting.
- Tested on clean synthetic documents; real tenders are messier and the prompts may need
  tuning.
- The rule knowledge base is simplified. Entries marked "Prototype policy" are our own
  rules, not official text. Check official sources before relying on them.
- The blacklist is simulated (`data/mock_debarred.json`); no live GST, Udyam, MCA or
  other government APIs are used.
- Uploads are kept in memory only (lost on restart).
- The system recommends. The Procurement Officer decides.