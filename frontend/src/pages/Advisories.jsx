import { api } from "../services/api";
import { Async, Card, RiskBadge, useApi } from "../components/ui";

export default function Advisories() {
  const res = useApi(api.advisories, []);
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-navy-900">Safety advisories</h1>
      <p className="max-w-3xl text-sm text-slate-600">
        General precautions linked to each rainfall concern level. These are <b>not</b> official alerts. For real
        warnings follow IMD and Pune Municipal Corporation announcements.
      </p>
      <Async res={res}>
        {(d) => (
          <div className="grid gap-6 md:grid-cols-3">
            {Object.entries(d.by_category).map(([cat, items]) => (
              <Card key={cat}>
                <RiskBadge category={cat} label={`${cat[0].toUpperCase() + cat.slice(1)} concern`} />
                <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-slate-700">
                  {items.map((t) => <li key={t}>{t}</li>)}
                </ul>
              </Card>
            ))}
          </div>
        )}
      </Async>
    </div>
  );
}
