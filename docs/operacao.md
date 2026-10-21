# Operação e continuidade

## Antes de qualquer habilitação real

- Conferir origem, HTTPS, `ENVIRONMENT=production`, segredo PostgreSQL de privilégio mínimo e escopo institucional existente. Nunca usar outro clinic_id por aplicação.
- Obter as migrações/implementações comuns referenciadas no contrato; conferir tipos, FKs, triggers, normalização ICU, grants e versão ACS-IDENTITY-1.
- Revisar a proposta `001_social_auth.proposed.sql` com backup recuperável, histórico de migrações, retenção e plano de recuperação. Aplicação é uma operação separada, não executada por build/startup.
- Homologar scrypt com fixtures da implementação institucional original; testar credenciais válidas/inválidas sem expor hashes, associação pelo ID, revogação de equipe, origem, limitação e logout em ambiente isolado.
- Aprovar matriz de equipes/permissões específica do Serviço Social e implementar trilha durável de acesso antes de ativar leituras reais. Não dar acesso social a Tecnologia por padrão.
- Confirmar provedor de frontend/API Python e rede entre ambos. Um build Next.js não provisiona FastAPI nem garante compatibilidade com Vercel. Não publicar fixture de teste.

## Próximas entregas

1. Contrato social físico e migrações com FK composta, versões, idempotência, homônimos, arquivamento e proveniência. Testes com PostgreSQL isolado, inclusive transações e concorrência.
2. Formulário conforme inventário do PDF e definições confirmadas; busca explícita de pessoa por ID/nome, revisão, gravação e edição transacionais.
3. Último atendimento: confirmar a fonte institucional e escopo; `institutional_user_events` não é, por inferência, a tabela de atendimentos. Exibir America/Fortaleza; sem registro, “Sem atendimentos”.
4. Ficha PDF backend e modal com impressão/download, auditoria separada, versão atual, cache privado e liberação de object URLs. Testar visualmente cada geração, inclusive nomes e textos longos.
5. Termo versionado, decisão de imagem separada, storage privado, quotas, magic bytes, nomes seguros, quarentena/antimalware e vínculo de cada documento ao atendimento/pessoa corretos.
6. Análises SQL agregadas; Pandas/NumPy apenas quando necessários. Critérios de pequenos grupos e filtros aprovados antes da exposição.
7. Homologação real desktop/mobile, teclado/leitor de tela, autorização horizontal/vertical, uploads hostis, recuperação de backup e resposta a incidentes. Publicar apenas após os gates.

## Cuidados de operação

API local usa `--no-access-log`; também configurar proxy, frontend e observabilidade para não registrar queries com nomes, e-mails, cookies ou documentos. Nunca habilitar SQL echo. Exceções públicas não incluem valores Pydantic nem URLs do banco.

Expiração impede acesso mesmo antes da limpeza física de sessões. O job de limpeza de sessões/tentativas e sua política de retenção ainda não foram implementados. Não anunciar renovação automática ou revogação por troca de senha. Configurar proteção global de tentativas no proxy controlado, sem confiar em X-Forwarded-For arbitrário.

Não existe deploy, alteração do catálogo `ssframework` ou migração automática nesta entrega. A auditoria deve ser atualizada a cada mudança com requisitos, comandos executados, resultados e limites reais.
