import { Header } from "./Dashboard";
import { ConfusionMatrix, FeatureImportanceChart, TimeChart } from "../components/Charts";

export function Analytics() {
  return (
    <div className="space-y-6">
      <Header title="Analytics" subtitle="Comparaison des modèles, matrices de confusion, importance des variables et tendances capteurs." />
      <div className="grid xl:grid-cols-2 gap-4">
        <section className="panel p-5"><h2 className="font-semibold mb-4">Feature importance</h2><FeatureImportanceChart /></section>
        <section className="panel p-5"><h2 className="font-semibold mb-4">Matrice de confusion</h2><ConfusionMatrix /></section>
      </div>
      <section className="panel p-5"><h2 className="font-semibold mb-4">Courbes temporelles</h2><TimeChart /></section>
    </div>
  );
}
