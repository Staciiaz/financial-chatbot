import { NextResponse } from "next/server";
import { getBackendToken, getStoredUsername } from "@/lib/auth";

export async function GET() {
  const token = getBackendToken();
  if (!token) {
    return NextResponse.json({ authenticated: false }, { status: 401 });
  }
  return NextResponse.json({
    authenticated: true,
    username: getStoredUsername() ?? "there",
  });
}
