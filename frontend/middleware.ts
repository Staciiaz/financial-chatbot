import { NextRequest, NextResponse } from "next/server";

const SESSION_COOKIE_NAME = "backend_token";

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;
  const token = req.cookies.get(SESSION_COOKIE_NAME)?.value;

  const isAuthPage = pathname === "/login" || pathname === "/register";
  const isProtectedPage = pathname === "/chat";

  if (isProtectedPage && !token) {
    return NextResponse.redirect(new URL("/login", req.url));
  }

  if (isAuthPage && token) {
    return NextResponse.redirect(new URL("/chat", req.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/chat", "/login", "/register"],
};
