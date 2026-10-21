import { Alert } from "@mui/material";
import { requireSession } from "@/src/lib/server-api";
import { RegistrationList } from "@/src/features/registrations/registration-list";
export default async function RegistrationsPage() {
  const { actor } = await requireSession();
  return (
    <>
      <section className="surface">
        <p className="eyebrow">Bem-vindo ao Social Framework AC Social</p>
        <h1>Olá, {actor.name.split(" ")[0]}</h1>
        <p>Um espaço de cuidado, acolhimento e acompanhamento social.</p>
      </section>
      {actor.permissions.includes("registrations:read") ? (
        <RegistrationList />
      ) : (
        <section className="surface">
          <p className="eyebrow">Serviço Social</p>
          <h2>Acesso aos cadastros</h2>
          <Alert severity="info">
            O acesso aos dados do Serviço Social depende de autorização
            institucional específica.
          </Alert>
          {actor.isTechnology && (
            <p>
              Use o menu Status da conexão para consultar o diagnóstico
              autorizado.
            </p>
          )}
        </section>
      )}
    </>
  );
}
