import io
import os
import requests
from fastapi import FastAPI, Form, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import piexif
from PIL import Image

# إعداد التطبيق والمجلدات القالبية
app = FastAPI()

# المسارات المطلوبة للتشغيل
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# --- وظائف المعالجة الخلفية (Background Tasks) ---

def dispatch_relay_task(cid: str, gateway_url: str, intensity: int):
    """
    بروتوكول المُرحّل الذكي: توجيه الأوامر إلى الهاتف لتنفيذ الزيارات محلياً.
    هذا يضمن تجاوز حظر Cloudflare لبروتوكول CONNECT.
    """
    # تنظيف الرابط وضمان وجود مسار الـ Relay
    relay_endpoint = f"{gateway_url.rstrip('/')}/fire"
    
    headers = {
        "User-Agent": "MEO-Dominator-Architect/1.3.0",
        "X-Relay-Command": "execute-traffic-simulation"
    }

    print(f"[*] Starting Smart Relay Task for CID: {cid} via {relay_endpoint}")
    
    success_count = 0
    for i in range(intensity):
        try:
            # إرسال طلب تنفيذ المهمة للهاتف
            params = {"cid": cid}
            response = requests.get(relay_endpoint, params=params, headers=headers, timeout=20)
            
            if response.status_code == 200:
                success_count += 1
                print(f"[+] Relay Signal {i+1}/{intensity}: Success")
            else:
                print(f"[-] Relay Signal {i+1}/{intensity}: Failed with code {response.status_code}")
                
        except Exception as e:
            print(f"[!] Critical Connection Error during relay: {str(e)}")
            break # التوقف في حالة فشل النفق كلياً

    print(f"[#] Task Completed. Success Rate: {success_count}/{intensity}")

# --- المسارات (Routes) ---

@app.get("/")
async def read_index(request: Request):
    """خدمة واجهة التحكم الأساسية"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process-geo")
async def process_geo(
    image: UploadFile = File(...),
    lat: float = Form(...),
    lon: float = Form(...)
):
    """
    محرك حقن البيانات الجغرافية (Module 1).
    يحافظ على جودة الصورة ويحقن إحداثيات GPS في EXIF.
    """
    try:
        # قراءة الصورة
        contents = await image.read()
        img = Image.open(io.BytesIO(contents))
        
        # تحويل الإحداثيات إلى صيغة EXIF (Rational)
        def to_deg(value, loc):
            if value < 0: loc_value = loc[0]
            elif value > 0: loc_value = loc[1]
            else: loc_value = ""
            abs_value = abs(value)
            deg = int(abs_value)
            t1 = (abs_value - deg) * 60
            min = int(t1)
            sec = round((t1 - min) * 60, 5)
            return (deg, min, sec), loc_value

        lat_deg, lat_ref = to_deg(lat, ["S", "N"])
        lon_deg, lon_ref = to_deg(lon, ["W", "E"])

        exif_dict = {"GPS": {
            piexif.GPSIFD.GPSLatitudeRef: lat_ref,
            piexif.GPSIFD.GPSLatitude: [(int(x), 1) if isinstance(x, int) else (int(x*10000), 10000) for x in lat_deg],
            piexif.GPSIFD.GPSLongitudeRef: lon_ref,
            piexif.GPSIFD.GPSLongitude: [(int(x), 1) if isinstance(x, int) else (int(x*10000), 10000) for x in lon_deg],
        }}

        exif_bytes = piexif.dump(exif_dict)
        
        # حفظ الصورة مع البيانات الجديدة
        output = io.BytesIO()
        img.save(output, format=img.format, exif=exif_bytes)
        output.seek(0)

        return JSONResponse(content={
            "status": "success", 
            "message": "Image geo-tagged successfully",
            "coordinates": {"lat": lat, "lon": lon}
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/trigger-traffic")
async def trigger_traffic(
    background_tasks: BackgroundTasks,
    cid: str = Form(...),
    gateway_url: str = Form(...),
    intensity: int = Form(...)
):
    """
    محرك ترافيك الأشباح (Module 2).
    يعمل بنظام Smart Relay لتجنب أخطاء 400 Bad Request.
    """
    # التحقق الأولي من صحة الرابط
    if not gateway_url.startswith("http"):
        return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid Gateway URL format"})

    # إسناد المهمة للخلفية لضمان عدم تجميد الواجهة
    background_tasks.add_task(dispatch_relay_task, cid, gateway_url, intensity)

    return JSONResponse(content={
        "status": "initiated",
        "mode": "Smart-Relay-Active",
        "details": f"Dispatching {intensity} signals to {gateway_url}"
    })

if __name__ == "__main__":
    import uvicorn
    # التشغيل المحلي للتطوير
    uvicorn.run(app, host="0.0.0.0", port=8000)
