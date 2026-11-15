"""The demo's web server (card #47): the page in app/static/ and three small JSON answers.

Run it from the repo folder:
    pip install -r requirements-demo.txt
    python app/server.py            then open http://localhost:8000

/api/company/<number>   one company, step by step (engine.company)
/api/overview           the whole pipeline's counts, weights and test result (engine.overview)
/api/code/<step>        the real source of one step, read from src/ (engine.code)
"""

import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

sys.path.insert(0, str(Path(__file__).resolve().parent))   # so that `import engine` works from the repo folder
import engine                                              # noqa: E402

app = FastAPI(title="TENSEGRITY demo")


@app.get("/api/company/{number}")
def company(number: str):
    return engine.company(number)


@app.get("/api/overview")
def overview():
    return engine.overview()


@app.get("/api/code/{step}")
def code(step: str):
    if step not in engine.CODE:
        raise HTTPException(404, f"No step called {step}")
    return engine.code(step)


# Everything else is the page itself: index.html, app.css, app.js, the fonts and the logo
app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="page")

if __name__ == "__main__":
    engine.load()          # load the crawl (or data/demo.pkl) before the first visitor, not during
    uvicorn.run(app, host="127.0.0.1", port=8000)
