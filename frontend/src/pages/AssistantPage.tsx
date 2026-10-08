import { useQuery } from "@tanstack/react-query";
import { fetchAssistantSettings } from "../api";

export function AssistantPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["assistant"],
    queryFn: fetchAssistantSettings,
  });

  return (
    <section>
      <h1>Assistant settings</h1>
      <p className="lede">Identity, languages, transfer and recording policy for Sheeba.</p>
      {isLoading && <p className="lede">Loading…</p>}
      {data && (
        <div className="panel">
          <p>
            <strong>Name:</strong> {data.assistant_name}
          </p>
          <p>
            <strong>Owner:</strong> {data.owner_name}
          </p>
          <p>
            <strong>Greeting:</strong> {data.greeting}
          </p>
          <p>
            <strong>Prompt version:</strong> {data.prompt_version}
          </p>
          <p>
            <strong>Language:</strong> {data.preferred_language}
          </p>
          <p>
            <strong>Transfers:</strong> {data.transfer_enabled ? "Enabled" : "Disabled"}
          </p>
          <p>
            <strong>Recording:</strong> {data.recording_enabled ? "On" : "Off"} ·{" "}
            <strong>Transcription:</strong> {data.transcription_enabled ? "On" : "Off"}
          </p>
        </div>
      )}
    </section>
  );
}
