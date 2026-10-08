const API_BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ?? "";
const API = `${API_BASE}/api/v1`;

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API}${path}`);
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export type CallListItem = {
  id: string;
  status: string;
  phone: string;
  caller_name: string | null;
  intent: string;
  priority: string;
  created_at: string;
  duration_seconds: number;
};

export type AssistantSettings = {
  assistant_name: string;
  owner_name: string;
  greeting: string;
  prompt_version: string;
  preferred_language: string;
  transfer_enabled: boolean;
  recording_enabled: boolean;
  transcription_enabled: boolean;
};

export function fetchCalls() {
  return getJson<{ items: CallListItem[] }>("/calls");
}

export function fetchCall(id: string) {
  return getJson<Record<string, unknown>>(`/calls/${id}`);
}

export function fetchAssistantSettings() {
  return getJson<AssistantSettings>("/assistant/settings");
}

export function fetchContacts() {
  return getJson<{ items: Array<Record<string, unknown>> }>("/contacts");
}
