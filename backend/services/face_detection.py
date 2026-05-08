
import io
import logging
import time
from dataclasses import dataclass
from typing import Optional, Tuple

import mediapipe as mp
import numpy as np
from PIL import Image, ImageDraw

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class DetectionResult:
    face_detected: bool
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    confidence: float = 0.0
    processing_time_ms: float = 0.0


class FaceDetectionService:

    def __init__(self):
        self._mp_face = mp.solutions.face_detection
        self._detector = self._mp_face.FaceDetection(
            model_selection=0,
            min_detection_confidence=settings.DETECTION_CONFIDENCE,
        )
        logger.info("MediaPipe FaceDetection initialised — NO OpenCV")

    def process_frame(self, jpeg_bytes: bytes) -> Tuple[bytes, DetectionResult]:
        t0 = time.perf_counter()

        image = self._bytes_to_pil(jpeg_bytes)
        result = self._detect(image)

        if result.face_detected:
            image = self._draw_roi(image, result)

        annotated_bytes = self._pil_to_bytes(image)
        result.processing_time_ms = (time.perf_counter() - t0) * 1000
        return annotated_bytes, result

    @staticmethod
    def _bytes_to_pil(data: bytes) -> Image.Image:
        return Image.open(io.BytesIO(data)).convert("RGB")

    @staticmethod
    def _pil_to_bytes(image: Image.Image, quality: int = 85) -> bytes:
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=quality)
        return buf.getvalue()

    def _detect(self, image: Image.Image) -> DetectionResult:
        rgb_array = np.array(image)
        mp_result = self._detector.process(rgb_array)

        if not mp_result.detections:
            return DetectionResult(face_detected=False)

        detection = mp_result.detections[0]
        score = float(detection.score[0])

        bb = detection.location_data.relative_bounding_box
        img_w, img_h = image.size

        x = max(0, int(bb.xmin * img_w))
        y = max(0, int(bb.ymin * img_h))
        w = min(int(bb.width * img_w), img_w - x)
        h = min(int(bb.height * img_h), img_h - y)

        return DetectionResult(
            face_detected=True,
            x=x, y=y, width=w, height=h,
            confidence=score,
        )

    @staticmethod
    def _draw_roi(image: Image.Image, result: DetectionResult) -> Image.Image:
        
        draw = ImageDraw.Draw(image)

        x0, y0 = result.x, result.y
        x1, y1 = result.x + result.width, result.y + result.height

        for i in range(settings.BOX_THICKNESS):
            draw.rectangle(
                [x0 - i, y0 - i, x1 + i, y1 + i],
                outline=settings.BOX_COLOR,
            )

        label = f"Face {result.confidence:.0%}"
        draw.text((x0, max(0, y0 - 18)), label, fill=settings.BOX_COLOR)

        return image


_service: Optional[FaceDetectionService] = None


def get_face_service() -> FaceDetectionService:
    global _service
    if _service is None:
        _service = FaceDetectionService()
    return _service