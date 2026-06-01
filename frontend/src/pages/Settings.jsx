import { useMutation } from "@tanstack/react-query";
import { Play } from "lucide-react";
import { trainModels } from "../api";
import { Header } from "./Dashboard";

export function Settings() {
  const mutation = useMutation({ mutationFn: trainModels });
  return (
    <div className="space-y-6">
      <Header title="Paramètres" subtitle="Configuration de démonstration, entraînement et état des modèles." />
      <section className="panel p-5">
        <button onClick={() => mutation.mutate()} className="inline-flex items-center gap-2 bg-coal text-white px-4 py-2 rounded hover:bg-steel" title="Entraîner les modèles">
          <Play size={18} /> Entraîner les modèles
        </button>
        {mutation.isPending && <p className="mt-4 text-slate-600">Entraînement en cours...</p>}
        {mutation.data && <pre className="mt-4 bg-slate-950 text-slate-100 p-4 rounded overflow-auto text-xs">{JSON.stringify(mutation.data, null, 2)}</pre>}
        {mutation.error && <p className="mt-4 text-red-600">{mutation.error.response?.data?.detail || mutation.error.message}</p>}
      </section>
    </div>
  );
}
