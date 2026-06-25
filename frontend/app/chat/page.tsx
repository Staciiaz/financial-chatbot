import { redirect } from "next/navigation";
import { getBackendToken, getStoredUsername } from "@/lib/auth";
import ChatClient from "./ChatClient";

export default function ChatPage() {
  const token = getBackendToken();
  if (!token) {
    redirect("/login");
  }

  const username = getStoredUsername() ?? "there";
  return <ChatClient username={username} />;
}
