import { redirect } from "next/navigation";
import { getAccessToken } from "@/lib/auth";

export default function Home() {
  const token = getAccessToken();
  redirect(token ? "/chat" : "/login");
}
