import { useState } from "react";
import { BookOpen, CloudRain, LayoutDashboard, LineChart, Map, Menu, ShieldAlert, X } from "lucide-react";
import Dashboard from "./pages/Dashboard";
import Analytics from "./pages/Analytics";
import RiskMap from "./pages/RiskMap";
import Advisories from "./pages/Advisories";
import About from "./pages/About";

const NAV = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "analytics", label: "Rainfall Analytics", icon: LineChart },
  { id: "map", label: "Risk Map", icon: Map },
  { id: "advisories", label: "Safety Advisories", icon: ShieldAlert },
  { id: "about", label: "About / Methodology", icon: BookOpen },
];

export default function App() {
  const [page, setPage] = useState("dashboard");
  const [open, setOpen] = useState(false);
  const go = (id) => { setPage(id); setOpen(false); window.scrollTo(0, 0); };

  return (
    <div className="min-h-screen md:flex">
      <div className="flex items-center justify-between bg-navy-900 p-4 text-white md:hidden">
        <Brand />
        <button onClick={() => setOpen(!open)} aria-label="Menu">{open ? <X /> : <Menu />}</button>
      </div>

      <aside className={`${open ? "block" : "hidden"} bg-navy-900 p-4 text-slate-200 md:sticky md:top-0 md:block md:h-screen md:w-64 md:shrink-0`}>
        <div className="mb-6 hidden md:block"><Brand /></div>
        <nav className="space-y-1">
          {NAV.map(({ id, label, icon: Icon }) => (
            <button key={id} onClick={() => go(id)}
              className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm ${page === id ? "bg-sky-500/20 text-white" : "hover:bg-white/10"}`}>
              <Icon size={18} /> {label}
            </button>
          ))}
        </nav>
        <p className="mt-8 hidden text-xs text-slate-400 md:block">Awareness tool. Not an official warning or flood forecast.</p>
      </aside>

      <main className="min-w-0 flex-1 p-4 md:p-8">
        {page === "dashboard" && <Dashboard go={go} />}
        {page === "analytics" && <Analytics />}
        {page === "map" && <RiskMap />}
        {page === "advisories" && <Advisories />}
        {page === "about" && <About />}
      </main>
    </div>
  );
}

const Brand = () => (
  <div className="flex items-center gap-2 text-lg font-bold text-white">
    <CloudRain className="text-sky-400" /> RainSafe Pune
  </div>
);
