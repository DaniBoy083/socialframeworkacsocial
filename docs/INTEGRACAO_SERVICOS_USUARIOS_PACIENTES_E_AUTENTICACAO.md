# Integração entre serviços — usuários, pacientes e autenticação institucional

Versão do contrato de cadastro: **ACS-IDENTITY-1**. Revisão documental: **20/10/2026**, America/Sao_Paulo. Este documento reúne a base para integrar outras aplicações da AC Social ao cadastro de pessoas e ao login institucional existentes. A ampliação da documentação não altera o contrato, o código, as permissões ou o banco.

Use este guia junto das migrações e dos adaptadores citados ao preparar outro workspace. O módulo de recepção não recebe nova tela, papel, acesso ou histórico por este contrato; o framework responsável gerenciará essas informações.

## Guia de consulta

- [Identidades e IDs](#objetivo-e-vocabulário): diferença entre paciente, profissional e conta de login.
- [Banco e estado de referência](#banco-existente-e-estado-de-referência): tabelas, migrações e limites da evidência disponível.
- [Autenticação institucional](#autenticação-institucional-por-login-senha-e-equipe-indireta): credenciais, equipe automática, autorização e sessões.
- [Relação de pessoas e serviços](#consulta-dos-usuáriospacientes-existentes-por-id): consulta por UUID e APIs disponíveis.
- [Dados comuns](#dados-comuns-campos-do-cadastro), [tabelas comuns](#tabelas-comuns) e [cadastro](#fluxo-de-cadastro-e-prevenção-de-identidade-incorreta): implementação do cadastro compartilhado.
- [Migração e publicação](#migração-e-publicação) e [adoção em outro serviço](#roteiro-para-integrar-uma-nova-aplicação): preparação e verificação da integração.

## Objetivo e vocabulário

Uma pessoa atendida possui **um UUID institucional**, reutilizado pelos prontuários dos serviços. O ABA usa esse ID; o futuro `ssframework` deve usar o mesmo ID. Ciclos, sessões, documentos e atividades têm IDs próprios, mas sempre referenciam a pessoa institucional.

“Usuário institucional” aqui significa pessoa atendida/beneficiário. Não é conta de login. `profissionais_cadastrados.id`, `aba_professionals.id` e o ID do ator autenticado identificam profissionais; nunca devem ser usados como ID do paciente por coincidência de nome.

O banco central é a fonte da identificação. Cada framework mantém seus próprios dados específicos e permissões. Identificar a mesma pessoa não concede acesso aos seus prontuários em outros serviços.

| Identidade | Fonte / relação | Uso |
|---|---|---|
| Pessoa atendida / usuário / paciente | `institutional_users.id` | Identificação compartilhada entre serviços; não autentica no login atual |
| Prontuário raiz ABA | `aba_patients.id = institutional_users.id` | Dados clínicos ABA da mesma pessoa |
| Profissional / operador autenticado | `public.profissionais_cadastrados.id` | Identidade de quem entra e executa ações |
| Espelho operacional do profissional ABA | `aba_professionals.id = profissionais_cadastrados.id` | Sessões, vínculos e auditoria ABA |
| Equipe institucional | `equipes_profissionais.id`; associação em `professional_ids_json` | Autoriza o profissional conforme a política do serviço |

Os IDs de pessoa e de profissional pertencem a cadastros distintos. Não relacioná-los por igualdade de nome ou e-mail. O login atual é destinado aos profissionais; um eventual portal de pacientes precisa de contrato próprio de conta, credenciais e autorização, sem usar o UUID do paciente como senha.

## Topologia obrigatória

As tabelas comuns e os anexos devem estar no **mesmo banco PostgreSQL autorizado**, mesmo schema `public` e mesmo escopo institucional `clinic_id`. Cada workspace pode ser um projeto diferente, mas não deve criar uma cópia independente do cadastro central em outra database/branch Neon.

`clinic_id` identifica o escopo institucional, não o serviço. Não inventar um `clinic_id` novo para cada framework. O UUID da pessoa é globalmente único neste banco e pertence a esse escopo. A separação entre escopos é validada também pelas FKs compostas.

Se os projetos usarem bancos separados, este contrato precisa de um serviço central autenticado de identidade. FKs entre databases não são implementadas por este padrão. Não substituir isso por cruzamento de nomes, cópia de credenciais, cookies compartilhados ou requisições anônimas.

## Banco existente e estado de referência

Esta revisão foi conferida contra os arquivos da `main` local, com base no commit `b021124`. **Não foi feita nova consulta ao banco nesta revisão documental.** As tabelas e regras abaixo descrevem o contrato exigido pelo código; não são uma exportação dos registros atuais nem comprovam que qualquer outro ambiente esteja atualizado.

| Grupo | Tabelas no schema `public` | Responsabilidade |
|---|---|---|
| Origem institucional existente | `profissionais_cadastrados`, `equipes_profissionais` | Credenciais, identidade e associação de profissionais às equipes |
| Cadastro compartilhado | `institutional_users`, `institutional_frameworks`, `institutional_user_services`, `institutional_user_events` | Pessoas atendidas, catálogo, vínculos entre serviços e proveniência administrativa |
| Autenticação operacional ABA | `aba_professionals`, `aba_sessions`, `aba_login_attempts` | Espelho institucional, sessões e limitação persistente de tentativas |
| Atendimento ABA | `aba_patients`, `aba_links`, `aba_references`, `aba_events`, `aba_commands`, `aba_tasks`, `aba_signature_documents` | Prontuários, profissionais vinculados, referências, auditoria, comandos, cálculos e assinaturas |

O contrato de readiness atual exige **16 tabelas, dez triggers ativos e a FK composta validada** `aba_patients(id, clinic_id) → institutional_users(id, clinic_id)`. A lista executável está em [`databaseSchema.ts`](../src/modules/aba/infrastructure/databaseSchema.ts); tabelas presentes sem os invariantes não representam schema pronto.

As migrações ABA 001–007 estão versionadas em [`migrations/`](../src/modules/aba/infrastructure/migrations). As tabelas institucionais `profissionais_cadastrados` e `equipes_profissionais` são preexistentes: essas migrações não criam nem substituem o cadastro institucional de login.

A evidência operacional mais recente consultada é de **19/10/2026**: aplicação isolada da 007, seguida de `aba:check` aprovado, sem tabelas ou invariantes ausentes. A aplicação das migrações 005/006 está registrada em 14/10/2026. Publicação e homologação são verificações separadas. Consulte [operação de produção](OPERACAO_PRODUCAO.md) e [evidências cadastrais](EVIDENCIAS_DEPLOY_CADASTRO_2026-10-14.md) antes de usar esses resultados como referência para um destino específico.

Para conferir o destino sem alterar dados, com as dependências instaladas e o ambiente correto configurado:

```powershell
npm.cmd run aba:check
node scripts/diagnose-auth.mjs
```

O primeiro comando verifica schema e invariantes. O segundo executa diagnóstico de autenticação em transação somente leitura e informa contagens, compatibilidade de formato de senha e permissões operacionais; não testa a senha de uma pessoa nem publica nomes, hashes ou credenciais. O código também aceita um e-mail para diagnóstico direcionado. Uma contagem de membros de equipes permitidas não comprova, sozinha, papel clínico reconhecido ou login bem-sucedido.

## Autenticação institucional por login, senha e equipe indireta

### O que a pessoa informa

O **login atual é o e-mail institucional**. A pessoa informa somente e-mail e senha. Não seleciona equipe, cargo, permissões ou `clinic_id`; o servidor obtém esses dados das fontes institucionais e da configuração do serviço.

O cliente ABA envia `email`, `password` e o marcador fixo `userType: "atendimento"`. Esse marcador não é equipe nem autorização. A rota de login usa e-mail e senha para autenticar e não confia em equipe, cargo ou permissões enviados pelo navegador.

### Fontes existentes e campos consumidos

| Origem | Campos usados pelo adaptador atual | Finalidade |
|---|---|---|
| `public.profissionais_cadastrados` | `id`, `email`, `password`, `display_name`, `user_type`, `services_json`, `assigned_functions_json` | Identidade, verificação de senha e definição do papel após confirmar a equipe |
| `public.equipes_profissionais` | `id`, `name`, `professional_ids_json`; a consulta também lê `tools_json` | Associação do profissional à equipe; `tools_json` não concede acesso na política ABA atual |
| `aba_professionals` | `id`, `clinic_id`, `name`, `email`, `role`, `password_hash`, `active`, `team`, campos de bloqueio | Espelho operacional do profissional, subordinado à origem institucional |
| `aba_sessions` | `token_hash`, `professional_id`, `expires_at` | Sessão opaca persistida no backend ABA |
| `aba_login_attempts` | `attempt_key`, `failures`, `first_failure_at`, `locked_until` | Proteção persistente contra repetição de tentativas |

Esses são os campos consumidos pelo código, não uma descrição de todas as colunas existentes no banco. `profissionais_cadastrados.password` contém o hash utilizado pelo verificador; não deve conter a senha em texto puro. Campos de atividade/bloqueio do espelho não devem ser apresentados como se fossem colunas ou verificações da origem institucional.

### Fluxo obrigatório no servidor

1. Validar origem da requisição, disponibilidade da configuração, corpo e limites de tentativas.
2. Localizar o profissional em `public.profissionais_cadastrados` por `lower(email)=lower($1)`, com parâmetro SQL. O servidor remove espaços externos do e-mail recebido; não transforma a senha.
3. Consultar `public.equipes_profissionais` usando o **ID do profissional encontrado**, pela associação `professional_ids_json @> to_jsonb(ARRAY[$1]::text[])`. O parâmetro dessa consulta é o ID institucional, não o e-mail e não o ID do paciente.
4. Resolver a equipe autorizada e o papel conforme a política do serviço. E-mail válido, nome de função ou serviço listado no cadastro não substituem associação a uma equipe autorizada.
5. Verificar a senha informada contra o hash institucional. No ABA, ausência de acesso ou senha incorreta recusa o login.
6. Criar/atualizar o espelho operacional preservando o ID institucional. No ABA: `aba_professionals.id = profissionais_cadastrados.id`; nome, e-mail, papel, hash e equipe vêm da origem, e `clinic_id` vem da configuração confiável.
7. Emitir a sessão do serviço, confirmar a sessão no cliente antes de redirecionar e validar autorização nas operações seguintes.

Assim, a equipe participa da autorização de forma **indireta e automática**. Não existe um terceiro campo de equipe que o usuário precise preencher. Pertencer à equipe não substitui a verificação da senha.

### Política atualmente implementada no ABA

| Equipe confirmada no banco | Regra de papel | Resultado |
|---|---|---|
| `Tecnologia` | Associação à equipe | Operação administrativa; não recebe poderes clínicos ou de AT |
| `Equipe ABA` | Texto reconhecido como Psicologia | `PSICOLOGO` |
| `Equipe ABA` | Texto reconhecido como Psicopedagogia | `PSICOPEDAGOGO` |
| `Equipe ABA` | Texto reconhecido como Terapia ABA | `TERAPIA_ABA` |
| Outra equipe ou nenhuma equipe permitida | Qualquer função informada | Acesso ABA negado |
| `Equipe ABA` sem função reconhecida | Inclusive apoio pedagógico isolado | Acesso ABA negado |

O adaptador procura funções em `user_type`, `services_json` e `assigned_functions_json`, normalizando acentos/caixa para a comparação. A prioridade de papéis é Psicologia, Psicopedagogia e Terapia ABA. Os nomes de equipe permitidos são comparados exatamente com `Tecnologia` e `Equipe ABA`; se ambas estiverem presentes, Tecnologia tem prioridade. O código armazena `role: "TERAPIA_ABA"` no espelho de Tecnologia por compatibilidade, mas a equipe limita as permissões: isso não torna o operador um profissional clínico.

Ações clínicas continuam exigindo o vínculo apropriado com o paciente. Acesso ao cadastro compartilhado é permitido para Tecnologia ou Coordenação da Equipe ABA (`PSICOLOGO`/`PSICOPEDAGOGO`), não para toda conta autenticada.

Outro serviço deve declarar sua própria política de equipes e papéis com base nas associações reais do mesmo banco. Não copiar automaticamente a lista de equipes ABA como política de Serviço Social, Recepção ou outro módulo; não conceder acesso apenas porque a pessoa conseguiu autenticar em outro aplicativo.

### Senhas e compatibilidade

O verificador atual usa **scrypt**, no formato `salt:hash_hex`, derivando 64 bytes e comparando os bytes com `timingSafeEqual`. Reutilizar a implementação em [`passwordHash.ts`](../src/modules/auth/application/passwordHash.ts), ou uma implementação comprovadamente compatível, sem alterar a senha institucional durante o login. Não aplicar caixa alta, remoção de espaços ou normalização cadastral à senha.

O formulário exige senha preenchida e limita a 512 caracteres; não impõe mínimo de seis caracteres a uma credencial já existente. Política de criação/troca de senha é uma operação separada. Formato incompatível exige revisão pelo responsável pelo cadastro institucional, sem fallback para comparação em texto puro ou redefinição silenciosa.

Em produção, o login ABA não aceita contas locais como substituição da origem institucional. O código atual permite um fallback **somente fora de produção**, ainda com banco, para contas em `aba_professionals` quando não encontra conta institucional. Essa facilidade de desenvolvimento não faz parte do contrato de integração entre serviços e não deve ser usada como base para contas reais.

### Sessão, revalidação e encerramento

No ABA, o servidor gera token aleatório de 32 bytes, guarda somente seu SHA-256 em `aba_sessions` e envia o token no cookie `ac_social_clinical`. O cookie usa `HttpOnly`, `SameSite=Strict`, `Path=/` e `Secure` em produção, com duração de oito horas. Logout remove a sessão correspondente no banco e o cookie.

A sessão é revalidada contra o profissional e suas equipes institucionais. A perda de associação autorizada impede o acesso na próxima verificação; mudanças reconhecidas de equipe/papel atualizam o espelho. A revalidação atual não confere a senha novamente, portanto não assumir que trocar o hash da senha, por si só, revogue todas as sessões já emitidas.

Cada aplicação deve gerenciar suas sessões e autorização. Compartilhar banco de identidade não estabelece SSO, não autoriza compartilhar o cookie ABA e não permite reutilizar suas tabelas operacionais como sessões de outro serviço. Uma integração entre origens exige desenho próprio; as APIs atuais exigem a sessão e a política do próprio aplicativo ABA.

### Contrato HTTP atual de autenticação

| Método / rota | Entrada e comportamento |
|---|---|
| `POST /api/auth/login` | `email` e `password`; o cliente atual também envia `userType: "atendimento"`. Sucesso: `{ ok: true, user: { id, email, team, userType } }`, com cookie de sessão |
| `GET /api/auth/session` | Revalida o cookie; retorna `authenticated` e, no sucesso, `actor` com `id`, `email`, `name`, `role`, `team`, `userType`. Resposta sem cache |
| `POST /api/auth/logout` | Exige origem válida e encerra a sessão; sucesso: `{ success: true }` |

No login, `401` indica credenciais/acesso recusados, `403` origem inválida/ausente, `413` corpo excessivo, `422` entrada inválida, `429` limite de tentativas e `503` configuração/infraestrutura indisponível. Não interpretar `503` como senha incorreta. Mensagens não devem expor hashes, senhas ou detalhes de contas a visitantes.

O ABA mantém limite em memória e em `aba_login_attempts`: cinco falhas na janela de 15 minutos bloqueiam novas tentativas por 15 minutos. A chave combina e-mail normalizado e IP confiável quando configurado; sem proxy confiável, usa o componente `local`. Não confiar em headers de IP arbitrários.

### Configuração do backend

- Configurar a conexão do banco por segredo de ambiente. O adaptador aceita, nesta ordem, `DATABASE_URL`, `POSTGRES_URL`, `PSTGRES_DATABASE_URL`, `PSTGRES_POSTGRES_URL` e `PSTGRES_POSTGRES_PRISMA_URL`; os nomes `PSTGRES_*` são compatibilidade existente, não erro a corrigir no consumidor. Nunca expor a URL ao navegador.
- Configurar `APP_ORIGIN` com a origem pública correta em produção; login e logout validam a origem. Em desenvolvimento, sem essa variável, a validação considera protocolo e host recebidos.
- No ABA, `ABA_CLINIC_ID` deve corresponder ao escopo compartilhado. Ausente ou inválido, o adaptador atual usa `00000000-0000-4000-8000-000000000001`. Conferir o escopo real antes de integrar; não usar um novo UUID por aplicativo.
- Ativar `APP_TRUST_PROXY=true` somente atrás de proxy controlado. Manter `.env` e `.env.local` fora do versionamento e não copiar segredos para este guia.

## Consulta dos usuários/pacientes existentes por ID

A relação vigente é obtida de `institutional_users` e `institutional_user_services` no banco autorizado. Não manter uma lista estática de nomes/UUIDs reais neste documento: ela ficaria desatualizada e espalharia dados pessoais entre workspaces. Para localizar uma pessoa no segundo serviço, reutilizar seu `institutional_users.id`.

Exemplo de consulta **somente leitura**, executada pelo backend autenticado, com parâmetros vinculados pelo driver. `$1` é o `clinic_id` obtido da sessão confiável; `$2` é o UUID da pessoa a consultar:

```sql
SELECT u.id AS user_id, u.clinic_id, u.full_name, u.birth_date,
       u.responsible_contact, u.version AS identity_version,
       s.framework_code, s.record_id, s.archived_at,
       f.name AS framework_name, f.available
FROM public.institutional_users u
LEFT JOIN public.institutional_user_services s
  ON s.user_id = u.id AND s.clinic_id = u.clinic_id
LEFT JOIN public.institutional_frameworks f ON f.code = s.framework_code
WHERE u.clinic_id = $1::uuid AND u.id = $2::uuid
ORDER BY s.framework_code;
```

Uma pessoa pode gerar várias linhas, uma por serviço; pessoa sem vínculo gera linha com campos de serviço nulos. `record_id` repete o UUID institucional por contrato. `archived_at` descreve o vínculo daquele serviço, não exclusão da pessoa. `available` descreve o catálogo, não a permissão do operador.

Para uma listagem administrativa autorizada, paginar por `full_name, id` com filtro obrigatório de escopo e projetar apenas os campos necessários. Não listar todos os prontuários clínicos para resolver identidade. Exportações de pacientes e consultas sem escopo não são disponibilizadas pelas APIs atuais.

### APIs de consulta implementadas no ABA

| Método / rota | Contrato |
|---|---|
| `GET /api/registry/users?q=...&offset=0` | Busca por trecho do nome normalizado ou UUID completo; `q` tem 3–200 caracteres; offset inteiro entre 0 e 100000; retorna `{ users, hasMore }` com até 50 pessoas |
| `GET /api/registry/users/{id}` | UUID válido; retorna `{ user, services }` dentro do escopo autenticado; pessoa fora do escopo/inexistente retorna `404` |

Cada `user` contém `id`, `name`, `birthDate`, `contact`, `version` e `createdAt`; `services` contém `code`, `name` e `archivedAt`. Ambas as rotas exigem sessão e permissão de cadastro, não retornam eventos ou prontuários e usam `Cache-Control: private, no-store` e `X-Identity-Contract: ACS-IDENTITY-1`. Não há endpoint público de exportação ou escrita cadastral nesse controlador; criação/atualização ABA ocorre pelos comandos do próprio módulo.

O contrato está em [`route.ts`](../src/app/api/registry/[[...path]]/route.ts), [`identity.ts`](../src/modules/registry/domain/identity.ts) e [`repository.ts`](../src/modules/registry/infrastructure/repository.ts). Esses endpoints não são, por si só, uma API de integração autenticada entre servidores de outros serviços; não contornar as permissões compartilhando cookies ou credenciais pessoais.

## Dados comuns: campos do cadastro

| Informação | JSON | PostgreSQL | Regra |
|---|---|---|---|
| ID institucional | `id` / `userId` ao vincular ABA | `institutional_users.id` | UUID v4 gerado no servidor, imutável |
| Escopo institucional | Obtido da sessão, nunca do formulário | `clinic_id` | UUID imutável, filtro em toda consulta |
| Nome completo | `name` | `full_name` | Unicode NFC, espaços normalizados, CAIXA ALTA, acentos preservados, até 200 caracteres no DTO |
| Nascimento | `birthDate` | `birth_date` | `YYYY-MM-DD`, data real entre 1900-01-01 e o dia atual; casos anteriores exigem revisão |
| Contato do responsável | `contact` | `responsible_contact` | Texto NFC, espaços normalizados, CAIXA ALTA, até 300 caracteres; preservar pontuação e dígitos |
| Versão cadastral | `version`; ABA expõe `identityVersion` | `version` | Inteiro monotônico; incremento quando identificação muda |
| Criação/atualização | Datas ISO com fuso explícito na saída | `created_at`, `updated_at` | `timestamptz`; não usar datas locais ambíguas |

Coordenação e ATs são vínculos específicos do **ABA**, preservados em `aba_links` e no agregado clínico. Não são atributos globais da pessoa e não devem ser copiados como responsáveis do Serviço Social.

Não inventar CPF, gênero, endereço, documentos ou dados de usuários ausentes do cadastro comum. A migração inicial importa os pacientes reais já existentes; banco vazio permanece sem pessoas fictícias.

O contato atual é texto livre. Não afirmar que esse campo é telefone E.164 ou que é identificador único. Irmãos podem compartilhar o mesmo responsável/telefone. Uma futura separação entre nome e telefone exige nova versão do contrato e conferência dos registros anteriores; não fazer parsing heurístico para criar fatos.

## Normalização normativa

Aplicar nesta ordem, somente aos textos de identificação:

1. Normalizar Unicode em NFC.
2. Substituir sequências de whitespace Unicode por um espaço ASCII e remover espaços nas extremidades.
3. Converter para caixa alta Unicode; no cliente TypeScript usar `toLocaleUpperCase("pt-BR")`.
4. Normalizar novamente em NFC e validar comprimento/conteúdo.
5. Rejeitar controles e caracteres de formatação invisível restantes (`Cc`/`Cf`); não apagar silenciosamente nomes malformados.

Preservar acentos, apóstrofos e hífens. Não transformar `JOÃO` em `JOAO`, não reduzir a iniciais e não ordenar palavras. Não aplicar caixa alta às anamneses, narrativas, prescrições, assinaturas ou ciclos históricos.

```ts
function normalizeIdentityText(value: string) {
  return value.normalize("NFC")
    .replace(/\s+/gu, " ")
    .trim()
    .toLocaleUpperCase("pt-BR")
    .normalize("NFC");
}
// "  Jose\u0301\u00a0 da\tSilva  " -> "JOSÉ DA SILVA"
```

O banco aplica `acs_identity_text` em triggers e valida `acs_identity_safe`, inclusive quando outro framework usa SQL diretamente. A migração exige PostgreSQL UTF8 com ICU, collation determinística `acs_identity_v1` (`und`). Não depender da collation do sistema operacional: a conversão para caixa alta usa a locale da collation. [Normalização e strings](https://www.postgresql.org/docs/17/functions-string.html), [collations ICU](https://www.postgresql.org/docs/17/collation.html).

Testar equivalência TypeScript/SQL com acentos compostos/decompostos, NBSP, tabs, espaços Unicode, apóstrofos e expansões como `straße` → `STRASSE`. As faixas proibidas da migração correspondem ao runtime Node 22 desta versão. Mudanças de Unicode/ICU precisam dessas fixtures novamente e revisão do contrato, sem reescrever histórico silenciosamente.

## Tabelas comuns

| Tabela | Responsabilidade | Chave / limite |
|---|---|---|
| `institutional_users` | Identificação canônica da pessoa | PK `id`, UNIQUE `(id,clinic_id)`; nenhum payload clínico |
| `institutional_frameworks` | Catálogo de integrações | PK `code`, nome, `available`; não representa atendimento |
| `institutional_user_services` | Relação pessoa ↔ prontuário raiz do serviço | PK `(user_id,framework_code)`; FK `(user_id,clinic_id)`; `record_id=user_id` |
| `institutional_user_events` | Proveniência administrativa para consumo pelo framework responsável | Evento UUID, fonte, ID original, tipo fixo, ator e data; sem narrativa clínica |

O catálogo inicial da migração contém `cadastro` e `abaframework` disponíveis. `ssframework` é inserido como **indisponível/planejado**; tentativas de registrar vínculo nesse serviço são recusadas pelo banco até sua implementação e habilitação deliberada. A migração preserva entradas já existentes (`ON CONFLICT DO NOTHING`); consultar o catálogo do destino para saber sua configuração vigente. Não criar `ss_patients`, atendimentos ou históricos simulados na base real.

O SQL comum completo está em [`005_shared_registry.sql`](../src/modules/aba/infrastructure/migrations/005_shared_registry.sql). Copiar esse arquivo junto deste documento para o novo workspace, mantendo nomes e regras. O adaptador ABA está separado em [`006_aba_shared_registry.sql`](../src/modules/aba/infrastructure/migrations/006_aba_shared_registry.sql); ele não deve ser aplicado por outro framework sem o ABA presente.

## Anexo de cada framework

O registro raiz do serviço usa o **mesmo ID** da pessoa. No ABA: `aba_patients.id = institutional_users.id`. Documentos, eventos, tarefas e ciclos continuam vinculados ao mesmo prontuário; seus IDs não mudam.

Exemplo de contrato para implementar futuramente no workspace Serviço Social; **não executado nesta entrega**:

```sql
CREATE TABLE ss_patients (
  id uuid PRIMARY KEY,
  clinic_id uuid NOT NULL,
  version integer NOT NULL DEFAULT 0 CHECK(version >= 0),
  document jsonb NOT NULL,
  updated_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY(id,clinic_id) REFERENCES institutional_users(id,clinic_id)
);
```

Episódios e registros do serviço são tabelas filhas com seus próprios UUIDs e FK ao registro raiz. Não criar outro UUID de pessoa ao entrar num segundo serviço. Não adicionar uma coluna JSON de cada framework à tabela central de usuários: isso mistura identidades, políticas e prontuários.

O adaptador deve manter atomicamente o vínculo em `institutional_user_services`, projetar os dados comuns da fonte central e publicar somente metadados administrativos autorizados. No ABA, triggers fazem essa integração inclusive para worker e comandos de backend.

## Fluxo de cadastro e prevenção de identidade incorreta

1. Autenticar o operador no servidor e obter seu escopo institucional real.
2. Localizar a pessoa por UUID ou nome normalizado; conferir nascimento e contato. Nomes são auxiliares de busca, não chaves.
3. Se for a mesma pessoa, selecionar explicitamente seu UUID e abrir o anexo do serviço com esse ID.
4. Se não existir, criar uma pessoa canônica e o anexo do serviço na mesma transação. Em nome/nascimento coincidentes, recusar por padrão e solicitar conferência; confirmação de homônimo permite um UUID distinto.
5. Validar profissionais e permissões específicas do serviço, sem derivá-las do cadastro central.
6. Confirmar o commit; retornar o UUID e as versões vigentes. Falha deve reverter pessoa, vínculo, anexo e eventos juntos.

Não fazer merge automático, fuzzy matching, deduplicação por telefone ou união de nomes semelhantes. Para pacientes já existentes no ABA, a migração preserva cada UUID original, inclusive possíveis duplicidades. Reconciliação entre duas pessoas requer processo institucional específico, avaliação de vínculos e trilha de auditoria; não foi implementada como heurística.

No ABA, `registrationKey` é UUID estável do formulário para repetir um cadastro após perda de resposta. O servidor serializa a chave e mantém hash/ator em `aba_commands`; chave com outro conteúdo/ator retorna `409`. Repetir a mesma requisição retorna a pessoa já criada, sem novo registro. O controle de homônimos usa outro lock por escopo/nome/nascimento. O novo framework deve oferecer idempotência equivalente para criação e comandos; não deve reutilizar `aba_commands` como sua tabela de comandos.

Exemplo de payload ABA, com UUIDs exclusivamente sintéticos:

```json
{
  "userId": "11111111-1111-4111-8111-111111111111",
  "registrationKey": "22222222-2222-4222-8222-222222222222",
  "name": "JOSÉ DA SILVA",
  "birthDate": "2020-01-01",
  "contact": "MARIA · +55 (85) 99999-1111",
  "clinicianIds": ["33333333-3333-4333-8333-333333333333"],
  "atIds": ["44444444-4444-4444-8444-444444444444"]
}
```

`userId` ausente cria pessoa nova após a conferência de homônimos. Presente, a identificação enviada deve corresponder à fonte central; divergência ou prontuário ABA já existente retorna `409`. `confirmDistinctPerson=true` exige conferência humana de pessoa diferente; não serve para contornar um prontuário já existente da mesma pessoa.

## Atualização, concorrência e histórico

Os campos comuns têm uma versão separada da versão clínica. Atualização ABA exige `expectedVersion` e `expectedIdentityVersion`; discrepância retorna `409` e nenhuma alteração parcial. O banco mantém ID/escopo imutáveis, aumenta a versão somente se os campos comuns mudarem e preserva a data de criação.

Nome/contato atuais são lidos da fonte central; a projeção ABA é padronizada no banco quando o agregado é gravado. Histórico clínico, entradas numéricas, hashes e documentos originais não são reescritos. Um framework novo deve separar a identificação atual dos snapshots/proveniência de avaliações históricas.

Nascimento participa dos cálculos clínicos: o ABA impede mudança depois de avaliação concluída ou existência de ciclos históricos, tanto no fluxo sequencial (006) quanto no paralelo (007). Essa situação precisa de revisão clínica apropriada, não de uma edição cadastral que invalide resultados silenciosamente. Os guards também estão no banco para proteger contra alterações vindas de outro framework.

Arquivar o prontuário ABA marca somente o vínculo desse serviço como arquivado. Não exclui a pessoa institucional nem os anexos de outros serviços. Reabertura de prontuário arquivado e eliminação física não foram criadas nesta entrega; não duplicar o UUID para simular reabertura.

## Proveniência para o framework responsável pelo histórico

`institutional_user_events` contém apenas os tipos fixos `user_registered`, `user_imported`, `identity_updated`, `service_registered`, `service_activity` e `service_archived`. Eventos ABA referenciam `aba_events.id` como `source_event_id`; não copiam `reason`, etapa, anamnese, arquivos, payloads ou resultados. UNIQUE `(framework_code,source_event_id,kind)` evita duplicação na importação.

A trilha administrativa é imutável no uso normal (UPDATE/DELETE recusados). Correções devem gerar novos eventos, não apagar registros. Retenção/eliminação precisa de procedimento institucional aprovado e privilégio administrativo dedicado.

O consumidor do histórico será implementado no framework responsável. **Não há linha do tempo de recepção nem API de histórico nesse aplicativo.** O lookup ABA `/api/registry/users?q=...` exige no mínimo três caracteres, sessão e Tecnologia/Coordenação, filtra escopo e limita/pagina 50 resultados. `/api/registry/users/{id}` retorna apenas `user` e `services`, sem eventos ou prontuário. AT e Recepção não recebem esse acesso; os grupos atuais de login continuam apenas Tecnologia e Equipe ABA.

## Segurança para outros workspaces

- Validar DTOs estritos, tipos, datas, limites e caracteres no servidor; CSS uppercase não é persistência padronizada.
- Obter ator, escopo e autorização da fonte institucional; UUID conhecido não é autorização. Não aceitar papel/escopo enviados pelo navegador.
- Parametrizar SQL; usar transação, versões, idempotência e filtros `clinic_id` em toda leitura/escrita.
- Usar credenciais próprias com privilégio mínimo; leitura administrativa não inclui acesso a JSONB clínico, assinaturas, hashes de senha ou sessões.
- Expor prontuário de cada serviço somente por seu próprio backend e política de acesso. O cadastro central não é portal irrestrito de prontuários.
- Respostas de identificação sem cache, sem logs de dados pessoais, sem armazenamento em navegador; proteger mutações com origem/autenticação e HTTPS.
- Registrar o ator real com `SELECT set_config('acs.actor_id',$1,true)` dentro da transação. Importação/sistema sem operador usa ator nulo, sem inventar profissional.
- Não disponibilizar eventos administrativos em endpoint público: vinculação a serviços também é informação pessoal.

FKs e triggers garantem integridade, mas não substituem política de autorização, grants, proteção de rede e auditoria independente. O framework futuro deve revisar essas permissões antes de compartilhar qualquer prontuário.

## Migração e publicação

1. Garantir backup/ponto de restauração e revisar dados legados. Não fabricar valores para completar registros inválidos.
2. No ABA, aplicar as migrações necessárias até 007 em transação com lock de migração. A 005 cria o núcleo; a 006 integra o ABA e preserva IDs, ciclos e narrativas, padronizando apenas identificação atual; a 007 protege nascimento no fluxo paralelo. Reexecução cadastral foi testada sem multiplicar vínculos ou incrementar versões de novo.
3. Rodar `npm run aba:check`: esta versão exige **16 tabelas, dez triggers ativos e a FK composta validada do ABA**. `ok: true` exige `missing: []` e `missingInvariants: []`; ter só as tabelas da 005 não comprova aplicação dos adaptadores. Vercel verifica isso antes do build; não aplica migração automaticamente.
4. Publicar somente depois de schema validado; executar smoke test e homologação autenticada no ambiente de destino.
5. No novo framework, copiar a 005 e criar seu próprio adaptador; não habilitar `ssframework` até sua implantação real. Registrar seu catálogo, anexos e publicação administrativa com testes equivalentes.

O contrato cadastral tem verificações em banco isolado e evidências registradas de aplicação no destino. Aplicação no banco de produção e publicação são operações distintas; não presumir execução no ambiente escolhido porque existe um arquivo de migração ou uma evidência de outro destino.

No código atual, `npm run aba:migrate:registry` aplica **005/006/007**, com lock, transação e verificação do contrato antes do commit; exige as tabelas anteriores do ABA e as origens institucionais. Para um destino com 001–006 completas, `npm run aba:migrate:parallel` aplica somente a 007. `npm run aba:migrate` executa todos os arquivos SQL versionados; não provisiona as tabelas institucionais preexistentes. Confira backup recuperável e destino antes de executar. Comandos descritos aqui não foram executados nesta revisão documental. [Operação e evidência da 007](OPERACAO_PRODUCAO.md), [evidências cadastrais de 14/10/2026](EVIDENCIAS_DEPLOY_CADASTRO_2026-10-14.md).

## Roteiro para integrar uma nova aplicação

1. Confirmar o banco/schema/escopo autorizado e verificar as tabelas existentes. Usar este documento como referência técnica, sem copiar segredos ou dados pessoais para o repositório novo.
2. Implementar o login no backend a partir de `profissionais_cadastrados`, validando o hash compatível e consultando `equipes_profissionais` pelo ID institucional. A interface solicita somente e-mail e senha. Definir as equipes e papéis autorizados para o serviço novo.
3. Preservar o ID do profissional no adaptador operacional do novo serviço e configurar seu escopo institucional confiável. Implementar sessões próprias, revalidação de equipe, encerramento, origem e limites de tentativas; não depender do espelho/cookie ABA como fonte de autenticação.
4. Localizar os pacientes reais em `institutional_users` pelo UUID, com filtro de escopo. Reutilizar o cadastro; conferir homônimos e não gerar outro ID para a mesma pessoa ao abrir um segundo serviço.
5. Se o núcleo compartilhado ainda não existir no destino autorizado, preparar a 005; se existir, verificar compatibilidade antes de qualquer DDL. Criar somente o adaptador e as tabelas específicas do novo framework, com FKs compostas, versões, idempotência e proveniência mínima. A 006 e a 007 são do ABA.
6. Gerenciar o vínculo em `institutional_user_services` na mesma transação da criação do prontuário raiz, com `record_id=user_id`. Habilitar o código do serviço em `institutional_frameworks` apenas quando sua implementação estiver pronta; não habilitar `ssframework` antecipadamente.
7. Aplicar a política própria de acesso ao prontuário e aos profissionais vinculados. Um UUID conhecido e uma identificação compartilhada não concedem acesso clínico entre serviços.
8. Verificar a integração em banco isolado, depois seguir o processo institucional de migração/publicação. Registrar destino, versão, checagens e limites sem incluir credenciais ou dados pessoais nos relatórios.

## Referências de implementação para outros workspaces

| Arquivo | O que reutilizar ou consultar |
|---|---|
| [`institutionalProfessionals.ts`](../src/modules/aba/infrastructure/institutionalProfessionals.ts) | Consultas institucionais, equipe por ID e preservação do ID no espelho; adaptar a parte específica ABA |
| [`institutionalAccess.ts`](../src/modules/auth/application/institutionalAccess.ts) e [`teamPolicy.ts`](../src/modules/auth/application/teamPolicy.ts) | Política atual ABA; definir explicitamente a política do novo serviço |
| [`passwordHash.ts`](../src/modules/auth/application/passwordHash.ts) | Verificação compatível do hash institucional |
| [`auth.ts`](../src/modules/aba/infrastructure/auth.ts) e [`loginRateLimit.ts`](../src/modules/auth/application/loginRateLimit.ts) | Ciclo de sessão, revalidação e proteção de tentativas do ABA |
| [`config.ts`](../src/modules/aba/infrastructure/config.ts) e [`http.ts`](../src/modules/aba/infrastructure/http.ts) | Configuração da conexão, origem e limites de entrada |
| [`005_shared_registry.sql`](../src/modules/aba/infrastructure/migrations/005_shared_registry.sql) | Núcleo compartilhado `ACS-IDENTITY-1` |
| [`006_aba_shared_registry.sql`](../src/modules/aba/infrastructure/migrations/006_aba_shared_registry.sql) e [`007_parallel_flow.sql`](../src/modules/aba/infrastructure/migrations/007_parallel_flow.sql) | Adaptadores e guards exclusivos do ABA, presentes no banco compartilhado |
| [`identity.ts`](../src/modules/registry/domain/identity.ts) e [`repository.ts`](../src/modules/registry/infrastructure/repository.ts) | DTOs, normalização, consulta, concorrência e atualização cadastral |

Ao copiar este documento para outro workspace, levar os arquivos comuns necessários e ajustar os caminhos das referências. As dependências do backend ABA não formam um pacote de autenticação independente pronto para importação em qualquer serviço.

## Critérios para aderência ao padrão

O novo workspace deve provar: mesma pessoa/UUID em dois serviços; isolamento entre escopos; Unicode e datas equivalentes no servidor e banco; homônimos distintos sem merge automático; FK composta e IDs imutáveis; falha transacional; idempotência e concorrência; CAS das versões; ausência de dados clínicos na identificação/proveniência compartilhada; arquivo histórico preservado; serviço ainda planejado sem vínculos fictícios; migração repetida; autorização negativa e fluxo desktop/mobile.

Para autenticação, verificar: login com e-mail/senha institucionais sem seleção de equipe; senha inválida recusada; associação de equipe resolvida pelo ID correto; campos de equipe/papel adulterados no cliente sem efeito autorizador; conta fora da política recusada; mesmo ID preservado no espelho; perda de equipe bloqueando a sessão na revalidação; logout e expiração; origem inválida e limites de tentativas; banco indisponível sem fallback de produção; hashes/credenciais ausentes das respostas e logs. Testar esses casos com dados sintéticos em ambiente isolado.

Aderência a este contrato não representa conformidade absoluta da instituição. Aceite clínico, privacidade/retenção, backup/restauração exercitada, operação durável e auditorias independentes permanecem critérios externos ao código.
