import { Header } from "./Dashboard";
import { FeatureImportanceChart } from "../components/Charts";

export function Explainability() {
  return (
    <div className="space-y-6">
      <Header title="Explicabilité IA" subtitle="Facteurs globaux et explications locales pour rendre les décisions auditables." />
      <section className="panel p-5"><h2 className="font-semibold mb-4">Importance SHAP moyenne</h2><FeatureImportanceChart /></section>
      <section className="panel p-5">
        <h2 className="font-semibold mb-3">Exemple d’explication locale</h2>
        <div className="grid md:grid-cols-3 gap-3 text-sm">
          {["tool_wear élevé", "vibration_rate_change positif", "temperature_rolling_mean élevée"].map((item) => (
            <div key={item} className="border border-slate-200 rounded p-3 bg-slate-50">{item}</div>
          ))}
        </div>
      </section>
    </div>
  );
}
