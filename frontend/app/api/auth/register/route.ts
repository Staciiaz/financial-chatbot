import { NextRequest, NextResponse } from "next/server";
import { getBackendHost } from "@/lib/backend";

export async function POST(req: NextRequest) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  try {
    const backendRes = await fetch(`${getBackendHost()}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await backendRes.json().catch(() => ({}));

    if (!backendRes.ok) {
      return NextResponse.json(
        { error: data?.error || data?.message || "Registration failed." },
        { status: backendRes.status }
      );
    }

    return NextResponse.json(data, { status: backendRes.status });
  } catch (err) {
    console.error("Register proxy error:", err);
    return NextResponse.json(
      { error: "Could not reach the backend. Please try again." },
      { status: 502 }
    );
  }
}
