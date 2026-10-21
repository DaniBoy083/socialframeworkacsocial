# Social Framework | AC Social

Base de desenvolvimento do ambiente interno do Serviço Social: Next.js 16.4.2, React, TypeScript e FastAPI. A entrega inicia o planejamento; **o MVP ainda não está completo nem homologado para dados reais**. Consulte a [auditoria de requisitos](docs/AUDITORIA_APLICACAO_E_PRINCIPIOS.md) antes de habilitar integrações.

## O que está disponível

Login institucional com layout baseado nas referências, shell responsivo, sidebar e Agenda Digital; backend de autenticação com scrypt, sessões opacas próprias, revalidação de equipes, limitação persistente de tentativas e proteção de origem; consulta institucional preparada, diagnóstico restrito a Tecnologia e componentes iniciais de cadastros/análises. A ausência de infraestrutura retorna indisponibilidade e não inventa registros.

A sessão depende de escopo configurado e das tabelas próprias de autenticação. O repositório contém uma **proposta de migração não aplicada**. A equipe Tecnologia recebe diagnóstico; não recebe acesso implícito aos dados sociais. As demais equipes dependem da matriz institucional aprovada. Não há conta demonstrativa, bypass de login ou armazenamento de credenciais no navegador.

## Ambiente local (PowerShell)

Requisitos: Node 22+, npm e Python 3.12. Use `npm.cmd` quando a política de execução impedir `npm.ps1`.

```powershell
npm.cmd ci
python -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.lock.txt
Copy-Item .env.example .env.local
```

Se `.env.local` já existir, preserve seu conteúdo e complete apenas as chaves faltantes. Não copie segredos para documentação. `requirements.lock.txt` registra as versões verificadas em Windows/Python 3.12; `requirements*.txt` descrevem as dependências diretas. Em Linux, use os executáveis em `backend/.venv/bin/`.

Em dois terminais:

```powershell
npm.cmd run dev:api
npm.cmd run dev
```

Abra `http://localhost:3000`. O backend fica em `http://127.0.0.1:8000`. `GET /api/v1/health` verifica somente a vida do processo; não comprova prontidão do banco.

Para autenticação real, confirmar primeiro `SOCIAL_CLINIC_ID`, estrutura do destino, implementação scrypt original e proposta de migração. Não gerar um escopo novo e não aplicar migrações ABA neste serviço. `APP_ORIGIN` deve coincidir no Next.js e no FastAPI. `SOCIAL_API_URL` é exclusiva do servidor. Produção exige `ENVIRONMENT=production`, HTTPS e infraestrutura revisada.

## Verificação

```powershell
npm.cmd run lint
npm.cmd run typecheck
npm.cmd run format:check
npm.cmd run build
backend/.venv/Scripts/python.exe -m ruff check backend/app backend/scripts backend/tests
backend/.venv/Scripts/python.exe -m ruff format --check backend/app backend/scripts backend/tests
npm.cmd run test:backend
npm.cmd exec playwright -- install chromium
npm.cmd test
npm.cmd audit --omit=dev
```

Os testes de interface usam um servidor isolado em `127.0.0.1:18001` com identidades sintéticas em `tests/fixtures/`; não criam pessoas no banco e não validam login real. Reserve a porta 3000 para a instância iniciada pelo teste. Capturas ficam em `output/screenshots`, fora do Git. Testes Python usam repositórios em memória e dependências substituídas, sem consultar o banco real.

Inspeção opcional **somente leitura**, sem imprimir credenciais, pessoas ou hashes:

```powershell
backend/.venv/Scripts/python.exe backend/scripts/inspect_schema.py
```

## Documentação

- [Planejamento recebido](docs/PLANEJAMENTO_SOCIAL_FRAMEWORK_AC_SOCIAL.md)
- [Arquitetura](docs/arquitetura.md) e [decisões](docs/decisoes.md)
- [Banco e contratos](docs/banco-contratos.md), [API](docs/api.md) e [modelo cadastral](docs/cadastro-modelo.md)
- [Matriz de tratamentos](docs/lgpd-matriz-tratamentos.md)
- [Auditoria, evidências e pendências](docs/AUDITORIA_APLICACAO_E_PRINCIPIOS.md)
- [Operação e evolução](docs/operacao.md)

Não há deploy automático nem alteração do banco em build/startup. PDFs pessoais, documentos, dados reais e segredos não devem ser adicionados a `public`, fixtures, logs ou commits.
