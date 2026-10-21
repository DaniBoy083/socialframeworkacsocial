import { notFound } from "next/navigation";
import { Alert } from "@mui/material";
import { requireSession } from "@/src/lib/server-api";
import { AnalyticsPanel } from "@/src/features/analytics/analytics-panel";
export default async function AnalyticsPage() {
  const { actor } = await requireSession();
  if (!actor.permissions.includes("analytics:read")) notFound();
  return (
    <section className="surface">
      <p className="eyebrow">Serviço Social</p>
      <h1>Análise de dados</h1>
      <p>Indicadores agregados para acompanhar o atendimento.</p>
      {actor.permissions.includes("analytics:read") ? (
        <AnalyticsPanel />
      ) : (
        <Alert severity="error">
          Você não tem permissão para acessar este módulo.
        </Alert>
      )}
    </section>
  );
}
