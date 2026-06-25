import { NextRequest, NextResponse } from "next/server";
import { getBackendHost } from "@/lib/backend";
import {
  SESSION_COOKIE_NAME,
  USERNAME_COOKIE_NAME,
  sessionCookieOptions,
  usernameCookieOptions,
} from "@/lib/auth";

export async function POST(req: NextRequest) {
  let body: { username?: string; password?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  try {
    const backendRes = await fetch(`${getBackendHost()}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await backendRes.json().catch(() => ({}));

    if (!backendRes.ok) {
      return NextResponse.json(
        { error: data?.error || data?.message || "Invalid username or password." },
        { status: backendRes.status }
      );
    }

    const token = data?.token;
    if (!token) {
      return NextResponse.json(
        { error: "Login succeeded but no token was returned." },
        { status: 502 }
      );
    }

    const res = NextResponse.json({ success: true });
    res.cookies.set(SESSION_COOKIE_NAME, token, sessionCookieOptions);
    if (body.username) {
      res.cookies.set(USERNAME_COOKIE_NAME, body.username, usernameCookieOptions);
    }
    return res;
  } catch (err) {
    console.error("Login proxy error:", err);
    return NextResponse.json(
      { error: "Could not reach the backend. Please try again." },
      { status: 502 }
    );
  }
}
