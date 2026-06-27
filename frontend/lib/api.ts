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

const TOKEN_EXPIRY_KEY = "token_expires_at";
// Refresh 30 seconds before actual expiry to avoid races.
const EXPIRY_BUFFER_MS = 30_000;

function storeTokenExpiry(expiresIn: number | null): void {
  if (typeof window === "undefined" || expiresIn == null) return;
  const expiresAt = Date.now() + expiresIn * 1000;
  localStorage.setItem(TOKEN_EXPIRY_KEY, String(expiresAt));
}

function isTokenExpired(): boolean {
  if (typeof window === "undefined") return false;
  const raw = localStorage.getItem(TOKEN_EXPIRY_KEY);
  if (!raw) return false;
  const expiresAt = Number(raw);
  if (!Number.isFinite(expiresAt)) {
    localStorage.removeItem(TOKEN_EXPIRY_KEY);
    return false;
  }
  return Date.now() >= expiresAt - EXPIRY_BUFFER_MS;
}

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

  const data = await res.json().catch(() => ({}));
  storeTokenExpiry(data?.expires_in);
}

export async function logoutRequest(): Promise<void> {
  await fetch("/api/auth/logout", { method: "POST" });
  if (typeof window !== "undefined") {
    localStorage.removeItem(TOKEN_EXPIRY_KEY);
  }
}

export async function refreshRequest(): Promise<void> {
  const res = await fetch("/api/auth/refresh", { method: "POST" });
  if (!res.ok) {
    throw new ApiError(await parseErrorMessage(res), res.status);
  }
  const data = await res.json().catch(() => ({}));
  storeTokenExpiry(data?.expires_in);
}

/**
 * Ensures the access token is fresh before executing `fn`.
 * If `fn` throws a 401 ApiError, refreshes once and retries.
 */
async function withAuthRefresh<T>(fn: () => Promise<T>): Promise<T> {
  if (isTokenExpired()) {
    await refreshRequest();
  }

  try {
    return await fn();
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) {
      await refreshRequest();
      return fn();
    }
    throw err;
  }
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
  return withAuthRefresh(async () => {
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
  });
}
