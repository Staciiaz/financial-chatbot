import { redirect } from "next/navigation";
import { getAccessToken, getStoredUsername } from "@/lib/auth";
import ChatClient from "./ChatClient";

export default function ChatPage() {
  const token = getAccessToken();
  if (!token) {
    redirect("/login");
  }

  const username = getStoredUsername() ?? "there";
  return <ChatClient username={username} />;
}
