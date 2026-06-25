import { redirect } from "next/navigation";
import { getBackendToken } from "@/lib/auth";

export default function Home() {
  const token = getBackendToken();
  redirect(token ? "/chat" : "/login");
}
