import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  timeout: 8000,
});

export async function getStats() {
  const { data } = await api.get("/dashboard/stats");
  return data;
}

export async function getAlerts() {
  const { data } = await api.get("/alerts");
  return data;
}

export async function trainModels() {
  const { data } = await api.post("/train");
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
