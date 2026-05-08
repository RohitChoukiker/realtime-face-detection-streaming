
import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});


export const fetchROIData = async (params = {}) => {
  const { data } = await api.get("/roi/data", { params });
  return data; 
};


export const fetchSessionStats = async (sessionId) => {
  const { data } = await api.get(`/roi/stats/${sessionId}`);
  return data;
};


export const checkHealth = async () => {
  const { data } = await api.get("/");
  return data;
};

export default api;
