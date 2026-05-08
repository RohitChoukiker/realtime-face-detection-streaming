#  Real-Time Face Detection Video Streaming System

Full-stack containerised system for real-time face detection with WebSocket video streaming.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Docker Compose Network                  │
│                                                         │
│  ┌──────────────┐    WebSocket    ┌──────────────────┐  │
│  │   Frontend   │◄───────────────►│    Backend       │  │
│  │  React.js    │   REST /roi     │  FastAPI+Python  │  │
│  │  port 3000   │◄───────────────►│   port 8000      │  │
│  └──────────────┘                 └────────┬─────────┘  │
│                                            │ SQLAlchemy │
│                                   ┌────────▼─────────┐  │
│                                   │   PostgreSQL     │  │
│                                   │   port 5432      │  │
│                                   └──────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | React.js | WebSocket + webcam + live UI |
| Backend | FastAPI + Python | Async, fast, WebSocket native |
| Face Detection | MediaPipe | No OpenCV — as required |
| Image Drawing | Pillow (PIL) | No OpenCV — draws ROI box |
| Database | PostgreSQL | Structured ROI data, SQL queries |
| Containers | Docker + Compose | Reproducible, portable |

---

## 3 Required API Endpoints

| # | Method | Path | Description |
|---|--------|------|-------------|
| 1 | POST | `/video/upload` | Receive a single JPEG frame, return annotated frame |
| 2 | WS | `/video/stream` | Bidirectional WebSocket — stream frames, receive annotated |
| 3 | GET | `/roi/data` | Fetch stored ROI detections from PostgreSQL |

---

## Quick Start

### Prerequisites
- Docker Desktop installed and running
- Ports 3000, 8000, 5432 free

### Run everything

```bash
git clone https://github.com/RohitChoukiker/realtime-face-detection-streaming.git
cd realtime-face-detection-streaming

docker-compose up --build
```

Then open: **http://localhost:3000**

- Click **▶ Start Detection**
- Allow camera permission
- See real-time face detection with green ROI box!

### API Docs (Swagger UI)
http://localhost:8000/docs

---

## Project Structure

```
realtime-face-detection-streaming/
├── docker-compose.yml
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env
│   └── app/
│       ├── main.py                   ← FastAPI app
│       ├── core/config.py            ← Settings
│       ├── db/database.py            ← Async PostgreSQL
│       ├── models/
│       │   ├── roi.py                ← DB table model
│       │   └── schemas.py            ← Pydantic schemas
│       ├── services/
│       │   ├── face_detection.py     ← MediaPipe + Pillow (NO OpenCV)
│       │   └── roi_service.py        ← DB CRUD
│       └── api/routes/
│           ├── video.py              ← Endpoints 1 & 2
│           └── roi.py                ← Endpoint 3
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    └── src/
        ├── App.jsx                   ← Root component
        ├── components/
        │   ├── Header.jsx
        │   ├── VideoPanel.jsx        ← Live video + ROI box display
        │   └── ROIPanel.jsx          ← ROI data + stats table
        ├── hooks/
        │   ├── useVideoStream.js     ← Webcam + WebSocket logic
        │   └── useROIData.js         ← REST polling hook
        ├── services/
        │   ├── websocketService.js   ← WS connection manager
        │   └── apiService.js         ← Axios REST client
        └── styles/
            ├── App.css
            ├── Header.module.css
            ├── VideoPanel.module.css
            └── ROIPanel.module.css
```

---

## No OpenCV — What's Used Instead

The assignment bans OpenCV. This project uses:

**Face Detection:** `mediapipe` (Google's ML framework)
```python
detector = mp.solutions.face_detection.FaceDetection(min_detection_confidence=0.5)
result = detector.process(rgb_numpy_array)
bbox = result.detections[0].location_data.relative_bounding_box
```

**Drawing ROI Rectangle:** `Pillow` (PIL)
```python
draw = ImageDraw.Draw(image)
draw.rectangle([x, y, x+w, y+h], outline="#00FF00", width=3)
```

---

## Database Schema

Table: `roi_detections`

```sql
CREATE TABLE roi_detections (
  id          VARCHAR(36) PRIMARY KEY,
  session_id  VARCHAR(64) NOT NULL,
  frame_id    INTEGER NOT NULL,
  x           INTEGER NOT NULL,
  y           INTEGER NOT NULL,
  width       INTEGER NOT NULL,
  height      INTEGER NOT NULL,
  confidence  FLOAT NOT NULL,
  detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## AI Collaboration Attestation

This project was built with AI assistance (Claude by Anthropic).

**Where AI was used:**
- Boilerplate generation for FastAPI routes and SQLAlchemy models
- MediaPipe integration pattern suggestions
- CSS module styling
- Docker Compose configuration

**What was verified manually:**
- All three endpoints match the assignment specification
- OpenCV is confirmed absent from all imports
- WebSocket protocol (binary frame → text metadata) design
- Database schema matches ROI storage requirements
