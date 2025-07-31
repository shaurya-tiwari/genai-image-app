from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from PIL import Image
import io, base64
from image_caption import describe_image
import gc  # Garbage collector

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, file: UploadFile = File(...)):
    image_bytes = await file.read()

    # Load image
    image = Image.open(io.BytesIO(image_bytes))
    image_format = image.format if image.format in ["JPEG", "PNG"] else "JPEG"

    # Convert mode if needed
    if image_format == "JPEG" and image.mode != "RGB":
        image = image.convert("RGB")  # JPEG doesn't support transparency
    elif image_format == "PNG" and image.mode not in ["RGB", "RGBA"]:
        image = image.convert("RGBA")  # Ensure safe PNG encoding

    # Resize image
    image = image.resize((512, 512))

    # Re-encode after resize
    buffer = io.BytesIO()
    image.save(buffer, format=image_format)
    resized_image_bytes = buffer.getvalue()

    # Get caption
    description = describe_image(resized_image_bytes)

    # Base64 encode for display
    image_b64 = base64.b64encode(resized_image_bytes).decode("utf-8")
    mime_type = "image/png" if image_format == "PNG" else "image/jpeg"

    # Cleanup
    del image, buffer, image_bytes, resized_image_bytes
    gc.collect()

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "description": description,
            "image_data": f"data:{mime_type};base64,{image_b64}",
        },
    )
