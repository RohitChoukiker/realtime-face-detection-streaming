from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from routes import video, roi
from database import init_db


app = FastAPI(
    title="Face Detection API",
    description="Real time face detection video streaming system",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Face Detection API is running"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(video.router, prefix="/video", tags=["Video"])
app.include_router(roi.router, prefix="/roi", tags=["ROI"])

@app.on_event("startup")
async def on_startup() -> None:
   await init_db()


if __name__ == "__main__":
   
    uvicorn.run(app, host="0.0.0", port=8000)

