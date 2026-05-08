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
    frame_id: str
    frame_number: int


class ROIResponse(ROIBase):
    id: str
    session_id: str
    frame_id: str
    frame_number: int
    detected_at: datetime

    class Config:
        from_attributes = True


class ROIListResponse(BaseModel):
    total: int
    items: List[ROIResponse]


class SessionStats(BaseModel):
    session_id: str
    total_frames: int
    total_detections: int
    detection_rate: float
    first_detection: Optional[datetime]
    last_detection: Optional[datetime]
    avg_confidence: Optional[float]
    avg_width: Optional[float]
    avg_height: Optional[float]
    
class SessionResponse(BaseModel):
    id: str
    started_at: datetime
    ended_at: Optional[datetime]
    total_frames: int
    total_detections: int
    is_active: bool


class SessionListResponse(BaseModel):
    total: int
    items: List[SessionResponse]    
    


class FrameResult(BaseModel):
    session_id: str
    frame_id: str
    frame_number: int
    face_detected: bool
    roi: Optional[ROIBase] = None
    processing_time_ms: float
    
    
class FrameCreate(BaseModel):
    session_id: str
    frame_number: int
    had_face: bool
    processing_time_ms: float