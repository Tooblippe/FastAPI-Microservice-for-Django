import io
import pathlib
import uuid
from functools import lru_cache

import pytesseract
from PIL import Image
from fastapi import (
    FastAPI,
    Header,
    HTTPException,
    Depends,
    Request,
    File,
    UploadFile
)
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_auth_token: str
    debug: bool = False
    echo_active: bool = False
    app_auth_token_prod: str = None
    skip_auth: bool = False

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
DEBUG = settings.debug
if DEBUG:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


BASE_DIR = pathlib.Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"

if DEBUG:
    app = FastAPI()
else:
    app = FastAPI(docs_url=None, redoc_url=None)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
origins = [
    "http://localhost",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_auth(authorization=Header(None), settings: Settings = Depends(get_settings)):
    """
    Authorization: Bearer <token>
    {"authorization": "Bearer <token>"}
    """
    if settings.debug and settings.skip_auth:
        return
    if authorization is None:
        raise HTTPException(detail="Invalid endpoint", status_code=401)
    label, token = authorization.split()
    if token != settings.app_auth_token:
        raise HTTPException(detail="Invalid endpoint", status_code=401)


@app.post("/test/")
def test(request: Request):
    return {"status": "ok"}


@app.post("/")  # http POST
async def prediction_view(file: UploadFile = File(...), authorization=Header(None),
                          settings: Settings = Depends(get_settings)):
    verify_auth(authorization, settings)
    bytes_str = io.BytesIO(await file.read())
    try:
        img = Image.open(bytes_str)
    except:
        raise HTTPException(detail="Invalid image", status_code=400)
    preds = pytesseract.image_to_string(img)
    predictions = [x for x in preds.split("\n")]
    results = {"result": predictions, "orig": preds}

    return results


@app.post("/img-echo/", response_class=FileResponse)  # http POST
async def img_echo_view(file: UploadFile = File(...), settings: Settings = Depends(get_settings)):
    if not settings.echo_active:
        raise HTTPException(detail="Invalid endpoint", status_code=400)
    UPLOAD_DIR.mkdir(exist_ok=True)
    bytes_str = io.BytesIO(await file.read())
    try:
        img = Image.open(bytes_str)
    except:
        raise HTTPException(detail="Invalid image", status_code=400)
    fname = pathlib.Path(file.filename)
    fext = fname.suffix  # .jpg, .txt
    dest = UPLOAD_DIR / f"{uuid.uuid1()}{fext}"
    img.save(dest)
    return dest


app.mount("/", StaticFiles(directory="./frontend/build-frontend", html=True), name="frontend")
# app.mount("/css", StaticFiles(directory="./frontend/build-frontend/css", html=True), name="frontend")
app.mount("/js", StaticFiles(directory="./frontend/build-frontend/js", html=True), name="frontend")
# app.mount("/img", StaticFiles(directory="./frontend/build-frontend/img", html=True), name="frontend")
