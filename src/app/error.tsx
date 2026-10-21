"use client";
import { Alert, Button } from "@mui/material";
export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <main className="error-panel" id="conteudo">
      <Alert severity="error">Não foi possível carregar esta página.</Alert>
      <Button onClick={reset}>Tentar novamente</Button>
    </main>
  );
}
