import React, { useEffect, useState } from "react";
import Header from "./components/Header";
import VideoPanel from "./components/VideoPanel";
import ROIPanel from "./components/ROIPanel";
import useVideoStream from "./hooks/useVideoStream";
import useROIData from "./hooks/useROIData";
import { checkHealth } from "./services/apiService";
import "./styles/App.css";

export default function App() {
  const [backendStatus, setBackendStatus] = useState("unknown");


  const {
    videoRef,
    canvasRef,
    isStreaming,
    annotatedSrc,
    frameResult,
    sessionId,
    error,
    fps,
    startStream,
    stopStream,
  } = useVideoStream();


  const { roiList, stats, total, loading } = useROIData(sessionId);

  useEffect(() => {
    checkHealth()
      .then(() => setBackendStatus("ok"))
      .catch(() => setBackendStatus("error"));
  }, []);


  const liveROI = frameResult?.face_detected ? frameResult.roi : null;

  return (
    <div className="app">
      <Header backendStatus={backendStatus} />

      <main className="main-layout">
       
        <VideoPanel
          videoRef={videoRef}
          canvasRef={canvasRef}
          annotatedSrc={annotatedSrc}
          isStreaming={isStreaming}
          fps={fps}
          frameResult={frameResult}
          onStart={startStream}
          onStop={stopStream}
          error={error}
        />

   
        <ROIPanel
          roiList={roiList}
          stats={stats}
          total={total}
          loading={loading}
          sessionId={sessionId}
          liveROI={liveROI}
        />
      </main>

      
    </div>
  );
}
