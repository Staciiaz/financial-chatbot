/**
 * Server-only backend host config. Do NOT prefix this with NEXT_PUBLIC_ —
 * it must never be exposed to the browser. Next.js API routes (which run
 * server-side, even inside the same Docker container as the frontend) read
 * this to reach the backend, e.g. http://backend:8000 in docker-compose,
 * or http://host.docker.internal:8000 if the backend runs outside Docker.
 */
export function getBackendHost(): string {
  const host = process.env.API_HOST;
  if (!host) {
    throw new Error(
      "API_HOST is not set. Add it to your environment (.env.local or docker-compose) — it should be the backend's address as seen from inside this server, e.g. http://backend:8000."
    );
  }
  // Render's fromService hostport gives a bare host[:port] without scheme.
  if (host.startsWith("http://") || host.startsWith("https://")) {
    return host;
  }
  return `https://${host}`;
}
