import { Header } from "./Dashboard";

export function History() {
  const rows = ["Inspection hydraulique", "Alerte vibration", "Réentraînement modèle", "Maintenance préventive", "Retour production"];
  return (
    <div className="space-y-6">
      <Header title="Historique" subtitle="Chronologie des événements, alertes et actions de maintenance." />
      <section className="panel p-5">
        {rows.map((row, index) => (
          <div key={row} className="flex gap-4 border-b border-slate-100 py-4 last:border-0">
            <span className="font-bold text-copper">J-{index + 1}</span>
            <p>{row}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
