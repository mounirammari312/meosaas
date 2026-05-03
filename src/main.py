from fastapi import FastAPI, HTTPException
from src.engine.metadata_processor import MetadataInjector
import os

app = FastAPI(title="MEO Dominator Engine", version="1.0.0")

@app.get("/")
async def health_check():
    """
    اختبار حالة النظام للتأكد من عمل السيرفر.
    """
    return {"status": "operational", "engine": "MEO-v1"}

@app.post("/process-geo")
async def process_image_geo(image_path: str, lat: float, lon: float):
    """
    نقطة نهاية (Endpoint) لاستقبال أوامر حقن البيانات الجغرافية.
    """
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    
    try:
        injector = MetadataInjector(image_path)
        injector.inject_geo_authority(
            lat=lat,
            lon=lon,
            keywords=["Local Service", "MEO Optimization"],
            description="Automated Geo-Targeting via MEO Engine"
        )
        return {"message": "Image processed successfully", "path": image_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
