from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils.questionnaire_generator import QuestionnaireGenerator

app = FastAPI(title="BI Storyteller Web")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


def _parse_variables(raw_variables: str) -> list[str]:
    return [line.strip() for line in raw_variables.splitlines() if line.strip()]


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/questionnaire", response_class=HTMLResponse)
def questionnaire(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "questionnaire.html",
        {"request": request, "questions": None, "variables": "", "error": None},
    )


@app.post("/questionnaire", response_class=HTMLResponse)
def questionnaire_submit(request: Request, variables: str = Form(...)) -> HTMLResponse:
    parsed_variables = _parse_variables(variables)
    if not parsed_variables:
        return templates.TemplateResponse(
            "questionnaire.html",
            {
                "request": request,
                "questions": None,
                "variables": variables,
                "error": "Please enter at least one variable.",
            },
        )

    generator = QuestionnaireGenerator()
    questions = generator.generate_questionnaire(parsed_variables)
    return templates.TemplateResponse(
        "questionnaire.html",
        {
            "request": request,
            "questions": questions,
            "variables": variables,
            "error": None,
        },
    )
