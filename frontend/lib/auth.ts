import { cookies } from "next/headers";

export const USERNAME_COOKIE_NAME = "username";
export const ACCESS_TOKEN_COOKIE_NAME = "user_access_token";
export const REFRESH_TOKEN_COOKIE_NAME = "user_refresh_token";

const SEVEN_DAYS_SECONDS = 60 * 60 * 24 * 7;

export const sessionCookieOptions = {
  httpOnly: true,
  secure: process.env.NODE_ENV === "production",
  sameSite: "lax" as const,
  path: "/",
  maxAge: SEVEN_DAYS_SECONDS,
};

// The username cookie is readable by client JS (not httpOnly) since it's
// only used for display ("Chatting as ..."), never for authorization.
export const usernameCookieOptions = {
  httpOnly: false,
  secure: process.env.NODE_ENV === "production",
  sameSite: "lax" as const,
  path: "/",
  maxAge: SEVEN_DAYS_SECONDS,
};

/**
 * Reads the backend auth token from the request's cookies.
 * Use only in Server Components, Route Handlers, or Server Actions.
 */
export function getAccessToken(): string | null {
  return cookies().get(ACCESS_TOKEN_COOKIE_NAME)?.value ?? null;
}

export function getRefreshToken(): string | null {
  return cookies().get(REFRESH_TOKEN_COOKIE_NAME)?.value ?? null;
}

export function getStoredUsername(): string | null {
  return cookies().get(USERNAME_COOKIE_NAME)?.value ?? null;
}
