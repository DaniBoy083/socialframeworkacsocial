# Banco e contratos

Referência: ACS-IDENTITY-1. Inspeção em 21/10/2026 exclusivamente em `information_schema.columns`, transação READ ONLY, com timeout. Não foram consultadas pessoas, credenciais, nomes de equipes, catálogo de serviços ou dados clínicos. Não foi executado DDL/DML no banco institucional.

## Estrutura efetivamente conferida

| Origem | Evidência de estrutura | Tratamento |
|---|---|---|
| `public.profissionais_cadastrados` | `id text`, `email text`, `password text`, `display_name text`; demais campos institucionais presentes | ID do operador é texto; preservar sem converter para UUID nem copiar senha |
| `public.equipes_profissionais` | `id text`, `name text`, `professional_ids_json jsonb`, `tools_json jsonb` | Equipe resolvida pelo ID do profissional; `tools_json` não autoriza |
| `public.institutional_users` | `id uuid`, `clinic_id uuid`, `full_name text`, `birth_date date`, `responsible_contact text`, `version integer`, datas `timestamptz` | Pessoa atendida tem identidade distinta do operador |
| `institutional_frameworks` | `code`, `name`, `available` | Disponibilidade do catálogo não representa autorização |
| `institutional_user_services` | `user_id uuid`, `clinic_id uuid`, `framework_code text`, `record_id uuid`, datas | Vínculo específico do serviço; nunca copiar prontuário ABA |
| `institutional_user_events` | IDs UUID, código, tipo e data | Não consultar nem publicar história clínica nesta etapa |
| `ss_sessions`, `ss_login_attempts` | Ausentes na inspeção | Login real indisponível até migração revisada |

O contrato documental tratava o operador como identidade institucional; a inspeção esclareceu seu tipo físico `text`. A proposta de autenticação usa FK de texto. Não presumir que os valores sejam UUIDs válidos.

## Limites da evidência

A inspeção não certifica FKs, triggers, grants, ICU, isolamento de rede, backups, conteúdo do catálogo nem política de acesso. O diagnóstico da aplicação confere apenas presença das tabelas de integração; não substitui a certificação ACS-IDENTITY-1. A disponibilidade real de `ssframework` não foi consultada ou alterada; o documento recebido o declara planejado/indisponível.

Os arquivos `005_shared_registry.sql`, `passwordHash.ts`, adaptadores ABA, evidências operacionais e guias arquiteturais citados no documento de integração não foram fornecidos neste workspace. Não copiar tabelas de sessões/comandos ABA nem criar uma segunda base de pessoas.

## Proposta de estruturas próprias

`backend/migrations/001_social_auth.proposed.sql` cria somente `ss_sessions` e `ss_login_attempts`, com lock e transação, sem modificar tabelas institucionais. Está **não aplicada e não aprovada para produção**. A convenção de migrações e a retenção de sessões/tentativas ainda precisam de revisão. Não há comando de migração automática. A migração é de execução única; uma eventual reexecução exige histórico/versionamento, não repetição cega.

Sessões armazenam ID institucional do operador e hash do token, sem senha. Tentativas armazenam hash do e-mail como chave, contador, primeira falha e bloqueio. Cinco falhas na janela de 15 minutos bloqueiam a conta por 15 minutos. Não se confia em IP fornecido por cabeçalhos arbitrários; proteção global no proxy ainda precisa de configuração.

## Consultas de identidade preparadas

Busca com nome normalizado ou UUID, filtro obrigatório `clinic_id` confiável e paginação máxima de 50 (51 lidos para calcular `hasMore`). SQL parametrizado, curingas escapados e ordem por nome/ID. O contato institucional continua texto livre: nunca extrair telefone por heurística ou usar como chave de pessoa. A futura ficha terá telefone próprio normalizado.

Escritas sociais exigem contrato físico próprio, FK composta `(id,clinic_id)`, ID raiz igual ao UUID institucional, versões separadas da identidade, idempotência por ator/conteúdo, transação única e proveniência mínima. Nenhuma dessas estruturas sociais foi criada por inferência.
