import logging
import sys

def setup_logger():
    """
    إعداد تهيئة السجلات للعمل في بيئة النشر السحابي.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("MEO_ENGINE")

# تشغيل الإعداد عند استدعاء المكتبة
logger = setup_logger()
