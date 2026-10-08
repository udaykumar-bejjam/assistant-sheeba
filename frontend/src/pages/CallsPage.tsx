import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { fetchCalls } from "../api";

export function CallsPage() {
  const { data, isLoading, error } = useQuery({ queryKey: ["calls"], queryFn: fetchCalls });

  return (
    <section>
      <h1>Calls</h1>
      <p className="lede">Recent inbound conversations handled by Sheeba.</p>
      {isLoading && <p className="lede">Loading…</p>}
      {error && <p className="lede">Could not load calls. Is the API running?</p>}
      {data && (
        <div className="panel">
          <table>
            <thead>
              <tr>
                <th>Caller</th>
                <th>Phone</th>
                <th>Status</th>
                <th>Intent</th>
                <th>Priority</th>
                <th>Duration</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((call) => (
                <tr key={call.id}>
                  <td>
                    <Link to={`/calls/${call.id}`}>{call.caller_name ?? "Unknown"}</Link>
                  </td>
                  <td>{call.phone}</td>
                  <td>
                    <span className="badge">{call.status}</span>
                  </td>
                  <td>{call.intent}</td>
                  <td>
                    <span className="badge warn">{call.priority}</span>
                  </td>
                  <td>{call.duration_seconds}s</td>
                </tr>
              ))}
              {data.items.length === 0 && (
                <tr>
                  <td colSpan={6}>No calls yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
