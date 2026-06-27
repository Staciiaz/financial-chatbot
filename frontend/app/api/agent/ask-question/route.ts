import { NextRequest, NextResponse } from "next/server";
import { getBackendHost } from "@/lib/backend";
import { getAccessToken } from "@/lib/auth";

export const runtime = "nodejs";

export async function GET(req: NextRequest) {
  const token = getAccessToken();
  if (!token) {
    return NextResponse.json({ error: "Not authenticated." }, { status: 401 });
  }

  const question = req.nextUrl.searchParams.get("q");
  if (!question) {
    return NextResponse.json({ error: "Missing 'q' query parameter." }, { status: 400 });
  }

  let backendRes: Response;
  try {
    const url = new URL(`${getBackendHost()}/api/protected/agent/ask-question`);
    url.searchParams.set("q", question);

    backendRes = await fetch(url.toString(), {
      method: "GET",
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch (err) {
    console.error("Ask-question proxy fetch error:", err);
    return NextResponse.json(
      { error: "Could not reach the backend. Please try again." },
      { status: 502 }
    );
  }

  if (backendRes.status === 401) {
    return NextResponse.json({ error: "Session expired." }, { status: 401 });
  }

  if (!backendRes.ok || !backendRes.body) {
    const errorText = await backendRes.text().catch(() => "");
    return NextResponse.json(
      { error: errorText || "The backend returned an error." },
      { status: backendRes.status || 502 }
    );
  }

  // Pipe the backend's streamed plain-text body straight through to the browser.
  return new Response(backendRes.body, {
    status: 200,
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-cache",
    },
  });
}
