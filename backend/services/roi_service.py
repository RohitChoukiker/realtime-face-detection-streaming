import uuid
import logging
from typing import List, Optional
from datetime import datetime

from sqlalchemy import select, func, desc, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.session import Session
from models.frame import Frame
from models.roi import ROIDetection
from DTO.schema import ROICreate, FrameCreate, SessionStats

logger = logging.getLogger(__name__)

class SessionService:

    @staticmethod
    async def create_session(db: AsyncSession, session_id: Optional[str] = None) -> Session:
        sid = session_id or str(uuid.uuid4())
        session = Session(id=sid)
        db.add(session)
        await db.flush()
        await db.refresh(session)
        logger.info(f"Session created: {sid}")
        return session

    @staticmethod
    async def get_session(db: AsyncSession, session_id: str) -> Optional[Session]:
        result = await db.execute(
            select(Session).where(Session.id == session_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def end_session(db: AsyncSession, session_id: str) -> Optional[Session]:
        session = await SessionService.get_session(db, session_id)
        if session:
            session.ended_at = datetime.utcnow()
            session.is_active = False
            await db.flush()
        return session

    @staticmethod
    async def increment_session_counters(
        db: AsyncSession,
        session_id: str,
        had_face: bool
    ):
        await db.execute(
            update(Session)
            .where(Session.id == session_id)
            .values(
                total_frames=Session.total_frames + 1,
                total_detections=Session.total_detections + (1 if had_face else 0),
            )
        )

    @staticmethod
    async def get_all_sessions(
        db: AsyncSession, limit: int = 50, offset: int = 0
    ) -> tuple[List[Session], int]:
        total = (await db.execute(
            select(func.count()).select_from(Session)
        )).scalar_one()
        rows = (await db.execute(
            select(Session).order_by(desc(Session.started_at))
            .limit(limit).offset(offset)
        )).scalars().all()
        return list(rows), total

class FrameService:

    @staticmethod
    async def create_frame(db: AsyncSession, data: FrameCreate) -> Frame:
        frame = Frame(
            session_id=data.session_id,
            frame_number=data.frame_number,
            had_face=data.had_face,
            processing_time_ms=data.processing_time_ms,
        )
        db.add(frame)
        await db.flush()
        await db.refresh(frame)
        return frame

    @staticmethod
    async def get_frames_for_session(
        db: AsyncSession, session_id: str, limit: int = 100
    ) -> List[Frame]:
        result = await db.execute(
            select(Frame)
            .where(Frame.session_id == session_id)
            .options(selectinload(Frame.roi_detection))
            .order_by(Frame.frame_number)
            .limit(limit)
        )
        return list(result.scalars().all())


class ROIService:

    @staticmethod
    async def save_roi(db: AsyncSession, data: ROICreate) -> ROIDetection:
        roi = ROIDetection(
            frame_id=data.frame_id,
            session_id=data.session_id,
            frame_number=data.frame_number,
            x=data.x, y=data.y,
            width=data.width, height=data.height,
            confidence=data.confidence,
        )
        db.add(roi)
        await db.flush()
        await db.refresh(roi)
        logger.debug(f"ROI saved: session={data.session_id} frame={data.frame_number}")
        return roi

    @staticmethod
    async def get_all(
        db: AsyncSession,
        session_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[ROIDetection], int]:
        q  = select(ROIDetection).order_by(desc(ROIDetection.detected_at))
        cq = select(func.count()).select_from(ROIDetection)

        if session_id:
            q  = q.where(ROIDetection.session_id == session_id)
            cq = cq.where(ROIDetection.session_id == session_id)

        total = (await db.execute(cq)).scalar_one()
        rows  = (await db.execute(q.limit(limit).offset(offset))).scalars().all()
        return list(rows), total

    @staticmethod
    async def get_session_stats(
        db: AsyncSession, session_id: str
    ) -> Optional[SessionStats]:

        roi_row = (await db.execute(
            select(
                func.count().label("total_rois"),
                func.min(ROIDetection.detected_at).label("first"),
                func.max(ROIDetection.detected_at).label("last"),
                func.avg(ROIDetection.confidence).label("avg_conf"),
                func.avg(ROIDetection.width).label("avg_w"),
                func.avg(ROIDetection.height).label("avg_h"),
            ).where(ROIDetection.session_id == session_id)
        )).one()

        frame_row = (await db.execute(
            select(func.count().label("total_frames"))
            .where(Frame.session_id == session_id)
        )).one()

        total_frames = frame_row.total_frames or 0
        total_rois   = roi_row.total_rois or 0

        if total_frames == 0:
            return None

        return SessionStats(
            session_id=session_id,
            total_detections=total_rois,
            total_frames=total_frames,
            detection_rate=round(total_rois / total_frames, 4),
            first_detection=roi_row.first,
            last_detection=roi_row.last,
            avg_confidence=round(float(roi_row.avg_conf), 4) if roi_row.avg_conf else None,
            avg_width=round(float(roi_row.avg_w), 2) if roi_row.avg_w else None,
            avg_height=round(float(roi_row.avg_h), 2) if roi_row.avg_h else None,
        )