# AI module guide (Member A)

Everything in `backend/app/ai/` and `backend/app/rag/`. Please do not edit those
folders; ask Member A if you need a change.

**Principle:** the AI reads and explains, plain Python decides. The AI never changes a
status or a score. If the AI is unavailable, every function still returns a result.

## 1. One-time setup

Use Python 3.12 (3.14 is too new for some libraries).

```
cd backend
py -3.12 -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn python-multipart python-dotenv pymupdf google-genai sentence-transformers chromadb
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

## 2. Functions you can call

### extract_tender(source, tender_id="T-001")
`from app.ai.extract_tender import extract_tender`
`source` is a PDF path or PDF bytes (for uploads: `await file.read()`).
Returns the tender JSON from the API contract: `tender_id`, `title`, `requirements`
(each with `id`, `text`, `type`, `mandatory`). Types: PAN, GST, UDYAM, OEM,
LOCAL_CONTENT, BLACKLIST, OTHER.

### extract_bidder(files, bidder_id="B-001")
`from app.ai.extract_bidder import extract_bidder`
`files` is a list of `(file_name, path_or_bytes)`. ONE AI call for all documents.
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
from the contract (`score`, `risk`, `recommendation`, `summary`, `checks`) plus two extra fields:

- every check has `citation` (`rule_id`, `title`, `source`)
- `cross_checks`: PAN inside GSTIN, same company name, same address
  (each PASS or REVIEW)

Status rules: the engine's true/false gives PASS/FAIL; a PASS with confidence below 0.9
becomes REVIEW. `recommendation` is APPROVE (nothing flagged) or REVIEW. It is never
REJECT: only the Procurement Officer disqualifies a bidder.
`summary` is written by the AI (one call, cached). On any AI error a template sentence is used.

### full_report(bidder, tender, use_ai=True)
`from app.ai.pipeline import full_report`
One call for the whole pipeline: converts the bidder JSON into engine inputs, runs
`calculate_compliance`, then `build_report`. The simulated blacklist reads
`data/mock_debarred.json` (`{"debarred": ["<GSTIN or PAN>"]}`).

### explain_compliance(result)
Kept for backward compatibility: one-line text from an engine result.

## 3. Test each module

```
python -m app.ai.llm                 # 1 AI call, tests the key and model
python -m app.ai.extract_tender      # reads data/demo_docs/tender.pdf
python -m app.ai.extract_bidder      # reads the 5 PDFs in data/demo_docs/abc/
python -m app.rag.retrieve           # 4 sample rule searches
python -m app.ai.explain --no-ai     # full report, template summary, no AI call
python -m app.ai.explain             # same, with the AI summary
python -m app.ai.pipeline            # prints the engine inputs for the demo bidder
```

Demo PDFs are synthetic. Regenerate them with `python make_sample_tender.py` and
`python make_sample_bidder.py` (run from `backend`). The demo bidder ABC Technologies
declares 42% local content against the tender's 50% (the planted flaw).

## 4. Cache and quota

- Every AI answer is saved in `data/cache/` (ignored by Git, so it is per laptop).
  The same question never costs a second call.
- The free tier has a small daily limit per model per key (about 20 requests in our
  tests; check ai.dev/rate-limit). Do not share keys, and run each AI command once.
- Before a demo, run the full flow once on the presenting laptop so the cache is filled.

## 5. Common errors

| Message | Meaning | Fix |
|---|---|---|
| `No module named 'app'` | wrong folder | `cd backend` first |
| `GEMINI_API_KEY is missing` | no `.env` | create `backend/.env` |
| `503 UNAVAILABLE` / "AI busy, retrying" | Google is overloaded | wait, it retries by itself |
| `Daily free quota used up` | 429 per-day limit | change `GEMINI_MODEL`, use a key from a new project, or wait |
| `Collection gem_rules does not exist` | rule database not built | `python -m app.rag.ingest` |
| `No text found in this PDF` | scanned image PDF | not supported (digital PDFs only) |
| `citation: null` | rule database missing | run ingest |

## 6. Honest limits

- Digital PDFs only; no OCR for scanned images or handwriting.
- Tested on clean synthetic documents; real tenders are messier and the prompts may need tuning.
- The rule knowledge base is simplified. Entries marked "Prototype policy" are our own
  rules, not official text. Check official sources before relying on them.
- The blacklist is simulated (`data/mock_debarred.json`); no live GST, Udyam, MCA or
  other government APIs are used.
- The system recommends. The Procurement Officer decides.