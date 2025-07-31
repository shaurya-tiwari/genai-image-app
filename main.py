from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from PIL import Image
import io, base64
from image_caption import describe_image

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, file: UploadFile = File(...)):
    image_bytes = await file.read()
    description = describe_image(image_bytes)
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    return templates.TemplateResponse("result.html", {
        "request": request,
        "description": description,
        "image_data": f"data:image/jpeg;base64,{image_b64}"
    })
