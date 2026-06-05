import { useQuery } from "@tanstack/react-query";
import { Header, EquipmentTable } from "./Dashboard";
import { TimeChart } from "../components/Charts";
import { getStats } from "../api";

export function Monitoring() {
  const { data } = useQuery({ queryKey: ["stats"], queryFn: getStats, retry: false });
  const stats = data || {
    total_equipment: 128,
    critical_equipment: 9,
    avg_failure_probability: 0.18,
    avg_rul: 64.5,
    temperature: 68.2,
    vibration: 41.8,
    pressure: 96.1,
    health_score: 84,
  };

  return (
    <div className="space-y-6">
      <Header title="Monitoring équipements" subtitle="Surveillance temps réel simulée des camions, foreuses et concasseurs." />
      <EquipmentTable stats={stats} />
      <section className="panel p-5"><h2 className="font-semibold mb-4">Flux capteurs</h2><TimeChart /></section>
    </div>
  );
}
