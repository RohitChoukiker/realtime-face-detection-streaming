import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Integer, DateTime, func, Boolean, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from session import Session
    from roi import ROIDetection


class Frame(Base):
    __tablename__ = "frames"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    frame_number: Mapped[int] = mapped_column(Integer, nullable=False)
    had_face: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    processing_time_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    session: Mapped["Session"] = relationship("Session", back_populates="frames")
    roi_detection: Mapped[Optional["ROIDetection"]] = relationship(
        "ROIDetection", back_populates="frame",
        cascade="all, delete-orphan", uselist=False
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "frame_number": self.frame_number,
            "had_face": self.had_face,
            "processing_time_ms": self.processing_time_ms,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "roi": self.roi_detection.to_dict() if self.roi_detection else None,
        }