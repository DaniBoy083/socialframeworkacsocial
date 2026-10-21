import { AppShell } from "@/src/components/app-shell";
import { requireSession } from "@/src/lib/server-api";
export default async function InstitutionalLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { actor } = await requireSession();
  return <AppShell actor={actor}>{children}</AppShell>;
}
