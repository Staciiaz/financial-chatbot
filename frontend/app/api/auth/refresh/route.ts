import { NextRequest, NextResponse } from "next/server";
import { getBackendHost } from "@/lib/backend";
import {
  ACCESS_TOKEN_COOKIE_NAME,
  REFRESH_TOKEN_COOKIE_NAME,
  getRefreshToken,
  sessionCookieOptions,
} from "@/lib/auth";

export async function POST(req: NextRequest) {
  const token = getRefreshToken();
  if (!token) {
    return NextResponse.json({ error: "Not authenticated." }, { status: 401 });
  }

  try {
    const backendRes = await fetch(`${getBackendHost()}/api/auth/refresh`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });

    const data = await backendRes.json().catch(() => ({}));

    if (!backendRes.ok) {
      return NextResponse.json(
        { error: data?.error || data?.message || "Token refresh failed." },
        { status: backendRes.status }
      );
    }

    const accessToken = data?.data?.access_token ?? data?.access_token;
    const refreshToken = data?.data?.refresh_token ?? data?.refresh_token;
    if (!accessToken || !refreshToken) {
      return NextResponse.json(
        { error: "Token refresh succeeded but no token was returned." },
        { status: 502 }
      );
    }

    const res = NextResponse.json({ success: true, expires_in: data?.data?.expires_in ?? data?.expires_in ?? null });
    res.cookies.set(ACCESS_TOKEN_COOKIE_NAME, accessToken, sessionCookieOptions);
    res.cookies.set(REFRESH_TOKEN_COOKIE_NAME, refreshToken, sessionCookieOptions);
    return res;
  } catch (err) {
    console.error("Refresh token proxy error:", err);
    return NextResponse.json(
      { error: "Could not reach the backend. Please try again." },
      { status: 502 }
    );
  }
}
