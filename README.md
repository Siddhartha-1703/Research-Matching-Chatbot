# Research Matching Chatbot (CLI)

Terminal-first prototype to connect students and professors with faculty project matches, implemented as a CLI. Includes scaffolding for ChromaDB-backed RAG search, mock Tavily and Semantic Scholar wrappers, and a loader for mock faculty profiles.

Quick start

1. Create and activate a Python environment (recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Populate ChromaDB with mock profiles:

```bash
python scripts/load_profiles.py --store chroma
```

4. Run the CLI:

```bash
python src/cli.py --mode student
```

Notes: Some services (Tavily, Semantic Scholar) are implemented as lightweight wrappers/mocks; replace with real API integrations and keys as needed.

Usage examples

- Populate the vector store (uses ChromaDB if installed, otherwise in-memory fallback):

```bash
python scripts/load_profiles.py --dir data/faculty
```

- Run the CLI in student mode and search for faculty by topic:

```bash
python src/cli.py --mode student
# Then enter: "natural language processing" or "NLP"
```

- Show details for a matched faculty member by selecting its number when prompted. The agent will always ask for confirmation before making or logging final decisions (e.g., assigning a student or sending an email).

- Run the CLI in professor mode for trend lookups:

```bash
python src/cli.py --mode professor
# Then enter: "trends in reinforcement learning"
```

- Run the scripted demo to review a sample Professor + Student conversation, including saved gap analysis and logged student interest:

```bash
python scripts/demo_conversation.py
```

Developer notes

- The project implements a RAG-style search over mock faculty profiles using `src/chromadb_client.py`. If `chromadb` is not installed the code falls back to an in-memory embedding search using `sentence-transformers`.
- `src/search.py` provides `find_faculty()`, `get_faculty_detail()`, and `suggest_collaborators()` which applies a simple availability-adjusted similarity score.
- Replace `src/tavily.py` and `src/semantic_scholar.py` with real API wrappers when ready.

Next steps

- Add real API keys and endpoints for Tavily and Semantic Scholar.
- Add Gmail OAuth flow instead of SMTP/password for extra security (recommended for production).

- Email setup

To enable sending summary emails from the CLI, set the following environment variables in your shell (do NOT commit credentials into source control):

```bash
export EMAIL_USER=rendlavishnutej@gmail.com
export EMAIL_PASS=your_smtp_password_or_app_password
# Optional (defaults shown):
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
```

On Windows PowerShell use `$env:EMAIL_USER = 'rendlavishnutej@gmail.com'` etc.

The CLI will prompt for confirmation before sending any email and will send to the recipient you provide (default: `rendlavishnutej@gmail.com`) when you confirm from the student flow.

- Optional: build a small Streamlit or Gradio UI after terminal flow is stable.

Printing and logging outputs

To always print detailed outputs (including email body) and save them to a log file, run:

```bash
py src/cli.py --mode student --print-output --log-file output.log
```

This prints match details and any email contents to the console and appends the same to `output.log`.


Beta package

I prepared a beta bundle you can create locally with:

```bash
py scripts/build_beta.py
```

The bundle will be written to `dist/research-matcher-0.1.0-beta.zip`.

Recording the demo

To record the demo as a video, use your preferred screen-recording tool (OBS Studio, Windows Game Bar, etc.) while running the interactive CLI or the demo script. The repository includes `outputs/transcript.txt` and `outputs/transcript.html` which you can present or open while recording.


