import { Header } from "./Dashboard";
import { RulChart } from "../components/Charts";

export function Rul() {
  return (
    <div className="space-y-6">
      <Header title="Estimation RUL" subtitle="Durée de vie résiduelle estimée avec validation temporelle passé vers futur." />
      <section className="panel p-5"><h2 className="font-semibold mb-4">RUL réel vs prédit</h2><RulChart /></section>
      <section className="panel p-5">
        <h2 className="font-semibold mb-2">Lecture métier</h2>
        <p className="text-slate-600">Un RUL faible combiné à une probabilité de panne élevée déclenche une alerte critique et une recommandation de maintenance préventive.</p>
      </section>
    </div>
  );
}
