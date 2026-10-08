import { useQuery } from "@tanstack/react-query";
import { fetchContacts } from "../api";

export function ContactsPage() {
  const { data, isLoading } = useQuery({ queryKey: ["contacts"], queryFn: fetchContacts });

  return (
    <section>
      <h1>Contacts</h1>
      <p className="lede">Known callers and handling preferences.</p>
      {isLoading ? (
        <p className="lede">Loading…</p>
      ) : (
        <div className="panel">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Phones</th>
                <th>Company</th>
                <th>Trusted</th>
                <th>Blocked</th>
              </tr>
            </thead>
            <tbody>
              {(data?.items ?? []).map((c) => (
                <tr key={String(c.id)}>
                  <td>{String(c.name)}</td>
                  <td>{(c.phones as string[] | undefined)?.join(", ")}</td>
                  <td>{String(c.company ?? "—")}</td>
                  <td>{c.is_trusted ? "Yes" : "No"}</td>
                  <td>{c.is_blocked ? "Yes" : "No"}</td>
                </tr>
              ))}
              {(data?.items?.length ?? 0) === 0 && (
                <tr>
                  <td colSpan={5}>No contacts yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
