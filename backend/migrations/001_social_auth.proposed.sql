-- PROPOSTA: revisar destino, tipos, privilégios e backup antes de aplicar.
-- Não é aplicada no startup nem no build. Não modifica tabelas compartilhadas.
BEGIN;
SELECT pg_advisory_xact_lock(hashtextextended('ssframework:migrations', 0));
CREATE TABLE public.ss_sessions (
    token_hash text PRIMARY KEY CHECK (length(token_hash) = 64),
    professional_id text NOT NULL REFERENCES public.profissionais_cadastrados(id),
    expires_at timestamptz NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ss_sessions_expiry ON public.ss_sessions(expires_at);
CREATE TABLE public.ss_login_attempts (
    attempt_key text PRIMARY KEY CHECK (length(attempt_key) = 64),
    failures integer NOT NULL CHECK (failures > 0),
    first_failure_at timestamptz NOT NULL,
    locked_until timestamptz
);
COMMIT;
