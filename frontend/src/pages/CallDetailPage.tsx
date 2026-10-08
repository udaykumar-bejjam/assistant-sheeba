import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { fetchCall } from "../api";

export function CallDetailPage() {
  const { id = "" } = useParams();
  const { data, isLoading, error } = useQuery({
    queryKey: ["call", id],
    queryFn: () => fetchCall(id),
    enabled: Boolean(id),
  });

  return (
    <section>
      <h1>Call detail</h1>
      <p className="lede">Structured summary, outcome, and transcript references.</p>
      {isLoading && <p className="lede">Loading…</p>}
      {error && <p className="lede">Call not found.</p>}
      {data && (
        <div className="panel">
          <p>
            <strong>Caller:</strong> {(data.caller_name as string) || "Unknown"}
          </p>
          <p>
            <strong>Phone:</strong> {String(data.phone)}
          </p>
          <p>
            <strong>Status:</strong> {String(data.status)}
          </p>
          <p>
            <strong>Intent:</strong> {String(data.intent)} · <strong>Priority:</strong>{" "}
            {String(data.priority)}
          </p>
          {data.summary != null && (
            <pre style={{ whiteSpace: "pre-wrap", color: "var(--muted)" }}>
              {JSON.stringify(data.summary, null, 2)}
            </pre>
          )}
        </div>
      )}
    </section>
  );
}
