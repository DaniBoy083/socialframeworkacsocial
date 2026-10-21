"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Alert, Button, CircularProgress, TextField } from "@mui/material";
import { FiPlus, FiSearch, FiUsers } from "react-icons/fi";
import { api, apiMessage } from "@/src/lib/api-client";
import { RegistrationTable, type Registration } from "./registration-table";
import { RegistrationModelDialog } from "./registration-model-dialog";

export function RegistrationList() {
  const [search, setSearch] = useState("");
  const [submitted, setSubmitted] = useState("");
  const [page, setPage] = useState(0);
  const [modelOpen, setModelOpen] = useState(false);
  const query = useQuery({
    queryKey: ["registrations", submitted, page],
    queryFn: async () =>
      (
        await api.get<{ items: Registration[]; hasMore: boolean }>(
          "/servico-social/cadastros",
          { params: { busca: submitted, offset: page * 50 } },
        )
      ).data,
  });
  return (
    <section className="surface">
      <div className="toolbar">
        <div>
          <p className="eyebrow">Acompanhamento social</p>
          <h2>Cadastros</h2>
          <p>Localize e acompanhe as pessoas atendidas pelo Serviço Social.</p>
        </div>
        <Button
          variant="contained"
          startIcon={<FiPlus />}
          onClick={() => setModelOpen(true)}
        >
          Novo cadastro
        </Button>
      </div>
      <form
        className="toolbar"
        onSubmit={(event) => {
          event.preventDefault();
          setSubmitted(search.trim());
          setPage(0);
        }}
      >
        <TextField
          label="Buscar por nome ou ID institucional"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          sx={{ flex: 1, minWidth: 180 }}
        />
        <Button type="submit" variant="outlined" startIcon={<FiSearch />}>
          Buscar
        </Button>
      </form>
      {query.isPending && (
        <div className="empty-state" role="status">
          <CircularProgress size={28} />
          <p>Carregando cadastros…</p>
        </div>
      )}
      {query.isError && (
        <Alert
          severity="error"
          sx={{ mt: 3 }}
          action={
            <Button color="inherit" onClick={() => query.refetch()}>
              Tentar novamente
            </Button>
          }
        >
          {apiMessage(query.error)}
        </Alert>
      )}
      {!query.isError &&
        query.data &&
        (query.data.items.length ? (
          <>
            <RegistrationTable items={query.data.items} />
            <div className="toolbar">
              <Button disabled={!page} onClick={() => setPage(page - 1)}>
                Anterior
              </Button>
              <span>Página {page + 1}</span>
              <Button
                disabled={!query.data.hasMore}
                onClick={() => setPage(page + 1)}
              >
                Próxima
              </Button>
            </div>
          </>
        ) : (
          <div className="empty-state">
            <FiUsers aria-hidden />
            <h2>Nenhum cadastro encontrado</h2>
            <p>Inicie um novo cadastro ou ajuste a busca.</p>
            <Button
              variant="contained"
              startIcon={<FiPlus />}
              onClick={() => setModelOpen(true)}
            >
              Novo cadastro
            </Button>
          </div>
        ))}
      <RegistrationModelDialog
        open={modelOpen}
        onClose={() => setModelOpen(false)}
      />
    </section>
  );
}
