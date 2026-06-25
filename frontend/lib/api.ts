export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function parseErrorMessage(res: Response): Promise<string> {
  try {
    const data = await res.json();
    return data?.error || data?.message || `Request failed (${res.status}).`;
  } catch {
    return `Request failed (${res.status}).`;
  }
}

export interface RegisterPayload {
  username: string;
  password: string;
  company: string;
  sector: string;
}

export interface LoginPayload {
  username: string;
  password: string;
}

// All requests below hit this app's own Next.js API routes (same-origin),
// which proxy to the real backend server-side. No CORS, no backend host
// exposed to the browser, and the auth token lives in an httpOnly cookie
// set by the server rather than in client-side JS.

export async function registerRequest(payload: RegisterPayload): Promise<void> {
  const res = await fetch("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new ApiError(await parseErrorMessage(res), res.status);
  }
}

export async function loginRequest(payload: LoginPayload): Promise<void> {
  const res = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new ApiError(await parseErrorMessage(res), res.status);
  }
}

export async function logoutRequest(): Promise<void> {
  await fetch("/api/auth/logout", { method: "POST" });
}

/**
 * Calls ask-question and streams the plain-text response.
 * `onChunk` is called once per piece of text as it arrives over the network.
 * Resolves once the stream ends; returns the full concatenated answer.
 */
export async function askQuestionRequest(
  question: string,
  onChunk: (chunkText: string) => void
): Promise<string> {
  const url = new URL("/api/agent/ask-question", window.location.origin);
  url.searchParams.set("q", question);

  const res = await fetch(url.toString(), { method: "GET" });

  if (!res.ok) {
    throw new ApiError(await parseErrorMessage(res), res.status);
  }

  if (!res.body) {
    const text = await res.text();
    onChunk(text);
    return text;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let fullText = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunkText = decoder.decode(value, { stream: true });
    if (chunkText) {
      fullText += chunkText;
      onChunk(chunkText);
    }
  }

  return fullText;
}
