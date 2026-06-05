import { Activity, AlertTriangle, Gauge, Thermometer, Waves, Workflow } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { getStats, getTimeseries } from "../api";
import { KpiCard } from "../components/KpiCard";
import { RadarHealth, RulChart, TimeChart } from "../components/Charts";
import { series as demoSeries } from "../data/demo";
import { subscribeSensorStream } from "../firebase";

export function Dashboard() {
  const { data: stats } = useQuery({ queryKey: ["stats"], queryFn: getStats, retry: false });
  const { data: timeseriesData } = useQuery({ 
    queryKey: ["timeseries"], 
    queryFn: () => getTimeseries(100), 
    retry: false 
  });

  // Réception des données capteurs en temps réel via Firebase
  const [realtimeSeries, setRealtimeSeries] = useState([]);
  useEffect(() => {
    const path = import.meta.env.VITE_FIREBASE_SENSORS_PATH || "/sensors/latest";
    const unsubscribe = subscribeSensorStream(path, (val) => {
      if (!val) return;
      let points = [];
      if (Array.isArray(val)) {
        points = val.map((p) => ({
          t: p.t || p.time || new Date().toLocaleTimeString(),
          temp: p.temperature ?? p.temp ?? null,
          vibration: p.vibration ?? null,
          pressure: p.pressure ?? null,
          humidity: p.humidity ?? null,
        }));
      } else if (typeof val === "object") {
        const first = Object.values(val)[0];
        if (first && typeof first === "object") {
          points = Object.entries(val).map(([k, v]) => ({
            t: v.t || v.time || k,
            temp: v.temperature ?? v.temp ?? null,
            vibration: v.vibration ?? null,
            pressure: v.pressure ?? null,
            humidity: v.humidity ?? null,
          }));
        } else {
          points = [{
            t: new Date().toLocaleTimeString(),
            temp: val.temperature ?? val.temp ?? null,
            vibration: val.vibration ?? null,
            pressure: val.pressure ?? null,
            humidity: val.humidity ?? null,
          }];
        }
      }
      setRealtimeSeries((prev) => {
        const merged = [...prev, ...points];
        return merged.slice(-100);
      });
    });
    return () => unsubscribe && unsubscribe();
  }, []);

  // Utiliser les données en temps réel si disponibles, sinon API puis démo
  const chartData = realtimeSeries && realtimeSeries.length > 0 ? realtimeSeries : (timeseriesData && timeseriesData.length > 0 ? timeseriesData : demoSeries);

  const dashboardStats = stats || {
    total_equipment: 128,
    critical_equipment: 9,
    avg_failure_probability: 0.18,
    avg_rul: 64.5,
    temperature: 68.2,
    vibration: 41.8,
    pressure: 96.1,
    health_score: 84
  };

  // Si on a une lecture temps réel, l'utiliser pour mettre à jour les KPI
  const latest = chartData && chartData.length ? chartData[chartData.length - 1] : null;
  if (latest) {
    dashboardStats.temperature = latest.temp ?? dashboardStats.temperature;
    dashboardStats.vibration = latest.vibration ?? dashboardStats.vibration;
    dashboardStats.pressure = latest.pressure ?? dashboardStats.pressure;
  }

  return (
    <div className="space-y-6">
      <Header title="Dashboard principal" subtitle="Vue opérationnelle des actifs miniers et du risque de panne." />
      <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard icon={Workflow} label="Équipements" value={dashboardStats.total_equipment} tone="info" />
        <KpiCard icon={AlertTriangle} label="Critiques" value={dashboardStats.critical_equipment} tone="danger" />
        <KpiCard icon={Gauge} label="Risque moyen" value={Math.round(dashboardStats.avg_failure_probability * 100)} suffix="%" tone="warn" />
        <KpiCard icon={Activity} label="RUL moyen" value={Number(dashboardStats.avg_rul).toFixed(1)} tone="normal" />
        <KpiCard icon={Thermometer} label="Température" value={dashboardStats.temperature} suffix=" °C" tone="warn" />
        <KpiCard icon={Waves} label="Vibrations" value={dashboardStats.vibration} suffix=" mm/s" tone="info" />
        <KpiCard icon={Gauge} label="Pression" value={dashboardStats.pressure} suffix=" bar" tone="danger" />
        <KpiCard icon={Activity} label="Santé globale" value={dashboardStats.health_score} suffix="%" tone="normal" />
      </div>
      <div className="grid xl:grid-cols-3 gap-4">
        <section className="panel p-5 xl:col-span-2"><h2 className="font-semibold mb-4">Séries temporelles capteurs</h2><TimeChart data={chartData} /></section>
        <section className="panel p-5"><h2 className="font-semibold mb-4">Radar santé</h2><RadarHealth /></section>
      </div>
      <div className="grid xl:grid-cols-2 gap-4">
        <section className="panel p-5"><h2 className="font-semibold mb-4">RUL et probabilité de panne</h2><RulChart data={chartData} /></section>
        <EquipmentTable stats={dashboardStats} />
      </div>
    </div>
  );
}

export function Header({ title, subtitle }) {
  return (
    <header>
      <p className="text-sm font-semibold text-copper">MinePredict</p>
      <h2 className="text-3xl font-bold tracking-normal">{title}</h2>
      <p className="text-slate-600 mt-1">{subtitle}</p>
    </header>
  );
}

export function EquipmentTable({ stats }) {
  const rows = [
    { label: "Équipements suivis", value: stats.total_equipment },
    { label: "Équipements critiques", value: stats.critical_equipment },
    { label: "Risque moyen", value: `${Math.round(stats.avg_failure_probability * 100)} %` },
    { label: "RUL moyen", value: `${Number(stats.avg_rul).toFixed(1)} cycles` },
    { label: "Santé globale", value: `${stats.health_score} %` },
  ];

  return (
    <section className="panel p-5 overflow-x-auto">
      <h2 className="font-semibold mb-4">Synthèse des actifs</h2>
      <table className="w-full text-sm">
        <thead className="text-left text-slate-500">
          <tr><th className="py-2">Métrique</th><th>Valeur</th></tr>
        </thead>
        <tbody>
          {rows.map((item) => (
            <tr key={item.label} className="border-t border-slate-100">
              <td className="py-3 font-medium">{item.label}</td>
              <td>{item.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
