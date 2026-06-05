import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  timeout: 8000,
});

export async function getStats() {
  const { data } = await api.get("/dashboard/stats");
  return data;
}

export async function getTimeseries(limit = 100) {
  try {
    const { data } = await api.get("/dashboard/timeseries", { params: { limit } });
    return data.data || [];
  } catch (error) {
    console.warn("Timeseries data unavailable, using demo data");
    return null;
  }
}

export async function getAlerts() {
  const { data } = await api.get("/alerts");
  return data;
}

export async function trainModels() {
  const { data } = await api.post("/train");
  return data;
}

export async function getTrainingStatus() {
  const { data } = await api.get("/train/status");
  return data;
}

export async function predictFailure(equipmentId, values) {
  const { data } = await api.post("/predict/failure", {
    equipment_id: equipmentId,
    values
  });
  return data;
}

export async function predictRul(equipmentId, values) {
  const { data } = await api.post("/predict/rul", {
    equipment_id: equipmentId,
    values
  });
  return data;
}
