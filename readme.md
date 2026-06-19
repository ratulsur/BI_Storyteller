# BI StoryTeller

An AI-powered business-analysis platform that takes a user from a raw business problem all the
way to a finished PowerPoint — defining the problem, generating a questionnaire, collecting and
cleaning data, analyzing it, visualizing insights, and producing a presentation, with an AI chat
assistant throughout. Built end-to-end in Python with Streamlit, Groq/Llama, and PostgreSQL.

## What it does

BI StoryTeller turns the full market-research workflow into a guided, eight-step pipeline. Each
step feeds the next, so a non-technical user can go from "here's my business question" to a
client-ready deck without leaving the app:

```
1. Problem definition   →  2. Variable extraction   →  3. Questionnaire generation
        →  4. Data collection  →  5. Preprocessing  →  6. Analysis
        →  7. Dashboard + PowerPoint  →  8. AI chat insights
```

LLM-powered steps (variable extraction, questionnaire and presentation generation, chat) run on
Groq-hosted Llama models; data collection integrates Google Sheets; analysis and visualization use
pandas, scikit-learn, scipy, and Plotly; and the deck is assembled with python-pptx, including
AI-generated SVG graphics.

## Key features

- **End-to-end pipeline** — problem framing to finished presentation in one guided flow.
- **AI-assisted research design** — automatic variable extraction and questionnaire generation
  from a plain-language business problem.
- **Flexible data collection** — PostgreSQL-backed interactive forms, with Google Sheets and
  CSV/JSON import/export as alternatives.
- **Automated analysis** — cleaning, outlier removal, normalization, encoding, correlation and
  statistical analysis.
- **Interactive dashboards** — Plotly visualizations for distributions, correlations, and trends.
- **One-click presentations** — PowerPoint generation with five professional templates and
  AI-generated SVG imagery.
- **Conversational insights** — a built-in AI chat assistant grounded in the analyzed data.

## Architecture

Modular design with clear separation of concerns under `utils/`, an API layer in `api/`, and
infrastructure/config separated out:

| Layer | Responsibility |
|-------|----------------|
| Frontend | Streamlit multi-page app (`app.py` + sequential workflow pages), session-state context |
| AI integration | `GroqClient` — variable extraction, questionnaire/presentation content, chat (Llama) |
| Data | `DatabaseClient` (PostgreSQL), `DataProcessor` (cleaning/encoding), pandas in-memory |
| Forms | `FormGenerator` — interactive Streamlit forms wired to the database |
| Visualization | `Visualizer` — Plotly charts for distributions, correlations, statistics |
| Presentation | `PresentationGenerator` (python-pptx) + `ImageGenerator` (AI SVG graphics) |
| Integrations | Google Sheets / Drive (gspread, google-auth) for collection and sharing |

## Stack

Python · Streamlit · Groq (Llama) · PostgreSQL · pandas · scikit-learn · scipy · Plotly ·
python-pptx · gspread / Google APIs · Docker

## Setup

```bash
git clone https://github.com/ratulsur/BI_Storyteller.git
cd BI_Storyteller

# Dependencies (managed with uv; pip also works)
uv sync                          # or: pip install -r requirements.txt

# Configure credentials in a .env file (never commit it — it is gitignored):
#   GROQ_API_KEY=...
#   DATABASE_URL=postgresql://...
#   GOOGLE_SERVICE_ACCOUNT=...    # service-account JSON or path, for Sheets
```

## Run

```bash
streamlit run app.py
```

Or with Docker:

```bash
docker build -t bi-storyteller .
docker run -p 8501:8501 --env-file .env bi-storyteller
```

Then open the app and step through the workflow from problem definition to presentation.

## Project structure

```
BI_Storyteller/
├── app.py             Streamlit entry point + workflow pages
├── api/               API layer
├── modules/           pipeline modules
├── utils/             core classes (Groq client, DB, forms, processing, viz, presentation)
├── config/            configuration
├── infrastructure/    infra setup
├── static/ template/  UI assets and presentation templates
├── tests/             test suite
├── dockerfile         container build
├── pyproject.toml     project + dependencies (uv.lock)
└── requirements.txt
```

## Notes

Requires active Groq AI credentials and Google Cloud service-account credentials for Sheets
integration; all secrets are supplied via environment variables. The app was originally
prototyped on Replit and is containerized for portable deployment.
