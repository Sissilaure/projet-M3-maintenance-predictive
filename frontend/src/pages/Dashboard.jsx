import { Activity, AlertTriangle, Gauge, Thermometer, Waves, Workflow } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { getStats } from "../api";
import { KpiCard } from "../components/KpiCard";
import { RadarHealth, RulChart, TimeChart } from "../components/Charts";
import { equipment } from "../data/demo";

export function Dashboard() {
  const { data } = useQuery({ queryKey: ["stats"], queryFn: getStats, retry: false });
  const stats = data || {
    total_equipment: 128,
    critical_equipment: 9,
    avg_failure_probability: 0.18,
    avg_rul: 64.5,
    temperature: 68.2,
    vibration: 41.8,
    pressure: 96.1,
    health_score: 84
  };
  return (
    <div className="space-y-6">
      <Header title="Dashboard principal" subtitle="Vue opérationnelle des actifs miniers et du risque de panne." />
      <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard icon={Workflow} label="Équipements" value={stats.total_equipment} tone="info" />
        <KpiCard icon={AlertTriangle} label="Critiques" value={stats.critical_equipment} tone="danger" />
        <KpiCard icon={Gauge} label="Risque moyen" value={Math.round(stats.avg_failure_probability * 100)} suffix="%" tone="warn" />
        <KpiCard icon={Activity} label="RUL moyen" value={Number(stats.avg_rul).toFixed(1)} tone="normal" />
        <KpiCard icon={Thermometer} label="Température" value={stats.temperature} suffix=" °C" tone="warn" />
        <KpiCard icon={Waves} label="Vibrations" value={stats.vibration} suffix=" mm/s" tone="info" />
        <KpiCard icon={Gauge} label="Pression" value={stats.pressure} suffix=" bar" tone="danger" />
        <KpiCard icon={Activity} label="Santé globale" value={stats.health_score} suffix="%" tone="normal" />
      </div>
      <div className="grid xl:grid-cols-3 gap-4">
        <section className="panel p-5 xl:col-span-2"><h2 className="font-semibold mb-4">Séries temporelles capteurs</h2><TimeChart /></section>
        <section className="panel p-5"><h2 className="font-semibold mb-4">Radar santé</h2><RadarHealth /></section>
      </div>
      <div className="grid xl:grid-cols-2 gap-4">
        <section className="panel p-5"><h2 className="font-semibold mb-4">RUL et probabilité de panne</h2><RulChart /></section>
        <EquipmentTable />
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

export function EquipmentTable() {
  return (
    <section className="panel p-5 overflow-x-auto">
      <h2 className="font-semibold mb-4">Tableau équipements</h2>
      <table className="w-full text-sm">
        <thead className="text-left text-slate-500">
          <tr><th className="py-2">ID</th><th>Type</th><th>Santé</th><th>Risque</th><th>RUL</th></tr>
        </thead>
        <tbody>
          {equipment.map((item) => (
            <tr key={item.id} className="border-t border-slate-100">
              <td className="py-3 font-medium">{item.id}</td>
              <td>{item.type}</td>
              <td>{item.health}%</td>
              <td><span className={`px-2 py-1 rounded text-xs status-${item.risk}`}>{item.risk}</span></td>
              <td>{item.rul}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
