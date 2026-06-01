import { Header, EquipmentTable } from "./Dashboard";
import { TimeChart } from "../components/Charts";

export function Monitoring() {
  return (
    <div className="space-y-6">
      <Header title="Monitoring équipements" subtitle="Surveillance temps réel simulée des camions, foreuses et concasseurs." />
      <EquipmentTable />
      <section className="panel p-5"><h2 className="font-semibold mb-4">Flux capteurs</h2><TimeChart /></section>
    </div>
  );
}
