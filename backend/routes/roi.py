import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from DTO.schema import (
    ROIListResponse, ROIResponse,
    SessionStats, SessionListResponse, SessionResponse,
)
from services.roi_service import ROIService, SessionService, FrameService

logger = logging.getLogger(__name__)
router = APIRouter()



@router.get("/data", response_model=ROIListResponse,
            summary="Fetch stored ROI detections from DB")
async def get_roi_data(
    session_id: Optional[str] = Query(None),
    limit:      int           = Query(100, ge=1, le=500),
    offset:     int           = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
   
    rows, total = await ROIService.get_all(
        db, session_id=session_id, limit=limit, offset=offset
    )
    return ROIListResponse(
        total=total,
        items=[ROIResponse(**r.to_dict()) for r in rows],
    )

@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    limit:  int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    rows, total = await SessionService.get_all_sessions(
        db, limit=limit, offset=offset
    )
    return SessionListResponse(
        total=total,
        items=[SessionResponse(**r.to_dict()) for r in rows],
    )


@router.get("/stats/{session_id}", response_model=SessionStats)
async def get_session_stats(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    stats = await ROIService.get_session_stats(db, session_id)
    if not stats:
        raise HTTPException(404, detail=f"No data for session '{session_id}'")
    return stats


@router.get("/frames/{session_id}")
async def get_frames(
    session_id: str,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    frames = await FrameService.get_frames_for_session(
        db, session_id, limit=limit
    )
    return {
        "session_id": session_id,
        "total": len(frames),
        "items": [f.to_dict() for f in frames],
    }


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    session = await SessionService.get_session(db, session_id)
    if not session:
        raise HTTPException(404, detail="Session not found")
    await db.delete(session)  
    return {"deleted": True, "session_id": session_id}