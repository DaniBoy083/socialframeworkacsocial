<!-- BEGIN:nextjs-agent-rules -->

## This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->


## Regras do Social Framework

- Antes de alterar o domínio, ler `docs/PLANEJAMENTO_SOCIAL_FRAMEWORK_AC_SOCIAL.md`, o contrato `docs/INTEGRACAO_SERVICOS_USUARIOS_PACIENTES_E_AUTENTICACAO.md` e `docs/AUDITORIA_APLICACAO_E_PRINCIPIOS.md`. Conferir também `docs/arquitetura.md`, `docs/cadastro-modelo.md` e `docs/decisoes.md` para mudanças relacionadas.
- Não inventar tabelas, campos, equipes, permissões ou consentimentos. Identidade institucional da pessoa é UUID; ID físico do profissional é texto. Não misturar as duas identidades.
- Manter domínio e aplicação Python independentes de HTTP e infraestrutura. Implementar adaptadores pelas portas e compor dependências na API.
- Não copiar credenciais/sessões ABA; não criar contas de demonstração nem habilitar `ssframework` no banco por inferência. Negar acesso por padrão e conferir autorização no servidor, inclusive tecnologia, arquivos e PDFs.
- Não aplicar migrações no startup/build. Revisar destino, contrato, backup e privilégios separadamente. Os SQLs com `.proposed.sql` não estão homologados para execução.
- Nunca versionar segredos, dados pessoais, documentos de pessoas ou resultados de consultas reais. Fixtures sintéticas vivem somente em `tests/`; não importar o servidor de fixtures na aplicação.
- Respeitar a ordem/campos confirmados no PDF. Não tratar assinatura/upload como autorização de imagem. Não armazenar arquivos pessoais em `public`, cache persistente do navegador ou URL aberta.
- Atualizar a auditoria com evidências e pendências em cada entrega; não declarar 100% de conformidade ou prontidão sem verificar cada critério. Executar os checks adequados do README e manter CI. Testes com fixtures não substituem homologação real.

- Login é permitido exclusivamente a membros institucionais de `Serviço social` e/ou `Tecnologia`, nomes físicos confirmados. Aplicar a lista fixa no login e na revalidação de sessão; configuração de módulos não pode autorizar outras equipes. Seguir `docs/politica-acesso.md`; manter dados sociais sob permissões separadas e diagnóstico exclusivo de Tecnologia.
