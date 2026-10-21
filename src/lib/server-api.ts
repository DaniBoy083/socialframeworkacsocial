import "server-only";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import type { Session } from "@/src/features/auth/types";

export const backendUrl = () =>
  process.env.SOCIAL_API_URL || "http://127.0.0.1:8000";
export async function readSession(): Promise<Session | null> {
  const token = (await cookies()).get("ac_social_ss")?.value;
  if (!token) return null;
  const response = await fetch(`${backendUrl()}/api/v1/auth/session`, {
    headers: { Cookie: `ac_social_ss=${encodeURIComponent(token)}` },
    cache: "no-store",
    signal: AbortSignal.timeout(6000),
  });
  if (response.status === 401 || response.status === 403) return null;
  if (!response.ok) throw new Error("Institutional session unavailable");
  return response.json();
}
export async function requireSession() {
  let session: Session | null;
  try {
    session = await readSession();
  } catch {
    redirect("/login?estado=indisponivel");
  }
  if (!session) redirect("/login");
  return session;
}
