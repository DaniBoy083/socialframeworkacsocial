import { notFound } from "next/navigation";
import { Alert } from "@mui/material";
import { requireSession } from "@/src/lib/server-api";
import { ConnectionPanel } from "@/src/features/technology/connection-panel";
export default async function ConnectionPage() {
  const { actor } = await requireSession();
  if (!actor.isTechnology) notFound();
  return (
    <section className="surface">
      <p className="eyebrow">Tecnologia</p>
      <h1>Status da conexão</h1>
      <p>Diagnóstico das integrações institucionais.</p>
      {actor.isTechnology ? (
        <ConnectionPanel />
      ) : (
        <Alert severity="error">Acesso exclusivo da equipe Tecnologia.</Alert>
      )}
    </section>
  );
}
