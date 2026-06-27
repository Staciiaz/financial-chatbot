import { NextResponse } from "next/server";
import { getBackendHost } from "@/lib/backend";
import {
  ACCESS_TOKEN_COOKIE_NAME,
  REFRESH_TOKEN_COOKIE_NAME,
  USERNAME_COOKIE_NAME,
  getRefreshToken,
  sessionCookieOptions,
  usernameCookieOptions,
} from "@/lib/auth";

const deleteCookieOptions = { maxAge: 0 };

function clearSessionCookies(res: NextResponse) {
  res.cookies.set(ACCESS_TOKEN_COOKIE_NAME, "", { ...sessionCookieOptions, ...deleteCookieOptions });
  res.cookies.set(REFRESH_TOKEN_COOKIE_NAME, "", { ...sessionCookieOptions, ...deleteCookieOptions });
  res.cookies.set(USERNAME_COOKIE_NAME, "", { ...usernameCookieOptions, ...deleteCookieOptions });
}

export async function POST() {
  const token = getRefreshToken();

  if (token) {
    try {
      await fetch(`${getBackendHost()}/api/auth/logout`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
    } catch (err) {
      console.error("Logout proxy error:", err);
    }
  }

  const res = NextResponse.json({ success: true });
  clearSessionCookies(res);
  return res;
}
