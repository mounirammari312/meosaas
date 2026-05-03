from fastapi import FastAPI, HTTPException, BackgroundTasks
from src.engine.metadata_processor import MetadataInjector
from src.engine.traffic_orchestrator import TrafficOrchestrator
import os

app = FastAPI(title="MEO Dominator Engine", version="1.1.0")

@app.get("/")
async def health_check():
    """
    نقطة فحص الحالة التشغيلية للنظام.
    """
    return {
        "status": "operational", 
        "engine": "MEO-v1",
        "architecture": "Senior-Decoupled"
    }

@app.post("/process-geo")
async def process_image_geo(image_path: str, lat: float, lon: float):
    """
    استقبال أوامر حقن البيانات الجغرافية في الصور.
    """
    # التحقق من وجود الملف في المسار المطلق المذكور
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail=f"Image file not found at: {image_path}")
    
    try:
        injector = MetadataInjector(image_path)
        injector.inject_geo_authority(
            lat=lat,
            lon=lon,
            keywords=["Local Service", "MEO Optimization", "Expert Repair"],
            description="Automated Geo-Targeting via MEO Engine v1.1"
        )
        return {
            "status": "success",
            "message": "Metadata injection completed",
            "integrity_check": injector.verify_integrity()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engine Error: {str(e)}")

@app.post("/trigger-traffic")
async def trigger_ghost_traffic(background_tasks: BackgroundTasks, cid: str, intensity: int = 5):
    """
    تفعيل محاكي التفاعل الجغرافي (CTR) لنشاط معين عبر المعرف الفريد CID.
    يتم التشغيل كـ Background Task لضمان استقرار السيرفر.
    """
    try:
        # تهيئة المحاكي - في الإنتاج يتم تمرير قائمة البروكسيات هنا
        orchestrator = TrafficOrchestrator(target_cid=cid)
        
        # إضافة المهمة للخلفية (Non-blocking operation)
        background_tasks.add_task(orchestrator.mass_orchestration, intensity=intensity)
        
        return {
            "status": "initiated",
            "message": f"Ghost traffic orchestration started in background for CID: {cid}",
            "intensity_level": intensity
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestrator Failure: {str(e)}")
