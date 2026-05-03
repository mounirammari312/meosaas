from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.engine.metadata_processor import MetadataInjector
from src.engine.traffic_orchestrator import TrafficOrchestrator
import os
import shutil

app = FastAPI(title="MEO Control Center", version="1.2.0")

# إعداد المسارات المطلقة لخدمة الواجهة
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# تهيئة نظام القوالب
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "src/templates"))

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    تقديم واجهة التحكم الرئيسية.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process-geo")
async def process_image_geo(
    lat: float = Form(...), 
    lon: float = Form(...), 
    image: UploadFile = File(...)
):
    """
    استقبال الصورة والبيانات الجغرافية ومعالجتها فوراً.
    """
    file_path = os.path.join(UPLOAD_DIR, image.filename)
    
    # حفظ الملف مؤقتاً للمعالجة
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    try:
        injector = MetadataInjector(file_path)
        injector.inject_geo_authority(
            lat=lat,
            lon=lon,
            keywords=["Premium Service", "Local Authority", "Expert Repair"],
            description="MEO Optimized Asset v1.2"
        )
        return {
            "status": "success", 
            "message": "Image geo-tagged successfully",
            "integrity": injector.verify_integrity()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trigger-traffic")
async def trigger_ghost_traffic(background_tasks: BackgroundTasks, cid: str, intensity: int = 5):
    """
    تفعيل محاكي التفاعل الجغرافي في الخلفية.
    """
    try:
        orchestrator = TrafficOrchestrator(target_cid=cid)
        background_tasks.add_task(orchestrator.mass_orchestration, intensity=intensity)
        return {
            "status": "initiated",
            "target": cid,
            "intensity": intensity
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
