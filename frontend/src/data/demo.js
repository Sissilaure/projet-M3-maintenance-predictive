export const series = [
  { t: "08:00", temp: 61, vibration: 29, pressure: 88, rul: 86, probability: 0.11 },
  { t: "10:00", temp: 66, vibration: 33, pressure: 91, rul: 78, probability: 0.16 },
  { t: "12:00", temp: 72, vibration: 39, pressure: 98, rul: 64, probability: 0.24 },
  { t: "14:00", temp: 81, vibration: 51, pressure: 111, rul: 39, probability: 0.47 },
  { t: "16:00", temp: 89, vibration: 64, pressure: 127, rul: 16, probability: 0.78 },
  { t: "18:00", temp: 76, vibration: 46, pressure: 103, rul: 44, probability: 0.35 }
];

export const equipment = [
  { id: "TRUCK-042", type: "Camion-benne", health: 41, risk: "critique", temp: 91, vibration: 62, rul: 9 },
  { id: "DRILL-017", type: "Foreuse", health: 73, risk: "moyen", temp: 71, vibration: 44, rul: 36 },
  { id: "CRUSH-006", type: "Concasseur", health: 58, risk: "moyen", temp: 84, vibration: 49, rul: 24 },
  { id: "TRUCK-019", type: "Camion-benne", health: 89, risk: "faible", temp: 63, vibration: 30, rul: 82 },
  { id: "PUMP-011", type: "Hydraulique", health: 77, risk: "faible", temp: 67, vibration: 35, rul: 68 }
];

export const featureImportance = [
  { feature: "tool_wear", value: 0.31 },
  { feature: "vibration_rate_change", value: 0.22 },
  { feature: "temperature_rolling_mean", value: 0.18 },
  { feature: "pressure_lag_1", value: 0.12 },
  { feature: "torque", value: 0.09 },
  { feature: "rotational_speed", value: 0.08 }
];

export const confusion = [
  { name: "TN", value: 412 },
  { name: "FP", value: 28 },
  { name: "FN", value: 19 },
  { name: "TP", value: 86 }
];
