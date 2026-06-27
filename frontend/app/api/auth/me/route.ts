import { NextResponse } from "next/server";
import { getAccessToken, getStoredUsername } from "@/lib/auth";

export async function GET() {
  const token = getAccessToken();
  if (!token) {
    return NextResponse.json({ authenticated: false }, { status: 401 });
  }
  return NextResponse.json({
    authenticated: true,
    username: getStoredUsername() ?? "there",
  });
}
