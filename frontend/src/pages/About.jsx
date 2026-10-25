import { Card } from "../components/ui";

const P = ({ children }) => <p className="text-sm leading-relaxed text-slate-700">{children}</p>;

export default function About() {
  return (
    <div className="max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold text-navy-900">About & methodology</h1>
      <Card title="What RainSafe Pune does">
        <P>It brings historical rainfall analysis, an interactive map, a rule-based rainfall concern indicator and safety guidance into one website for Pune.</P>
      </Card>
      <Card title="Data">
        <P>Daily rainfall, temperature and wind for one Pune city-centre point (18.5204, 73.8567). History from 1 Jan 2020 to 31 Dec 2025 is a saved CSV from the Open-Meteo Historical Weather API. Days after that are fetched automatically from Open-Meteo (archive API, plus the forecast API’s recent past-days for the last few days) and refreshed about every 30 minutes; the “live conditions” box uses Open-Meteo’s current-conditions feed. If the live feed is unreachable the site falls back to the saved CSV and says so. The saved data is cleaned with Pandas: dates validated, duplicates removed, negative rainfall treated as missing. Missing values are never replaced with zero. All values are model-based estimates for a grid cell around that point, not official IMD rain-gauge records.</P>
      </Card>
      <Card title="How the statistics work">
        <P><b>Daily rainfall</b> is what fell on one day. The <b>3-day</b> and <b>7-day</b> totals add today and the previous days (a total is only calculated when every day in the window has data). Annual totals sum the days of a year; monthly averages average each calendar month over all years.</P>
      </Card>
      <Card title="How the indicator works">
        <P>Daily, 3-day and 7-day rainfall are compared with thresholds (Moderate: 35 / 60 / 100 mm; High: 64.5 / 100 / 150 mm). The highest level triggered becomes the category and the triggered rules are shown. The same input always gives the same result. The thresholds are <b>project-defined operational values</b>, not proven flood boundaries. Verify the IMD rainfall classes on the IMD website before quoting them.</P>
      </Card>
      <Card title="Why rainfall is not flood prediction">
        <P>Flooding also depends on drainage, terrain, river and dam levels, and how wet the ground already is. We have none of that data, so we cannot say any neighbourhood will flood. Map markers are representative points with approximate coordinates.</P>
      </Card>
      <Card title="Future improvements">
        <P>Recent-data feed, official IMD warnings, ward boundaries, elevation and drainage layers, and — only if credible incident records are found — a simple validated model.</P>
      </Card>
    </div>
  );
}
