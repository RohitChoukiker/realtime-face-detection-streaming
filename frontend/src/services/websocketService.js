
const WS_URL = process.env.REACT_APP_WS_URL || "ws://localhost:8000";

class WebSocketService {
  constructor() {
    this.ws = null;
    this.sessionId = null;
    this.isConnected = false;
    this._expectingBinary = true; 

    // Callbacks set by consumer
    this.onAnnotatedFrame = null; 
    this.onFrameResult = null;  
    this.onConnected = null;      
    this.onDisconnected = null;  
    this.onError = null;         
  }

  connect() {
    if (this.ws) this.disconnect();

    this.ws = new WebSocket(`${WS_URL}/video/stream`);
    this.ws.binaryType = "blob";

    this.ws.onopen = () => {
      this.isConnected = true;
      console.log("[WS] Connected");
    };

    this.ws.onmessage = (event) => {
      if (typeof event.data === "string") {
        
        try {
          const data = JSON.parse(event.data);
          if (data.event === "connected") {
            this.sessionId = data.session_id;
            this.onConnected?.(data.session_id);
          } else {
            this.onFrameResult?.(data);
          }
        } catch (e) {
          console.warn("[WS] Failed to parse text message:", e);
        }
      } else {
     
        const url = URL.createObjectURL(event.data);
        this.onAnnotatedFrame?.(url);
      }
    };

    this.ws.onclose = () => {
      this.isConnected = false;
      console.log("[WS] Disconnected");
      this.onDisconnected?.();
    };

    this.ws.onerror = (err) => {
      console.error("[WS] Error:", err);
      this.onError?.("WebSocket connection error");
    };
  }

  sendFrame(jpegBlob) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(jpegBlob);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.isConnected = false;
    }
  }
}

export default new WebSocketService();
