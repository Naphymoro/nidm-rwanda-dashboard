export const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function parseResponse(res: Response) {
  const contentType = res.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await res.json() : await res.text();
  if (!res.ok) {
    const detail = typeof payload === "string" ? payload : payload?.detail || payload?.message || JSON.stringify(payload);
    throw new Error(detail || `API request failed with status ${res.status}`);
  }
  return payload;
}

export async function post(path: string, body: unknown) {
  const res = await fetch(`${API}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return parseResponse(res);
}

export async function get(path: string) {
  const res = await fetch(`${API}${path}`);
  return parseResponse(res);
}

export async function upload(path: string, formData: FormData) {
  const res = await fetch(`${API}${path}`, {
    method: "POST",
    body: formData,
  });
  return parseResponse(res);
}
