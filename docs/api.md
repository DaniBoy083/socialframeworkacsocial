# API — base 0.1.0

Backend FastAPI em `/api/v1`; Next.js oferece BFF de mesma origem sob o mesmo prefixo. Não há compartilhamento de cookies ABA, SSO implícito ou conexão direta do navegador ao banco. Documentação interativa/OpenAPI HTTP está desativada; o schema pode ser inspecionado localmente por `app.openapi()`.

| Método e rota | Autorização / resultado |
|---|---|
| GET `/health` | Público; `{status: "ok", service: "social-framework"}`; não revela banco/configuração |
| POST `/auth/login` | Origem exata; `{email,password}` estrito; senha válida + vínculo atual exclusivamente com `Serviço social`/`Tecnologia`; cria cookie próprio e retorna `{authenticated,actor}` |
| GET `/auth/session` | Sessão válida, revalidação institucional das duas equipes autorizadas; perda do último vínculo retorna 401; `{authenticated:true,actor}` |
| POST `/auth/logout` | Origem exata; revoga sessão e remove cookie; idempotente sem cookie |
| GET `/usuarios?busca=...&offset=0` | Sessão + `registry:read`; 3–200 caracteres normalizados, offset 0–100000; `{users,hasMore}` |
| GET `/tecnologia/conexao` | Sessão + equipe atual exatamente `Tecnologia`; status e latência sanitizados |
| GET `/servico-social/cadastros` | Sessão + `registrations:read`; **503**, contrato social pendente |
| GET `/servico-social/analises/resumo` | Sessão + `analytics:read`; **503**, agregações pendentes |

`actor`: `id` (texto), `name`, `email`, `teams`, `permissions`, `isTechnology`. O cliente não pode escolher esses atributos. `users`: identidade administrativa mínima, sem prontuário, campos `id,name,birthDate,contact,version,createdAt`. Não usar esse endpoint como lista de cadastros sociais ou interpretar ausência de prontuário como ausência da pessoa.

Todos os endpoints de dados exigem autorização no backend e não são públicos por conhecer um ID. Nenhuma permissão social é concedida até configurar explicitamente política aprovada. Essa política não concede login a outras equipes. Membros de Serviço Social e Tecnologia podem autenticar sem permissões de módulo, mas não consultar dados sem autorização específica. Consulta institucional está implementada, mas não homologada com registros reais.

## Erros e segurança

- 401: sessão/credenciais/acesso de login recusados; 403: origem/equipe/permissão recusada.
- 404: rota fora da lista permitida; 413: corpo acima de 16 KiB.
- 422: DTO/pesquisa inválida, sem ecoar entrada ou senha.
- 429: cinco falhas em 15 minutos; aguardar o bloqueio de 15 minutos.
- 503: configuração/infraestrutura/módulo indisponível; nunca interpretar como senha errada ou lista vazia.

Cabeçalhos de dados: `Cache-Control: private, no-store`, `X-Content-Type-Options: nosniff`; sem logs de SQL, parâmetros ou strings de conexão. Tamanho é conferido durante a leitura também em requisições sem Content-Length.

PDF, anexos, manifestações, criação/edição/arquivamento e atendimentos **ainda não possuem endpoints**. A lista do planejamento é um roteiro, não contrato já entregue. Quando implementados, downloads e impressão exigirão autorização e auditoria próprias; jamais apontar para `/public` ou URLs permanentes.
