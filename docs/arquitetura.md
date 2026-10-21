# Arquitetura — 21/10/2026

## Fontes normativas

Ler [planejamento](PLANEJAMENTO_SOCIAL_FRAMEWORK_AC_SOCIAL.md), [integração ACS-IDENTITY-1](INTEGRACAO_SERVICOS_USUARIOS_PACIENTES_E_AUTENTICACAO.md), [branding](branding-guidelines.md) e [modelo cadastral](cadastro-modelo.md). O bloco Next.js do `AGENTS.md` permanece preservado; guias locais consultados: layouts/pages, server/client components, route handlers e autenticação, em `node_modules/next/dist/docs/`.

## Camadas e dependências

```text
Navegador → Next.js App Router / BFF → FastAPI / API
                                       ↓
                                  Aplicação → Domínio
                                       ↑
                               Infraestrutura PostgreSQL
```

- `backend/app/domain`: identidade e política pura, sem FastAPI, SQLAlchemy ou React.
- `backend/app/application`: serviços de autenticação e consulta, erros de aplicação e portas (`Protocol`). Não importa framework HTTP nem repositórios concretos.
- `backend/app/infrastructure`: PostgreSQL, consultas parametrizadas, unidade transacional, scrypt e diagnóstico. Implementa as portas.
- `backend/app/api`: composição e autorização HTTP; `main.py` monta o processo, os endpoints e a barreira de segurança. DTOs Pydantic ficam em `schemas`.
- `src/app`: rotas e guards server-side; páginas dependentes de sessão são dinâmicas. `src/features` reúne apresentação por módulo; `src/lib` centraliza Axios, tema e acesso exclusivo do servidor; `src/components` contém o shell.

O frontend segue na raiz existente para preservar o projeto Next.js; o backend tem ambiente Python independente. `cacheComponents` experimental foi retirado desta base para manter os fluxos autenticados explícitos e dinâmicos. Fetches de sessão/API usam `no-store`; não se instala service worker nem persiste cache no navegador.

## Autenticação e autorização

E-mail e senha são os únicos campos de login. Equipes vêm da consulta pelo ID de `profissionais_cadastrados`, nunca de dados do cliente. O verificador implementa scrypt com parâmetros padrão do Node e comparação constante; foi conferido no código local do adaptador ABA e em vetor sintético independente, mantendo pendente a homologação das credenciais/destino. O cliente confirma a sessão antes de redirecionar.

Sessão própria `ac_social_ss`: token aleatório de 32 bytes; somente SHA-256 no PostgreSQL; cookie HttpOnly, SameSite=Strict, Path=/ e Secure em produção; expiração de oito horas. Revalidação consulta o profissional e suas equipes a cada operação. Logout revoga o hash. Nenhuma senha é escrita no espelho, nas sessões ou nos logs.

A lista fixa de login permite somente as equipes institucionais exatas `Serviço social` e `Tecnologia`, confirmadas no banco. Ambas podem autenticar sem permissões de módulos quando a infraestrutura estiver pronta. A configuração não autoriza equipes adicionais. Perder o último vínculo permitido faz a sessão retornar 401 na próxima operação; o frontend limpa consultas e volta ao login. Consulte a [política de acesso](politica-acesso.md).

Tecnologia pode diagnosticar conexões; não ganha acesso social automaticamente. A política de leitura social está vazia e desligada por padrão; ativá-la exige matriz aprovada. Não há permissões de escrita disponíveis nesta etapa. Guards de página e API são independentes; rota técnica sem equipe retorna página 404 e endpoint 403.

## Fronteiras de segurança

BFF permite somente métodos/caminhos enumerados; não encaminha cabeçalhos de papel, IP ou equipe. Mutações exigem origem exata no Next.js e no Python. Corpos são limitados a 16 KiB por leitura efetiva, inclusive sem Content-Length. Cookies são encaminhados apenas ao backend configurado no servidor; o destino não vem da requisição. CORS permite apenas a origem configurada.

Respostas de API usam `private, no-store`, `nosniff` e erros sanitizados. DTOs não devolvem os valores submetidos em erros de validação. React Query permanece em memória (`gcTime: 0`, sem persistência); logout ou 401 limpa as consultas. O ambiente de execução deve proteger logs e desativar logs de acesso com query string; o comando local da API usa `--no-access-log`.

## Evolução obrigatória

Persistência social, prontidão completa do contrato, trilha durável de acessos, storage privado/quarentena, termo versionado, PDF, idempotência e CAS ainda precisam de implementação. A API retorna 503 nos módulos sociais, e ações futuras não recebem endpoints fictícios. Confira a auditoria antes de considerar o sistema pronto para produção.
