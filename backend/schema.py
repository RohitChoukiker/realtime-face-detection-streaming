from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ROIBase(BaseModel):
    x: int = Field(..., ge=0, description="Left edge of bounding box (pixels)")
    y: int = Field(..., ge=0, description="Top edge of bounding box (pixels)")
    width: int = Field(..., gt=0, description="Width of bounding box (pixels)")
    height: int = Field(..., gt=0, description="Height of bounding box (pixels)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence 0-1")


class ROICreate(ROIBase):
    session_id: str
    frame_id: int


class ROIResponse(ROIBase):
    id: str
    session_id: str
    frame_id: int
    detected_at: datetime

    class Config:
        from_attributes = True


class ROIListResponse(BaseModel):
    total: int
    items: List[ROIResponse]


class SessionStats(BaseModel):
    session_id: str
    total_detections: int
    first_detection: Optional[datetime]
    last_detection: Optional[datetime]
    avg_confidence: Optional[float]
    avg_width: Optional[float]
    avg_height: Optional[float]


class FrameResult(BaseModel):
    """Returned over WebSocket after each frame is processed."""
    session_id: str
    frame_id: int
    face_detected: bool
    roi: Optional[ROIBase] = None
    processing_time_ms: float