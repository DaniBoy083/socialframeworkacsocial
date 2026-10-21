"use client";
import { useQuery } from "@tanstack/react-query";
import { Alert, CircularProgress } from "@mui/material";
import { api, apiMessage } from "@/src/lib/api-client";
export function AnalyticsPanel() {
  const query = useQuery({
    queryKey: ["analytics"],
    queryFn: async () =>
      (await api.get("/servico-social/analises/resumo")).data,
  });
  if (query.isPending)
    return <CircularProgress aria-label="Carregando indicadores" size={28} />;
  if (query.isError)
    return <Alert severity="info">{apiMessage(query.error)}</Alert>;
  return (
    <Alert severity="info">
      Os indicadores serão apresentados após a homologação da integração.
    </Alert>
  );
}
