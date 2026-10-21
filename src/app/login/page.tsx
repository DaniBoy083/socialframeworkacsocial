import type { Metadata } from "next";
import { LoginForm } from "@/src/features/auth/login-form";
export const metadata: Metadata = { title: "Acesso institucional" };
export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ estado?: string }>;
}) {
  const params = await searchParams;
  return <LoginForm unavailable={params.estado === "indisponivel"} />;
}
