import piexif
from PIL import Image
import os
from fractions import Fraction
import logging

# إعداد السجل الخاص بالمحرك
logger = logging.getLogger(__name__)

class MetadataInjector:
    """
    محرك حقن البيانات الجغرافية والميتا-داتا المتقدم.
    المسار المطلق: src.engine.metadata_processor
    """

    def __init__(self, image_path: str):
        self.image_path = image_path
        if not os.path.exists(self.image_path):
            logger.error(f"Image not found at: {self.image_path}")
            raise FileNotFoundError(f"Source image not found at: {self.image_path}")

    def _decimal_to_exif_rational(self, degree_float: float) -> tuple:
        """
        تحويل الإحداثيات العشرية إلى صيغة Rational المتوافقة مع معايير EXIF.
        """
        abs_degree = abs(degree_float)
        degrees = int(abs_degree)
        minutes = int((abs_degree - degrees) * 60)
        seconds = round((abs_degree - degrees - minutes / 60) * 3600, 5)
        
        seconds_fraction = Fraction(seconds).limit_denominator(1000)
        
        return (
            (degrees, 1),
            (minutes, 1),
            (seconds_fraction.numerator, seconds_fraction.denominator)
        )

    def inject_geo_authority(self, lat: float, lon: float, keywords: list, description: str):
        """
        تنفيذ عملية الحقن في طبقات البيانات الثنائية للصورة.
        """
        try:
            img = Image.open(self.image_path)
            
            # تهيئة قاموس EXIF
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
            
            # حقن الوصف والكلمات المفتاحية (XPKeywords المعياري)
            exif_dict["0th"][piexif.ImageIFD.ImageDescription] = description.encode('utf-8')
            keyword_string = ";".join(keywords).encode('utf-16le')
            exif_dict["0th"][piexif.ImageIFD.XPKeywords] = keyword_string

            # حقن إحداثيات GPS الدقيقة
            lat_ref = 'N' if lat >= 0 else 'S'
            lon_ref = 'E' if lon >= 0 else 'W'
            
            exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = lat_ref
            exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = self._decimal_to_exif_rational(lat)
            exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = lon_ref
            exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = self._decimal_to_exif_rational(lon)

            # تحويل البيانات إلى بايتات وحفظ الصورة
            exif_bytes = piexif.dump(exif_dict)
            img.save(self.image_path, exif=exif_bytes)
            img.close()
            logger.info(f"Successfully injected metadata into {self.image_path}")
            
        except Exception as e:
            logger.error(f"Metadata injection failed: {str(e)}")
            raise e

    def verify_integrity(self) -> bool:
        """
        التحقق من صحة البيانات المحقونة.
        """
        try:
            exif_data = piexif.load(self.image_path)
            return "GPS" in exif_data and len(exif_data["GPS"]) > 0
        except Exception:
            return False
