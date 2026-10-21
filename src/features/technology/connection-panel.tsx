"use client";
import { useQuery } from "@tanstack/react-query";
import {
  Alert,
  Button,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
} from "@mui/material";
import { api, apiMessage } from "@/src/lib/api-client";
type Status = {
  database: string;
  authTablesPresent: boolean;
  identityContractVerified: boolean;
  socialRecordsReady: boolean;
  storageReady: boolean;
  latencyMs: number;
  accessPolicyApproved: boolean;
};
export function ConnectionPanel() {
  const query = useQuery({
    queryKey: ["connection"],
    queryFn: async () => (await api.get<Status>("/tecnologia/conexao")).data,
  });
  if (query.isPending)
    return <CircularProgress aria-label="Verificando integrações" size={28} />;
  if (query.isError)
    return (
      <Alert
        severity="error"
        action={
          <Button color="inherit" onClick={() => query.refetch()}>
            Tentar novamente
          </Button>
        }
      >
        {apiMessage(query.error)}
      </Alert>
    );
  const data = query.data;
  return (
    <>
      <List>
        {[
          ["Banco institucional", data.database === "connected"],
          ["Tabelas de autenticação", data.authTablesPresent],
          ["Contrato cadastral homologado", data.identityContractVerified],
          ["Política de acesso aprovada", data.accessPolicyApproved],
          ["Cadastros do Serviço Social", data.socialRecordsReady],
          ["Armazenamento privado", data.storageReady],
        ].map(([label, ready]) => (
          <ListItem key={String(label)} divider>
            <ListItemText
              primary={label}
              secondary={
                ready ? "Disponível" : "Aguardando configuração ou validação"
              }
            />
          </ListItem>
        ))}
      </List>
      <p>Tempo da verificação: {data.latencyMs} ms</p>
      <Button variant="outlined" onClick={() => query.refetch()}>
        Atualizar diagnóstico
      </Button>
    </>
  );
}
