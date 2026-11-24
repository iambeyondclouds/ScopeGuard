
import { useEffect, useState } from "react";

const API = "http://127.0.0.1:8000";

function App() {
  const [task, setTask] = useState("Fix login bug");
  const [registered, setRegistered] = useState(false);
  const [action, setAction] = useState("read_file");
  const [target, setTarget] = useState("project/login.py");
  const [result, setResult] = useState(null);
  const [events, setEvents] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [policy, setPolicy] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function refreshData() {
    try {
      const [eventResponse, incidentResponse] = await Promise.all([
        fetch(`${API}/events`),
        fetch(`${API}/incidents`),
      ]);

      if (!eventResponse.ok || !incidentResponse.ok) {
        throw new Error("Could not load security data");
      }

      setEvents(await eventResponse.json());
      setIncidents(await incidentResponse.json());
      setError("");
    } catch (err) {
      setError("Cannot connect to ScopeGuard API. Is FastAPI running?");
    }
  }

  useEffect(() => {
    refreshData();
  }, []);

  async function registerTask(event) {
    event.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(`${API}/task`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task }),
      });

      const data = await response.json();

      if (!response.ok) throw new Error("Task registration failed");

      setPolicy(data.policy);
      setRegistered(true);
      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function executeAction(event) {
    event.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(`${API}/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, target }),
      });

      const data = await response.json();

      if (!response.ok) throw new Error("Action execution failed");

      setResult(data);
      await refreshData();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const blockedCount = events.filter(
    (event) => event.status === "blocked"
  ).length;

  const allowedCount = events.filter(
    (event) => event.status === "allowed"
  ).length;

  return (
    <main className="min-h-screen bg-[#080d18] text-slate-200">
      <header className="border-b border-slate-800 bg-[#0d1422] px-6 py-5">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-wide text-white">
              SCOPE<span className="text-cyan-400">GUARD</span>
            </h1>
            <p className="mt-1 text-xs tracking-[0.2em] text-slate-500">
              AI AGENT SECURITY & RUNTIME PROTECTION
            </p>
          </div>

          <div className="flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-400">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            API DASHBOARD
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl space-y-6 p-6">
        {error && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
            {error}
          </div>
        )}

        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Total Activities" value={events.length} />
          <StatCard title="Allowed Actions" value={allowedCount} color="text-emerald-400" />
          <StatCard title="Blocked Actions" value={blockedCount} color="text-red-400" />
          <StatCard title="Security Incidents" value={incidents.length} color="text-amber-400" />
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-xl border border-slate-800 bg-[#0d1422] p-6">
            <h2 className="mb-4 text-lg font-semibold text-white">
              Agent Task
            </h2>

            <form onSubmit={registerTask} className="space-y-4">
              <label className="block text-sm text-slate-400">
                Define the task and its intended scope
              </label>

              <input
                value={task}
                onChange={(e) => setTask(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-[#080d18] px-4 py-3 text-white outline-none focus:border-cyan-400"
                placeholder="Enter agent task"
                required
              />

              <button
                disabled={loading}
                className="rounded-lg bg-cyan-500 px-5 py-3 font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:opacity-50"
              >
                Register Task
              </button>
            </form>

            {policy && (
              <div className="mt-5 rounded-lg border border-slate-700 bg-[#080d18] p-4">
                <p className="mb-2 text-sm font-semibold text-cyan-400">
                  ACTIVE POLICY
                </p>
                <p className="text-sm text-slate-300">
                  Task: {policy.task}
                </p>
                <p className="mt-3 text-xs text-slate-500">
                  Allowed actions
                </p>
                <p className="mt-1 text-sm text-emerald-400">
                  {policy.allowed_actions?.join(", ")}
                </p>
                <p className="mt-3 text-xs text-slate-500">
                  Restricted actions
                </p>
                <p className="mt-1 text-sm text-red-400">
                  {policy.blocked_actions?.join(", ")}
                </p>
              </div>
            )}
          </div>

          <div className="rounded-xl border border-slate-800 bg-[#0d1422] p-6">
            <h2 className="mb-4 text-lg font-semibold text-white">
              Execute Agent Action
            </h2>

            <form onSubmit={executeAction} className="space-y-4">
              <label className="block text-sm text-slate-400">
                Operation
              </label>

              <select
                value={action}
                onChange={(e) => setAction(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-[#080d18] px-4 py-3 text-white outline-none focus:border-cyan-400"
              >
                <option value="read_file">Read file</option>
                <option value="write_file">Write file</option>
              </select>

              <label className="block text-sm text-slate-400">
                Target resource
              </label>

              <input
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-[#080d18] px-4 py-3 text-white outline-none focus:border-cyan-400"
                placeholder="project/login.py"
                required
              />

              <button
                disabled={!registered || loading}
                className="rounded-lg bg-violet-500 px-5 py-3 font-semibold text-white transition hover:bg-violet-400 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {loading ? "Processing..." : "Execute Action"}
              </button>
              {!registered && (
                <p className="text-xs text-amber-400">
                  Register a task before executing an action.
                </p>
              )}
            </form>

            {result && (
              <div className={`mt-5 rounded-lg border p-4 ${
                result.decision === "BLOCKED"
                  ? "border-red-500/30 bg-red-500/10"
                  : "border-emerald-500/30 bg-emerald-500/10"
              }`}>
                <p className={`font-bold ${
                  result.decision === "BLOCKED"
                    ? "text-red-400"
                    : "text-emerald-400"
                }`}>
                  {result.decision}
                </p>
                <p className="mt-2 text-sm text-slate-300">
                  {result.reason}
                </p>
              </div>
            )}
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <DataPanel title="Runtime Activity">
            {events.length === 0 ? (
              <EmptyState />
            ) : events.map((event) => (
              <div key={event.id} className="flex items-center justify-between gap-3 border-b border-slate-800 py-3 last:border-0">
                <div className="min-w-0">
                  <p className="text-sm text-white">{event.action}</p>
                  <p className="truncate text-xs text-slate-500">{event.target}</p>
                </div>
                <Status value={event.status} />
              </div>
            ))}
          </DataPanel>

          <DataPanel title="Security Incidents">
            {incidents.length === 0 ? (
              <EmptyState />
            ) : incidents.map((incident) => (
              <div key={incident.incident_id} className="border-b border-slate-800 py-3 last:border-0">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold text-white">
                    {incident.incident_id}
                  </p>
                  <span className="rounded bg-red-500/10 px-2 py-1 text-xs text-red-400">
                    {incident.severity}
                  </span>
                </div>
                <p className="mt-2 text-sm text-slate-300">
                  {incident.action}: {incident.target}
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  {incident.reason}
                </p>
              </div>
            ))}
          </DataPanel>
        </section>

        <div className="flex justify-end">
          <button
            onClick={refreshData}
            className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-cyan-400 hover:text-cyan-400"
          >
            Refresh Security Data
          </button>
        </div>
      </div>
    </main>
  );
}

function StatCard({ title, value, color = "text-white" }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-[#0d1422] p-5">
      <p className="text-sm text-slate-500">{title}</p>
      <p className={`mt-2 text-3xl font-bold ${color}`}>{value}</p>
    </div>
  );
}

function DataPanel({ title, children }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-[#0d1422] p-6">
      <h2 className="mb-4 text-lg font-semibold text-white">{title}</h2>
      {children}
    </div>
  );
}

function Status({ value }) {
  const allowed = value === "allowed";

  return (
    <span className={`shrink-0 rounded-full px-3 py-1 text-xs font-semibold ${
      allowed
        ? "bg-emerald-500/10 text-emerald-400"
        : "bg-red-500/10 text-red-400"
    }`}>
      {value?.toUpperCase()}
    </span>
  );
}

function EmptyState() {
  return (
    <p className="py-6 text-center text-sm text-slate-500">
      No records available yet.
    </p>
  );
}

export default App;

