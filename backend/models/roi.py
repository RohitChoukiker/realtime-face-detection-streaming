
import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Float, Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

if TYPE_CHECKING:
    from frame import Frame
    from session import Session

class ROIDetection(Base):

    __tablename__ = "roi_detections"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    frame_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("frames.id", ondelete="CASCADE"),
        nullable=False, unique=True  
    )
    session_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False, index=True   
    )

    frame_number: Mapped[int] = mapped_column(Integer, nullable=False)
    x: Mapped[int] = mapped_column(Integer, nullable=False)
    y: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    frame: Mapped["Frame"] = relationship("Frame", back_populates="roi_detection")
    session: Mapped["Session"] = relationship("Session")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "frame_id": self.frame_id,
            "session_id": self.session_id,
            "frame_number": self.frame_number,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "confidence": self.confidence,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
        }