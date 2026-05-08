import { useState, useEffect, useCallback, useRef } from "react";
import { fetchROIData, fetchSessionStats } from "../services/apiService";

const POLL_INTERVAL_MS = 2000;

export default function useROIData(sessionId) {
  const [roiList, setRoiList] = useState([]);
  const [stats, setStats] = useState(null);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const timerRef = useRef(null);

  const fetchData = useCallback(async () => {
    if (!sessionId) return;
    try {
      setLoading(true);
      const [roiData, sessionStats] = await Promise.all([
        fetchROIData({ session_id: sessionId, limit: 20 }),
        fetchSessionStats(sessionId).catch(() => null),
      ]);
      setRoiList(roiData.items);
      setTotal(roiData.total);
      setStats(sessionStats);
      setError(null);
    } catch (err) {
      setError("Failed to fetch ROI data");
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  
  useEffect(() => {
    if (!sessionId) {
      setRoiList([]);
      setStats(null);
      setTotal(0);
      return;
    }

    fetchData();
    timerRef.current = setInterval(fetchData, POLL_INTERVAL_MS);

    return () => clearInterval(timerRef.current);
  }, [sessionId, fetchData]);

  return { roiList, stats, total, loading, error, refetch: fetchData };
}
