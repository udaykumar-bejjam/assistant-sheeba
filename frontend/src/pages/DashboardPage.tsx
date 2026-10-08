import { useQuery } from "@tanstack/react-query";
import { fetchCalls } from "../api";

export function DashboardPage() {
  const { data, isLoading } = useQuery({ queryKey: ["calls"], queryFn: fetchCalls });
  const items = data?.items ?? [];
  const today = new Date().toDateString();
  const todays = items.filter((c) => new Date(c.created_at).toDateString() === today);
  const transferred = todays.filter((c) => c.status === "TRANSFERRED").length;
  const spam = todays.filter((c) => c.intent === "SPAM").length;
  const avgDuration =
    todays.length === 0
      ? 0
      : Math.round(
          todays.reduce((sum, c) => sum + c.duration_seconds, 0) / todays.length,
        );

  return (
    <section>
      <h1>Dashboard</h1>
      <p className="lede">Live overview of Sheeba’s call handling for Uday.</p>
      {isLoading ? (
        <p className="lede">Loading…</p>
      ) : (
        <div className="metrics">
          <div className="metric">
            <strong>{todays.length}</strong>
            <span>Today’s calls</span>
          </div>
          <div className="metric">
            <strong>{todays.filter((c) => c.status === "COMPLETED").length}</strong>
            <span>AI handled</span>
          </div>
          <div className="metric">
            <strong>{transferred}</strong>
            <span>Transferred</span>
          </div>
          <div className="metric">
            <strong>{spam}</strong>
            <span>Spam calls</span>
          </div>
          <div className="metric">
            <strong>{avgDuration}s</strong>
            <span>Avg duration</span>
          </div>
        </div>
      )}
    </section>
  );
}
