import { useQuery } from "@tanstack/react-query";
import { AlertTriangle } from "lucide-react";
import { getAlerts } from "../api";
import { Header } from "./Dashboard";

export function Alerts() {
  const { data } = useQuery({ queryKey: ["alerts"], queryFn: getAlerts, retry: false });
  const alerts = data || [
    { equipment_id: "TRUCK-042", level: "critique", title: "Risque de panne élevé", message: "Probabilité estimée à 78%.", recommendation: "Inspection immédiate du train de roulement." },
    { equipment_id: "CRUSH-006", level: "moyen", title: "Vibrations excessives", message: "Tendance vibratoire en hausse.", recommendation: "Vérifier roulements et alignement." }
  ];
  return (
    <div className="space-y-6">
      <Header title="Alertes intelligentes" subtitle="Priorisation automatique selon probabilité de panne, RUL et seuils capteurs." />
      <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
        {alerts.map((alert, index) => (
          <section className="panel p-5" key={`${alert.equipment_id}-${index}`}>
            <div className="flex items-start gap-3">
              <AlertTriangle className={alert.level === "critique" ? "text-red-600" : "text-amber-600"} />
              <div>
                <span className={`px-2 py-1 rounded text-xs status-${alert.level}`}>{alert.level}</span>
                <h3 className="font-semibold mt-3">{alert.title}</h3>
                <p className="text-sm text-slate-600 mt-1">{alert.equipment_id} · {alert.message}</p>
                <p className="text-sm mt-3 font-medium">{alert.recommendation}</p>
              </div>
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
