import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Line, LineChart, PolarAngleAxis, PolarGrid, Radar, RadarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { confusion, featureImportance, series } from "../data/demo";

export function TimeChart({ data }) {
  const chartData = data && data.length > 0 ? data : series;
  return (
    <div className="h-72">
      <ResponsiveContainer>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="t" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="temp" stroke="#c47735" strokeWidth={2} name="Température" />
          <Line type="monotone" dataKey="vibration" stroke="#2563eb" strokeWidth={2} name="Vibration" />
          <Line type="monotone" dataKey="pressure" stroke="#ef4444" strokeWidth={2} name="Pression" />
          <Line type="monotone" dataKey="humidity" stroke="#06b6d4" strokeWidth={2} name="Humidité" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function RulChart({ data }) {
  const chartData = data && data.length > 0 ? data : series;
  return (
    <div className="h-72">
      <ResponsiveContainer>
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="t" />
          <YAxis />
          <Tooltip />
          <Area type="monotone" dataKey="rul" stroke="#10b981" fill="#d1fae5" name="RUL" />
          <Area type="monotone" dataKey="probability" stroke="#ef4444" fill="#fee2e2" name="Probabilité panne" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export function FeatureImportanceChart() {
  return (
    <div className="h-72">
      <ResponsiveContainer>
        <BarChart data={featureImportance} layout="vertical" margin={{ left: 70 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis dataKey="feature" type="category" />
          <Tooltip />
          <Bar dataKey="value" fill="#26313d" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ConfusionMatrix() {
  const colors = ["#10b981", "#f59e0b", "#ef4444", "#2563eb"];
  return (
    <div className="h-72">
      <ResponsiveContainer>
        <BarChart data={confusion}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="value">
            {confusion.map((entry, index) => <Cell key={entry.name} fill={colors[index]} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function RadarHealth() {
  const data = [
    { axis: "Température", value: 72 },
    { axis: "Vibrations", value: 61 },
    { axis: "Pression", value: 68 },
    { axis: "RUL", value: 54 },
    { axis: "Fiabilité", value: 81 }
  ];
  return (
    <div className="h-72">
      <ResponsiveContainer>
        <RadarChart data={data}>
          <PolarGrid />
          <PolarAngleAxis dataKey="axis" />
          <Radar dataKey="value" stroke="#c47735" fill="#c47735" fillOpacity={0.35} />
          <Tooltip />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
