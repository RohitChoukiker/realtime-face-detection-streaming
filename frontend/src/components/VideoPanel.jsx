import React from "react";
import styles from "../styles/VideoPanel.module.css";

export default function VideoPanel({
  videoRef,
  canvasRef,
  annotatedSrc,
  isStreaming,
  fps,
  frameResult,
  onStart,
  onStop,
  error,
}) {
  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <h2 className={styles.title}>Live Feed</h2>
        <div className={styles.badges}>
          <span className={`${styles.badge} ${isStreaming ? styles.live : styles.idle}`}>
            {isStreaming ? " LIVE" : "IDLE"}
          </span>
          {isStreaming && (
            <span className={styles.badge}>{fps} fps</span>
          )}
        </div>
      </div>

      
      <div className={styles.videoWrapper}>
        
        <video
          ref={videoRef}
          className={styles.hiddenVideo}
          muted
          playsInline
        />

       
        <canvas ref={canvasRef} className={styles.hiddenCanvas} />

       
        {isStreaming && annotatedSrc ? (
          <img
            src={annotatedSrc}
            alt="Annotated video feed"
            className={styles.feed}
          />
        ) : (
          <div className={styles.placeholder}>
          
            <p>{isStreaming ? "Waiting for frames…" : "Press Start to begin"}</p>
          </div>
        )}

      
        {isStreaming && frameResult && (
          <div className={`${styles.detectionBadge} ${frameResult.face_detected ? styles.detected : styles.notDetected}`}>
            {frameResult.face_detected ? "Face Detected" : " No Face"}
          </div>
        )}
      </div>

     
      {isStreaming && frameResult && (
        <p className={styles.processingTime}>
           Processing: {frameResult.processing_time_ms?.toFixed(1)} ms
        </p>
      )}

     
      {error && <p className={styles.error}> {error}</p>}

     
      <div className={styles.controls}>
        {!isStreaming ? (
          <button className={styles.btnStart} onClick={onStart}>
             Start Detection
          </button>
        ) : (
          <button className={styles.btnStop} onClick={onStop}>
             Stop
          </button>
        )}
      </div>
    </div>
  );
}
