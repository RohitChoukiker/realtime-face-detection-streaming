import { useState, useRef, useCallback, useEffect } from "react";
import wsService from "../services/websocketService";

const FRAME_INTERVAL_MS = 33; 
const JPEG_QUALITY = 0.8;

export default function useVideoStream() {
  const videoRef = useRef(null);     
  const canvasRef = useRef(null);      
  const intervalRef = useRef(null);   
  const prevFrameUrl = useRef(null);  
  const isStartingRef = useRef(false);

  const [isStreaming, setIsStreaming] = useState(false);
  const [annotatedSrc, setAnnotatedSrc] = useState(null);  
  const [frameResult, setFrameResult] = useState(null);    
  const [sessionId, setSessionId] = useState(null);
  const [error, setError] = useState(null);
  const [fps, setFps] = useState(0);


  const fpsCountRef = useRef(0);
  useEffect(() => {
    const timer = setInterval(() => {
      setFps(fpsCountRef.current);
      fpsCountRef.current = 0;
    }, 1000);
    return () => clearInterval(timer);
  }, []);


  useEffect(() => {
    wsService.onAnnotatedFrame = (url) => {
      if (prevFrameUrl.current) URL.revokeObjectURL(prevFrameUrl.current);
      prevFrameUrl.current = url;
      setAnnotatedSrc(url);
      fpsCountRef.current += 1;
    };

    wsService.onFrameResult = (result) => {
      setFrameResult(result);
    };

    wsService.onConnected = (sid) => {
      setSessionId(sid);
      setError(null);
    };

    wsService.onDisconnected = () => {
      setIsStreaming(false);
    };

    wsService.onError = (msg) => {
      setError(msg);
      setIsStreaming(false);
    };

    return () => {
      wsService.onAnnotatedFrame = null;
      wsService.onFrameResult = null;
      wsService.onConnected = null;
      wsService.onDisconnected = null;
      wsService.onError = null;
    };
  }, []);

  const startStream = useCallback(async () => {
    if (isStartingRef.current) return;
    isStartingRef.current = true;
    setError(null);
    setIsStreaming(true);


    let stream = null;
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: "user" },
        audio: false,
      });
    } catch (err) {
      setError("Camera access denied. Please allow camera permission.");
      isStartingRef.current = false;
      setIsStreaming(false);
      return;
    }


    if (videoRef.current) {
      videoRef.current.srcObject = stream;
      try {
        await videoRef.current.play();
      } catch (err) {
        console.warn("[Video] play() failed/interrupted:", err);
      }
    }

    wsService.connect();


    intervalRef.current = setInterval(() => {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      if (!video || !canvas || !wsService.isConnected) return;

      const ctx = canvas.getContext("2d");
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      canvas.toBlob(
        (blob) => {
          if (blob) wsService.sendFrame(blob);
        },
        "image/jpeg",
        JPEG_QUALITY
      );
    }, FRAME_INTERVAL_MS);

    isStartingRef.current = false;
  }, []);

  const stopStream = useCallback(() => {
    clearInterval(intervalRef.current);
    intervalRef.current = null;
   if (videoRef.current?.srcObject) {
      videoRef.current.srcObject.getTracks().forEach((t) => t.stop());
      videoRef.current.srcObject = null;
    }

    wsService.disconnect();

    setIsStreaming(false);
    setAnnotatedSrc(null);
    setFrameResult(null);
    isStartingRef.current = false;
  }, []);

  return {
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
  };
}
