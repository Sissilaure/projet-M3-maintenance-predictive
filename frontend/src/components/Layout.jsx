import { Activity, AlertTriangle, BarChart3, BrainCircuit, Gauge, History, MonitorCog, Wrench } from "lucide-react";

const nav = [
  ["dashboard", Gauge, "Dashboard"],
  ["monitoring", MonitorCog, "Monitoring"],
  ["alertes", AlertTriangle, "Alertes"],
  ["rul", Activity, "RUL"],
  ["analytics", BarChart3, "Analytics"],
  ["explainability", BrainCircuit, "IA explicable"],
  ["historique", History, "Historique"],
  
];

export function Layout({ page, setPage, children }) {
  return (
    <div className="min-h-screen grid grid-cols-1 lg:grid-cols-[260px_1fr]">
      <aside className="bg-coal text-white p-5 lg:min-h-screen">
        <div className="flex items-center gap-3 mb-8">
          <div className="h-10 w-10 grid place-items-center rounded bg-copper"><Wrench size={22} /></div>
          <div>
            <h1 className="text-xl font-bold">MinePredict</h1>
            <p className="text-xs text-slate-300">Maintenance prédictive minière</p>
          </div>
        </div>
        <nav className="grid gap-2">
          {nav.map(([id, Icon, label]) => (
            <button
              key={id}
              onClick={() => setPage(id)}
              className={`flex items-center gap-3 px-3 py-2 rounded text-left transition ${page === id ? "bg-white text-coal" : "text-slate-300 hover:bg-steel hover:text-white"}`}
              title={label}
            >
              <Icon size={18} />
              <span>{label}</span>
            </button>
          ))}
        </nav>
      </aside>
      <main className="p-4 md:p-8">
        {children}
      </main>
    </div>
  );
}
