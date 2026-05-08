import json
import logging
import uuid
from typing import Optional

from fastapi import (APIRouter, WebSocket, WebSocketDisconnect,
                     Depends, UploadFile, File, HTTPException)
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from DTO.schema import FrameResult, ROICreate, FrameCreate
from services.face_detection import get_face_service, FaceDetectionService
from services.roi_service import ROIService, FrameService, SessionService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", summary="Upload single frame for face detection")
async def upload_frame(
    file: UploadFile = File(...),
    session_id: Optional[str] = None,
    frame_number: int = 0,
    db: AsyncSession = Depends(get_db),
    service: FaceDetectionService = Depends(get_face_service),
):
    if file.content_type not in ("image/jpeg", "image/jpg", "image/png"):
        raise HTTPException(status_code=400, detail="Only JPEG/PNG accepted.")

    sid = session_id or str(uuid.uuid4())
    raw_bytes = await file.read()

    
    annotated_bytes, detection = service.process_frame(raw_bytes)

  
    existing = await SessionService.get_session(db, sid)
    if not existing:
        await SessionService.create_session(db, sid)


    frame_record = await FrameService.create_frame(db, FrameCreate(
        session_id=sid,
        frame_number=frame_number,
        had_face=detection.face_detected,
        processing_time_ms=detection.processing_time_ms,
    ))


    if detection.face_detected:
        await ROIService.save_roi(db, ROICreate(
            frame_id=frame_record.id,
            session_id=sid,
            frame_number=frame_number,
            x=detection.x, y=detection.y,
            width=detection.width, height=detection.height,
            confidence=detection.confidence,
        ))


    await SessionService.increment_session_counters(db, sid, detection.face_detected)

    return Response(
        content=annotated_bytes,
        media_type="image/jpeg",
        headers={
            "X-Session-Id":        sid,
            "X-Frame-Id":          frame_record.id,
            "X-Face-Detected":     str(detection.face_detected).lower(),
            "X-Processing-Time-Ms": f"{detection.processing_time_ms:.2f}",
            "X-ROI": json.dumps({
                "x": detection.x, "y": detection.y,
                "width": detection.width, "height": detection.height,
                "confidence": detection.confidence,
            }) if detection.face_detected else "null",
        }
    )


@router.websocket("/stream")
async def video_stream(
    websocket: WebSocket,
    session_id: Optional[str] = None,
):
   
    await websocket.accept()

    sid     = session_id or str(uuid.uuid4())
    counter = 0
    service = get_face_service()

    logger.info(f"WS connected: session={sid}")

    async for db in get_db():

       
        if not await SessionService.get_session(db, sid):
            await SessionService.create_session(db, sid)
            await db.commit()

        await websocket.send_text(json.dumps({
            "event": "connected", "session_id": sid
        }))

        try:
            while True:
                raw_bytes = await websocket.receive_bytes()
                counter  += 1
                
                annotated_bytes, detection = service.process_frame(raw_bytes)

                frame_record = await FrameService.create_frame(db, FrameCreate(
                    session_id=sid,
                    frame_number=counter,
                    had_face=detection.face_detected,
                    processing_time_ms=detection.processing_time_ms,
                ))
                
                if detection.face_detected:
                    await ROIService.save_roi(db, ROICreate(
                        frame_id=frame_record.id,
                        session_id=sid,
                        frame_number=counter,
                        x=detection.x, y=detection.y,
                        width=detection.width, height=detection.height,
                        confidence=detection.confidence,
                    ))

                await SessionService.increment_session_counters(
                    db, sid, detection.face_detected
                )
                await db.commit()
                
                await websocket.send_bytes(annotated_bytes)

                await websocket.send_text(FrameResult(
                    session_id=sid,
                    frame_id=frame_record.id,
                    frame_number=counter,
                    face_detected=detection.face_detected,
                    roi={
                        "x": detection.x, "y": detection.y,
                        "width": detection.width, "height": detection.height,
                        "confidence": detection.confidence,
                    } if detection.face_detected else None,
                    processing_time_ms=detection.processing_time_ms,
                ).model_dump_json())

        except WebSocketDisconnect:
            logger.info(f"WS disconnected: session={sid} frames={counter}")
            await SessionService.end_session(db, sid)
            await db.commit()

        except Exception as e:
            logger.error(f"WS error: {e}", exc_info=True)
            await websocket.send_text(
                json.dumps({"event": "error", "message": str(e)})
            )
        break