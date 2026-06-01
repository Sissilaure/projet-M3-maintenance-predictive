export function KpiCard({ icon: Icon, label, value, tone = "normal", suffix = "" }) {
  const tones = {
    normal: "text-emerald-600 bg-emerald-50",
    warn: "text-amber-600 bg-amber-50",
    danger: "text-red-600 bg-red-50",
    info: "text-sky-600 bg-sky-50"
  };
  return (
    <section className="panel p-4">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm text-slate-500">{label}</p>
          <p className="text-2xl font-bold mt-1">{value}<span className="text-base text-slate-500">{suffix}</span></p>
        </div>
        <div className={`h-11 w-11 rounded grid place-items-center ${tones[tone]}`}>
          <Icon size={22} />
        </div>
      </div>
    </section>
  );
}
