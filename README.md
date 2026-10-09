# GeM Bid Compliance Verifier

An AI-assisted tool that checks bidder documents against a tender's requirements and shows the evidence behind every result. **The AI recommends. The Procurement Officer decides.**

> **Note:** This is a student hackathon prototype. It is not an official Government of India or GeM website, and its results are recommendations only. Debarment is checked against a small sample list (`data/mock_debarred.json`).

## What it does

Manually screening bids is slow and hard to audit. This system:

1. **Reads the tender PDF** and extracts the list of requirements.
2. **Reads the bidder's documents** (PAN, GST, Udyam, OEM authorization, local content declaration) and extracts the key fields, with a confidence score for each document.
3. **Lets the officer review and correct** the extracted fields before anything is scored.
4. **Checks every requirement** with a rules engine and produces a PASS, REVIEW or FAIL result with evidence, the source document and the rule applied. Rule text is retrieved from a knowledge base (RAG).
5. **Gives a compliance score and risk level** with a plain-language summary.
6. **Leaves the final decision to the officer**: approve, reject or override, with a written reason required for reject and override.

## Tech stack

| Part | Technology |
|---|---|
| Frontend | React (Vite), plain CSS |
| Backend | Python, FastAPI, SQLModel |
| AI | Google Gemini (`google-genai`) |
| RAG | ChromaDB + sentence-transformers (`all-MiniLM-L6-v2`) |
| PDF reading | PyMuPDF |

## Project structure

```
5sem-mini-proj/
├── backend/
│   ├── requirements.txt
│   ├── .env.example          # copy to .env and add your Gemini key
│   └── app/
│       ├── main.py           # FastAPI app and /decision
│       ├── store.py          # in-memory store linking uploads to reports
│       ├── models.py
│       ├── routes/           # tender, bidder, report endpoints
│       ├── rules/            # rules engine (scoring and checks)
│       ├── ai/               # Gemini calls: extraction, explanations, pipeline
│       └── rag/              # ingest.py and retrieve.py (rules knowledge base)
├── frontend/
│   ├── package.json
│   └── src/
│       ├── api.js            # all backend calls (USE_MOCK flag lives here)
│       ├── pages/            # About, Tender, Bidder, Results
│       ├── components/       # Header, Footer, ScoreCard, CheckTable, ...
│       └── mock/             # sample JSON for running the UI without a backend
├── data/
│   ├── kb/rules.json         # rules knowledge base
│   ├── demo_docs/            # sample tender and bidder PDFs
│   └── mock_debarred.json    # sample debarred-bidders list
├── docs/                     # API contract, demo script
├── tests/
├── CLAUDE.md
└── PROJECT_CONTEXT.md
```

## Prerequisites

- **Git**
- **Python 3.12** (recommended; newer versions can fail to install the AI packages)
- **Node.js 18 or newer** and npm
- A free **Gemini API key** from https://aistudio.google.com/apikey

## Run it locally

You need two terminals: one for the backend and one for the frontend.

### 1. Clone the repository

```bash
git clone https://github.com/bhumika-16-02/5sem-mini-proj.git
cd 5sem-mini-proj
```

### 2. Backend

```bash
cd backend

# create and activate an environment (conda shown; python -m venv also works)
conda create -n gem python=3.12 -y
conda activate gem

pip install -r requirements.txt
```

Create your environment file:

```bash
cp .env.example .env        # Windows: copy .env.example .env
```

Open `backend/.env` and set your key:

```
GEMINI_API_KEY=paste_your_key_here
```

Optionally add `GEMINI_MODEL=<model name>`. If you leave it out, the default in `app/ai/llm.py` is used. **Never commit `.env`.**

Build the rules knowledge base once (the first run downloads a small embedding model, so you need internet):

```bash
python -m app.rag.ingest
```

Start the server:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Check it works by opening http://localhost:8000/docs, which lists every endpoint.

### 3. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Requests to `/api/...` are forwarded to the backend on port 8000 by the Vite proxy in `vite.config.js`.

In `frontend/src/api.js`, set the flag for the mode you want:

```js
export const USE_MOCK = false   // false = use the real backend, true = sample data only
```

### 4. Try the demo

Use the files in `data/demo_docs/`.

1. Open the **Verify a bid** tab and upload `tender.pdf`. Wait 10 to 20 seconds for the AI to extract the requirements.
2. Upload the five bidder PDFs from one of the bidder folders (`abc/`, `xyz/` or `flagged/`) into the matching slots: PAN, GST, Udyam, OEM, Local Content.
3. Review the extracted fields and correct anything that is wrong. Low-confidence documents are flagged.
4. Click **Confirm fields & run compliance check** to see the score, the per-requirement results and the evidence.
5. Approve, reject or override as the Procurement Officer.

Try the different bidder folders to see different outcomes. Answers from the AI are cached in `data/cache/`, so repeating a demo is fast.

## API overview

Full details are in `docs/api_contract.md` and at `/docs` when the backend is running.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/tender/upload` | Upload the tender PDF, returns extracted requirements |
| POST | `/bidder/upload` | Upload bidder documents, returns extracted fields and confidence |
| PUT | `/bidder/{bidder_id}/fields` | Save the officer's corrections |
| GET | `/report/{bidder_id}` | Compliance report: score, risk, checks, evidence, summary |
| POST | `/decision` | Record the officer's decision and reason |

## Troubleshooting

| Problem | Fix |
|---|---|
| `ResolutionImpossible` or build errors during `pip install` | Use Python 3.12 in a clean environment. |
| `No module named 'dotenv'` (or another package) | You are in the wrong environment. Activate the one you installed into, and run `python -m uvicorn ...` from it. |
| `Address already in use` on port 8000 | An earlier server is still running. Stop it (`lsof -i :8000`, then `kill <PID>`). |
| PyTorch or NumPy errors on an Intel Mac | The newest PyTorch does not support Intel Macs. Install `"numpy<2" "transformers==4.44.2" "sentence-transformers==3.0.1" "huggingface_hub<1.0"`. |
| The UI shows the same sample results every time | `USE_MOCK` is still `true` in `frontend/src/api.js`. Set it to `false`. |
| Report says "Bidder not found" | The backend keeps data in memory. After a restart, upload the tender and bidder again. |
| Citations missing from the report | Run `python -m app.rag.ingest` in the backend folder. |
| Gemini quota or key errors | Check `GEMINI_API_KEY` in `backend/.env`, and wait a minute if you hit the free-tier limit. |

## Known limitations

- Uploaded data is stored **in memory**, so restarting the backend clears it.
- Officer decisions are accepted by the API but not yet saved, and there is no audit-log screen yet.
- The debarment check uses a sample list, not a live government source.
- Extraction quality depends on the AI model and the quality of the uploaded PDFs.

## Team workflow

The project was built by a team of three using feature branches and pull requests.

- Never push directly to `main`. Create a branch, push it, and open a pull request.
- Pull `main` before starting new work: `git checkout main && git pull origin main`.
- Never commit `.env`, API keys, `chroma_db/`, or `data/cache/`.

```bash
git checkout -b feature/<your-feature>
git add <files>
git commit -m "feat: <what you changed>"
git push -u origin feature/<your-feature>
```