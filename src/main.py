from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.engine.metadata_processor import MetadataInjector
from src.engine.traffic_orchestrator import TrafficOrchestrator
import os
import shutil

app = FastAPI(title="MEO Control Center", version="1.3.0")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "src/templates"))

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process-geo")
async def process_image_geo(
    lat: float = Form(...), 
    lon: float = Form(...), 
    image: UploadFile = File(...)
):
    file_path = os.path.join(UPLOAD_DIR, image.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    try:
        injector = MetadataInjector(file_path)
        injector.inject_geo_authority(lat=lat, lon=lon, keywords=["MEO", "Local"], description="Verified Asset")
        return {"status": "success", "integrity": injector.verify_integrity()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trigger-traffic")
async def trigger_ghost_traffic(
    background_tasks: BackgroundTasks, 
    cid: str = Form(...), 
    intensity: int = Form(...),
    gateway_url: str = Form(None) # استقبال رابط البروكسي من الهاتف
):
    try:
        # استخدام رابط الهاتف كبوابة خروج للبيانات
        orchestrator = TrafficOrchestrator(target_cid=cid, gateway_url=gateway_url)
        background_tasks.add_task(orchestrator.mass_orchestration, intensity=intensity)
        return {"status": "initiated", "gateway": gateway_url if gateway_url else "Direct"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
