"""FastAPI API for the BI Storyteller backend.

This file defines endpoints for the full application lifecycle:

* Project creation and context updates.
* Variable extraction and approval.
* Questionnaire generation and approval.
* Synthetic data generation and cleaning.
* Visualisation and statistical analysis (trends, A/B tests, prediction, sentiment).
* LLM and Mixture‑of‑Recursions chat.
* Secondary scraping and ingestion (Flipkart and Astra DB).
* NLP analysis (topics, co‑occurrence, word correlations).
* Presentation assembly.

Each endpoint defers to an underlying function imported from the ``modules``
package.  If a module is missing or raises an error the API surfaces
a server error.  For production use, replace the in‑memory ``projects``
dict with persistent storage and add authentication as appropriate.
"""

from __future__ import annotations

import datetime as _dt
import uuid
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# In‑memory store for project state.  Do not use in production!
projects: Dict[str, Dict[str, Any]] = {}

# Pydantic schemas
class ProjectInitRequest(BaseModel):
    study_type: str
    business_problem: Optional[str] = None


class ProjectInitResponse(BaseModel):
    project_id: str


class ContextUpdateRequest(BaseModel):
    business_problem: str


class VariablesRequest(BaseModel):
    project_id: str


class VariablesResponse(BaseModel):
    variables: List[Dict[str, Any]]


class VariablesApproveRequest(BaseModel):
    project_id: str
    variables: List[Dict[str, Any]]


class QuestionnaireRequest(BaseModel):
    project_id: str


class QuestionnaireResponse(BaseModel):
    questionnaire: Dict[str, Any]


class QuestionnaireApproveRequest(BaseModel):
    project_id: str
    questionnaire: Dict[str, Any]


class SampleDataRequest(BaseModel):
    project_id: str
    n_rows: int = Field(100, ge=1)


class SampleDataResponse(BaseModel):
    data_path: str


class CleanDataRequest(BaseModel):
    project_id: str
    options: Dict[str, Any] = Field(default_factory=dict)


class CleanDataResponse(BaseModel):
    data_path: str
    summary: Dict[str, Any]


class PlotRequest(BaseModel):
    project_id: str
    columns: List[str]
    chart_type: str


class PlotResponse(BaseModel):
    plot_path: str


class TrendsRequest(BaseModel):
    project_id: str
    date_column: str
    metrics: List[str]


class TrendsResponse(BaseModel):
    results: Dict[str, Any]


class ABTestRequest(BaseModel):
    project_id: str
    variant_column: str
    metric_column: str
    test_type: str = "z"


class ABTestResponse(BaseModel):
    p_value: float
    lift: Optional[float] = None
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    summary: str


class PredictRequest(BaseModel):
    project_id: str
    target: str
    features: List[str]
    test_size: float = Field(0.2, ge=0.05, le=0.95)


class PredictResponse(BaseModel):
    metrics: Dict[str, Any]
    artifacts: Dict[str, str]


class SentimentRequest(BaseModel):
    project_id: str
    text_columns: List[str]


class SentimentResponse(BaseModel):
    results: Dict[str, Any]


class ChatRequest(BaseModel):
    project_id: str
    question: str


class ChatResponse(BaseModel):
    answer: str


class MorChatRequest(BaseModel):
    project_id: str
    question: str
    max_depth: int = 3
    branch_limit: int = 3
    budget_tokens: int = 3000


class MorChatResponse(BaseModel):
    answer: str
    trace: List[Dict[str, Any]]


class ScrapeRequest(BaseModel):
    project_id: str
    queries: List[str]
    max_products: int = 1
    review_count: int = 2


class ScrapeResponse(BaseModel):
    products_count: int
    reviews_count: int
    products_path: str
    reviews_path: str
    sample: Dict[str, Any]


class IngestRequest(BaseModel):
    project_id: str
    collection_name: Optional[str] = None
    do_sample_search: bool = False


class IngestResponse(BaseModel):
    inserted: int
    collection_name: str


class NLPRequest(BaseModel):
    project_id: str
    k: Optional[int] = None


class NLPResponse(BaseModel):
    results: Dict[str, Any]


class PresentationSectionRequest(BaseModel):
    project_id: str
    title: str
    content: str
    artifacts: Optional[List[str]] = None


class PresentationBuildRequest(BaseModel):
    project_id: str
    theme: Optional[str] = None


class PresentationBuildResponse(BaseModel):
    pptx_path: str


# FastAPI app instance
app = FastAPI(title="BI Storyteller API", version="0.1.0")

# ----------------------------------------------------------------------
# CORS configuration
#
# The frontend for BI Storyteller may run on a different port or domain
# (e.g. index.html served by a simple HTTP server on :8080).  Browsers
# enforce the same‑origin policy by default, blocking requests from a
# different origin.  To allow the browser to call this API, we
# configure CORSMiddleware with a list of allowed origins.  During
# development you can use "*" to allow everything, but it is
# recommended to explicitly list the domains you control in
# production.
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8080",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------------
# Static file serving
#
# When the API and frontend live in the same container you can serve
# your static files directly from FastAPI.  We mount the current
# directory under `/static` so that assets like `style.css` are
# accessible to the browser.  We also provide a root route that
# returns `index.html` so that navigating to http://localhost:8000/ in
# a browser loads your frontend.  If you prefer to host the frontend
# separately (e.g. via a CDN), you can remove this section.

app.mount("/static", StaticFiles(directory=".", html=False), name="static")

@app.get("/", response_class=FileResponse, include_in_schema=False)
def serve_index() -> FileResponse:
    """Serve the frontend index.html from the API root."""
    return FileResponse("index.html")


def _get_project(project_id: str) -> Dict[str, Any]:
    project = projects.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
    return project


# Primary workflow
@app.post("/project/init", response_model=ProjectInitResponse)
def create_project(req: ProjectInitRequest) -> ProjectInitResponse:
    project_id = str(uuid.uuid4())
    projects[project_id] = {
        "study_type": req.study_type,
        "business_problem": req.business_problem,
        "created_at": _dt.datetime.utcnow().isoformat(),
        "variables": None,
        "questionnaire": None,
        "raw_data_path": None,
        "clean_data_path": None,
        "analysis": {},
        "nlp": {},
        "presentation_sections": [],
    }
    return ProjectInitResponse(project_id=project_id)


@app.post("/project/{project_id}/context")
def update_context(project_id: str, req: ContextUpdateRequest) -> None:
    project = _get_project(project_id)
    project["business_problem"] = req.business_problem
    return None


@app.post("/llm/variables", response_model=VariablesResponse)
def extract_variables(req: VariablesRequest) -> VariablesResponse:
    project = _get_project(req.project_id)
    bp = project.get("business_problem")
    if not bp:
        raise HTTPException(status_code=400, detail="Business problem not set")
    try:
        from modules.groq_client import GroqClient  # type: ignore
        client = GroqClient()
        variables = client.extract_variables(bp)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Variable extraction failed: {exc}")
    return VariablesResponse(variables=variables)


@app.post("/project/{project_id}/variables")
def approve_variables(project_id: str, req: VariablesApproveRequest) -> None:
    project = _get_project(project_id)
    project["variables"] = req.variables
    return None


@app.post("/llm/questionnaire", response_model=QuestionnaireResponse)
def generate_questionnaire(req: QuestionnaireRequest) -> QuestionnaireResponse:
    project = _get_project(req.project_id)
    variables = project.get("variables")
    if not variables:
        raise HTTPException(status_code=400, detail="Variables not approved")
    bp = project.get("business_problem") or ""
    try:
        from modules.groq_client import GroqClient  # type: ignore
        client = GroqClient()
        questionnaire = client.generate_questionnaire(bp, variables)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Questionnaire generation failed: {exc}")
    return QuestionnaireResponse(questionnaire=questionnaire)


@app.post("/project/{project_id}/questionnaire")
def approve_questionnaire(project_id: str, req: QuestionnaireApproveRequest) -> None:
    project = _get_project(project_id)
    project["questionnaire"] = req.questionnaire
    return None


@app.post("/data/sample", response_model=SampleDataResponse)
def generate_sample_data(req: SampleDataRequest) -> SampleDataResponse:
    project = _get_project(req.project_id)
    q = project.get("questionnaire")
    if not q:
        raise HTTPException(status_code=400, detail="No questionnaire available")
    try:
        from modules.sampling import generate_sample_dataframe  # type: ignore
        from modules.storage import save_dataframe  # type: ignore
        df = generate_sample_dataframe(q, req.n_rows)
        project_dir = f"data/{req.project_id}"
        fname = f"sample_{int(_dt.datetime.utcnow().timestamp())}.parquet"
        path = save_dataframe(df, project_dir, fname)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Sample data generation failed: {exc}")
    project["raw_data_path"] = path
    return SampleDataResponse(data_path=path)


@app.post("/data/clean", response_model=CleanDataResponse)
def clean_data(req: CleanDataRequest) -> CleanDataResponse:
    project = _get_project(req.project_id)
    path = project.get("raw_data_path")
    if not path:
        raise HTTPException(status_code=400, detail="No raw data available")
    try:
        from modules.storage import load_dataframe, save_dataframe  # type: ignore
        from modules.analysis_cleaning import clean_data as do_clean  # type: ignore
        df = load_dataframe(path)
        cleaned, summary = do_clean(df, req.options)
        project_dir = f"data/{req.project_id}"
        fname = f"clean_{int(_dt.datetime.utcnow().timestamp())}.parquet"
        cpath = save_dataframe(cleaned, project_dir, fname)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Data cleaning failed: {exc}")
    project["clean_data_path"] = cpath
    return CleanDataResponse(data_path=cpath, summary=summary)


@app.post("/viz/figure", response_model=PlotResponse)
def create_plot(req: PlotRequest) -> PlotResponse:
    project = _get_project(req.project_id)
    path = project.get("clean_data_path") or project.get("raw_data_path")
    if not path:
        raise HTTPException(status_code=400, detail="No data available for plotting")
    try:
        from modules.storage import load_dataframe  # type: ignore
        from modules.analysis_visuals import create_plot as do_plot  # type: ignore
        df = load_dataframe(path)
        ppath = do_plot(df, req.columns, req.chart_type, req.project_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Plot creation failed: {exc}")
    return PlotResponse(plot_path=ppath)


@app.post("/analysis/trends", response_model=TrendsResponse)
def run_trends(req: TrendsRequest) -> TrendsResponse:
    project = _get_project(req.project_id)
    path = project.get("clean_data_path") or project.get("raw_data_path")
    if not path:
        raise HTTPException(status_code=400, detail="No data available")
    try:
        from modules.storage import load_dataframe  # type: ignore
        from modules.analysis_trends import analyse_trends  # type: ignore
        df = load_dataframe(path)
        results = analyse_trends(df, req.date_column, req.metrics, req.project_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {exc}")
    return TrendsResponse(results=results)


@app.post("/analysis/abtest", response_model=ABTestResponse)
def run_abtest(req: ABTestRequest) -> ABTestResponse:
    project = _get_project(req.project_id)
    path = project.get("clean_data_path") or project.get("raw_data_path")
    if not path:
        raise HTTPException(status_code=400, detail="No data available")
    try:
        from modules.storage import load_dataframe  # type: ignore
        from modules.analysis_abtest import perform_abtest  # type: ignore
        df = load_dataframe(path)
        result = perform_abtest(df, req.variant_column, req.metric_column, req.test_type)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"A/B test failed: {exc}")
    return ABTestResponse(**result)


@app.post("/analysis/predict", response_model=PredictResponse)
def run_predict(req: PredictRequest) -> PredictResponse:
    project = _get_project(req.project_id)
    path = project.get("clean_data_path") or project.get("raw_data_path")
    if not path:
        raise HTTPException(status_code=400, detail="No data available")
    try:
        from modules.storage import load_dataframe  # type: ignore
        from modules.analysis_predict import train_and_evaluate_model  # type: ignore
        df = load_dataframe(path)
        metrics, artifacts = train_and_evaluate_model(df, req.target, req.features, req.test_size, req.project_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")
    return PredictResponse(metrics=metrics, artifacts=artifacts)


@app.post("/analysis/sentiment", response_model=SentimentResponse)
def run_sentiment(req: SentimentRequest) -> SentimentResponse:
    project = _get_project(req.project_id)
    path = project.get("clean_data_path") or project.get("raw_data_path")
    if not path:
        raise HTTPException(status_code=400, detail="No data available")
    try:
        from modules.storage import load_dataframe  # type: ignore
        from modules.analysis_sentiment import analyse_sentiment  # type: ignore
        df = load_dataframe(path)
        results = analyse_sentiment(df, req.text_columns, req.project_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {exc}")
    return SentimentResponse(results=results)


@app.post("/llm/chat", response_model=ChatResponse)
def run_chat(req: ChatRequest) -> ChatResponse:
    project = _get_project(req.project_id)
    context_parts = []
    if project.get("business_problem"):
        context_parts.append(project["business_problem"])
    if project.get("variables"):
        context_parts.append(str(project["variables"]))
    context = "\n".join(context_parts)
    try:
        from modules.groq_client import GroqClient  # type: ignore
        client = GroqClient()
        answer = client.chat_response(req.question, context)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"LLM chat failed: {exc}")
    return ChatResponse(answer=answer)


@app.post("/mor/chat", response_model=MorChatResponse)
def run_mor(req: MorChatRequest) -> MorChatResponse:
    project = _get_project(req.project_id)
    context = project.get("business_problem", "")
    try:
        from modules.mor_controller import MorController  # type: ignore
        mor = MorController(req.max_depth, req.branch_limit, req.budget_tokens)
        answer = mor.recurse(req.question, context)
        trace = mor.trace
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"MoR chat failed: {exc}")
    return MorChatResponse(answer=answer, trace=trace)


# Secondary workflow
@app.post("/scrape/flipkart", response_model=ScrapeResponse)
def scrape(req: ScrapeRequest) -> ScrapeResponse:
    project = _get_project(req.project_id)
    try:
        from modules.flipkart_scraper import FlipkartScraper  # type: ignore
        scraper = FlipkartScraper()
        all_products: List[Dict[str, Any]] = []
        all_reviews: List[Dict[str, Any]] = []
        for q in req.queries:
            result = scraper.scrape(q, req.max_products, req.review_count)
            all_products.extend(result["products"])
            all_reviews.extend(result["reviews"])
        # Dedup
        products_dict: Dict[str, Dict[str, Any]] = {}
        for p in all_products:
            pid = p.get("product_id") or p.get("title")
            products_dict[pid] = p
        reviews_dict: Dict[str, Dict[str, Any]] = {}
        for r in all_reviews:
            key = f"{r.get('product_id')}::{r.get('review_id')}"
            reviews_dict[key] = r
        uniq_products = list(products_dict.values())
        uniq_reviews = list(reviews_dict.values())
        from modules.storage import save_records  # type: ignore
        project_dir = f"data/{req.project_id}/secondary"
        ppath = save_records(uniq_products, project_dir, "products.parquet")
        rpath = save_records(uniq_reviews, project_dir, "reviews.parquet")
        project["nlp"]["products_path"] = ppath
        project["nlp"]["reviews_path"] = rpath
        sample = {"product": uniq_products[0] if uniq_products else {}, "review": uniq_reviews[0] if uniq_reviews else {}}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {exc}")
    return ScrapeResponse(
        products_count=len(uniq_products),
        reviews_count=len(uniq_reviews),
        products_path=ppath,
        reviews_path=rpath,
        sample=sample,
    )


@app.post("/ingest/astra", response_model=IngestResponse)
def ingest(req: IngestRequest) -> IngestResponse:
    project = _get_project(req.project_id)
    ppath = project.get("nlp", {}).get("products_path")
    rpath = project.get("nlp", {}).get("reviews_path")
    if not rpath:
        raise HTTPException(status_code=400, detail="No scraped data available")
    try:
        from modules.storage import load_dataframe  # type: ignore
        from modules.ingestion_astra import DataIngestion  # type: ignore
        reviews_df = load_dataframe(rpath)
        ingestion = DataIngestion()
        inserted, coll = ingestion.run(reviews_df, req.collection_name, req.do_sample_search)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")
    return IngestResponse(inserted=inserted, collection_name=coll)


@app.post("/nlp/topics", response_model=NLPResponse)
def nlp_topics(req: NLPRequest) -> NLPResponse:
    project = _get_project(req.project_id)
    rpath = project.get("nlp", {}).get("reviews_path")
    if not rpath:
        raise HTTPException(status_code=400, detail="No reviews available")
    try:
        from modules.storage import load_dataframe  # type: ignore
        from modules.nlp_text import topic_model  # type: ignore
        df = load_dataframe(rpath)
        results = topic_model(df["text"].tolist(), req.k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Topic modelling failed: {exc}")
    return NLPResponse(results=results)


@app.post("/nlp/cooccurrence", response_model=NLPResponse)
def nlp_cooccur(req: NLPRequest) -> NLPResponse:
    project = _get_project(req.project_id)
    rpath = project.get("nlp", {}).get("reviews_path")
    if not rpath:
        raise HTTPException(status_code=400, detail="No reviews available")
    try:
        from modules.storage import load_dataframe  # type: ignore
        from modules.nlp_text import cooccurrence_matrix  # type: ignore
        df = load_dataframe(rpath)
        results = cooccurrence_matrix(df["text"].tolist())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Co‑occurrence analysis failed: {exc}")
    return NLPResponse(results=results)


@app.post("/nlp/corrwords", response_model=NLPResponse)
def nlp_corrwords(req: NLPRequest) -> NLPResponse:
    project = _get_project(req.project_id)
    rpath = project.get("nlp", {}).get("reviews_path")
    if not rpath:
        raise HTTPException(status_code=400, detail="No reviews available")
    try:
        from modules.storage import load_dataframe  # type: ignore
        from modules.nlp_text import word_correlations  # type: ignore
        df = load_dataframe(rpath)
        results = word_correlations(df["text"].tolist())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Word correlation analysis failed: {exc}")
    return NLPResponse(results=results)


@app.post("/viz/bubbleline", response_model=PlotResponse)
def viz_bubbleline(req: NLPRequest) -> PlotResponse:
    project = _get_project(req.project_id)
    rpath = project.get("nlp", {}).get("reviews_path")
    if not rpath:
        raise HTTPException(status_code=400, detail="No reviews available")
    try:
        from modules.storage import load_dataframe  # type: ignore
        from modules.analysis_visuals import create_bubbleline  # type: ignore
        df = load_dataframe(rpath)
        plot_path = create_bubbleline(df["text"].tolist(), req.project_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Bubbleline creation failed: {exc}")
    return PlotResponse(plot_path=plot_path)


# Presentation
@app.post("/presentation/section")
def add_section(req: PresentationSectionRequest) -> None:
    project = _get_project(req.project_id)
    project["presentation_sections"].append({
        "title": req.title,
        "content": req.content,
        "artifacts": req.artifacts or [],
    })
    return None


@app.post("/presentation/build", response_model=PresentationBuildResponse)
def build_presentation(req: PresentationBuildRequest) -> PresentationBuildResponse:
    project = _get_project(req.project_id)
    sections = project.get("presentation_sections", [])
    if not sections:
        raise HTTPException(status_code=400, detail="No presentation sections added")
    try:
        from modules.presentation_generator import PresentationGenerator  # type: ignore
        generator = PresentationGenerator()
        prs = generator.create_comprehensive_presentation({
            "business_problem": project.get("business_problem"),
            "processed_data": None,  # optionally pass cleaned DataFrame if available
            "analysis_results": project.get("analysis"),
            "dashboard_insights": None,
            "chat_history": [],
        }, req.theme or "Modern Business")
        filename = f"presentation_{req.project_id}_{int(_dt.datetime.utcnow().timestamp())}.pptx"
        pptx_path = generator.save_presentation(prs, filename)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Presentation build failed: {exc}")
    project["presentation_path"] = pptx_path
    return PresentationBuildResponse(pptx_path=pptx_path)
