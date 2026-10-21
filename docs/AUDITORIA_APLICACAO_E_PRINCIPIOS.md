# Auditoria da aplicação e dos princípios

Data: **21/10/2026**, America/Sao_Paulo. Escopo: primeira entrega de desenvolvimento, a partir do bootstrap Next.js existente. **Não há evidência para afirmar 100% de conformidade, conclusão do MVP ou prontidão para produção.** As restrições abaixo são parte do resultado, não uma homologação implícita.

## Materiais examinados

- Planejamento `PLANEJAMENTO_SOCIAL_FRAMEWORK_AC_SOCIAL.md` recebido no workspace, preservado e incluído no versionamento.
- Contrato `INTEGRACAO_SERVICOS_USUARIOS_PACIENTES_E_AUTENTICACAO.md` e `branding-guidelines.md`.
- Duas páginas do PDF-modelo: texto extraído e renderização visual; campos e ambiguidades em [cadastro-modelo](cadastro-modelo.md).
- Imagens do prompt: composição do login e painel/sidebar ABA. Nomes adaptados para Social Framework, com logo oficial extraído do modelo.
- [Agenda Digital](https://agenda-digital-ac-social.vercel.app), consultada por HTTP em 21/10/2026, resposta 200: login institucional e identificação do rodapé. A consulta não foi uma homologação autenticada da Agenda.
- Guias locais da versão instalada do Next.js para páginas/layouts, componentes servidor/cliente, route handlers e autenticação; bloco obrigatório do AGENTS preservado.
- Inventário READ ONLY de colunas do banco configurado: [banco e contratos](banco-contratos.md). Não houve leitura de pessoas/senhas, criação de sessões reais, DDL/DML institucional ou deploy.

Arquivos externos referenciados e ausentes: migração 005 comum, implementação `passwordHash.ts`, adaptadores ABA, guias de arquitetura unificada, documentos de operação/evidências de outro serviço. Suas afirmações documentais não foram tratadas como verificação deste destino.

## Princípios e evidência

| Princípio | Situação nesta etapa | Evidência / limite |
|---|---|---|
| Clean Architecture | Implementado na base | Domínio/aplicação independentes de HTTP e infraestrutura; portas e adaptadores; dois testes protegem a direção das dependências |
| Clean Code e reutilização | Implementado na base | Providers, tema, cliente Axios, guards, shell e módulos separados; ESLint, TypeScript estrito, Ruff e formatação |
| Segurança por padrão | Parcial | Origem, sessão, revalidação, corpos limitados, erros seguros e permissões; falta homologação real, trilha durável e revisão de produção |
| Responsividade/acessibilidade | Verificado nas superfícies implementadas | Login, modal e diagnóstico com Axe; navegação desktop/mobile, foco no menu e Escape; não certifica leitor de tela ou fluxos futuros |
| Integração sem duplicidade | Preservada por restrição | Sem cópias de pessoas/credenciais; tipos físicos conferidos; nenhuma escrita social; criação transacional ainda pendente |
| Privacidade desde a concepção | Parcial | Coleta social desativada, cache privado, sem dados reais em fixtures; matriz inicial documentada; bases legais/retenção/termos pendentes |
| Consistência visual | Implementada na base | Paleta institucional, rodapé único, cards claros, sidebar vermelha e atalho real da Agenda; capturas revisadas |

## Matriz dos critérios de aceite do planejamento

Legenda: **implementado** descreve código entregue; **verificado** tem evidência local; **pendente** não deve ser anunciado como funcional em produção.

| Requisito | Estado | Evidência / próxima condição |
|---|---|---|
| Next.js/TypeScript + FastAPI, dependências, README e ambiente | Implementado e verificado | Build, checks e dependências instaladas; lockfiles versionados |
| Login institucional funcional e perfis conferidos no banco | Parcial | Serviço, adaptador e testes prontos; faltam escopo confirmado, migração própria, arquivo original scrypt, matriz e login real homologado |
| Sidebar responsiva, Cadastros, Análises, Agenda e Tecnologia | Implementado e verificado com fixtures | Visibilidade por permissão; Tecnologia sem poderes sociais implícitos |
| Equipe alheia não acessa a área técnica | Implementado e verificado | Guard servidor da página; API 403; headers adulterados sem efeito |
| Lista vazia sem tabela e com Novo cadastro | Implementado e verificado com fixtures | Resposta real de cadastros permanece 503; não representar falha como zero registros |
| Nome, último atendimento, WhatsApp e ações na tabela | Parcial | Componente/formatadores iniciais; faltam fonte de atendimentos, dados sociais e ações operacionais |
| Data/hora America/Fortaleza e telefone válido | Implementado nos utilitários e testado | Sem datas fictícias; WhatsApp só de telefone E.164 brasileiro explícito, nunca de contato livre |
| Ver cadastro em modal PDF | Pendente | Backend PDF e viewer ainda não implementados |
| Imprimir e Baixar PDF autorizados | Pendente | Requer permissões, mesma versão do conteúdo e auditoria dos acionamentos |
| PDF atual, fiel ao modelo, sem cache público | Pendente | Modelo inventariado; nenhuma ficha real foi gerada |
| Editar e excluir/arquivar com confirmação/retenção | Pendente | Sem endpoints de escrita; exige contrato, CAS, política de guarda e auditoria |
| Novo cadastro como formulário fiel ao PDF | Parcial | Modal acessível informa seções; formulário operacional não foi liberado; faltam regras não declaradas no modelo |
| Pesquisa por ID/nome e prevenção de duplicidade | Parcial | Consulta parametrizada preparada, paginada e com escopo; falta homologação do banco e fluxo transacional de criação/homônimos |
| Registro social conserva UUID institucional | Pendente de persistência | Regra documentada e identidade preservada nas consultas; nenhuma nova tabela social criada por inferência |
| Termo PDF/foto/câmera com preview e substituição | Pendente | Texto combinado identificado; confirmar versão, manifestação e infraestrutura privada |
| Anexos de atendimento por PDF/imagem | Pendente | Fonte/ID de atendimento e storage/quarentena ainda não confirmados |
| Documentos privados com autorização | Pendente | Não há upload/download público ou privado liberado nesta etapa |
| Ciência e imagem com rastreabilidade separada | Pendente | Decisão arquitetural registrada; não inferir consentimento por assinatura/upload |
| Pendência documental retomável | Pendente | Requer persistência e workflow de formalização |
| Análises reais e consistentes | Pendente | Página/endpoint protegidos; retorna 503; sem números simulados |
| Logs, retenção e LGPD revisados | Parcial | Sanitização e minimização implementadas; matriz técnica inicial; revisão institucional e trilha durável faltantes |
| Testes de autorização, uploads, validação e erros | Parcial | Autorização/validação/erros verificados; uploads e autorização horizontal de cadastros aguardam implementação |
| Migrações, backup, deploy e homologação final | Pendente | SQL somente proposto; CI configurada localmente; nenhum workflow remoto/deploy executado |

## Verificações executadas

| Verificação | Resultado |
|---|---|
| `npm.cmd run lint` | Aprovado |
| `npm.cmd run typecheck` | Aprovado, geração de tipos Next + TypeScript |
| `npm.cmd run format:check` | Aprovado |
| `npm.cmd run build` | Aprovado, rotas autenticadas dinâmicas |
| Ruff check/format | Aprovado |
| `npm.cmd run test:backend` | **30 testes aprovados**, sem acesso ao banco real |
| `npm.cmd test` | **19 testes aprovados**, 1 ignorado intencionalmente: teste exclusivo de menu móvel no projeto desktop |
| Axe WCAG A/AA nas telas/cenários testados | Nenhuma violação automática reportada; não equivale a certificação completa |
| Smoke FastAPI real, sem consultar dados | Health 200; sessão sem cookie 401; login sem escopo 503 |
| scrypt Python × Node 22 | Vetor sintético independente aprovado, preservando espaços/acentos da senha; arquivo institucional original ainda ausente |
| `pip check` | Nenhuma incompatibilidade reportada |
| `npm audit --omit=dev` | Nenhuma vulnerabilidade de produção reportada na data da consulta |
| `npm audit` completo | **5 ocorrências altas pendentes** na cadeia ESLint/fast-glob/micromatch/braces; sem correção compatível publicada na consulta |
| Inventário de banco | Consulta READ ONLY bem-sucedida; tipos/colunas, sem certificar constraints/triggers/grants |

Os testes de frontend usam servidor exclusivo `tests/fixtures/api-server.mjs` com atores sintéticos e banco ausente. Testes Python substituem repositórios/dependências; verificam limites, autorização, ciclo de sessão e regras, mas **não provam a integração PostgreSQL real**. O CI foi adicionado para manter as verificações em futuras alterações; execução remota ainda não foi observada.

Aviso de ferramenta observado: Starlette sinaliza futura troca de `httpx` por `httpx2` no TestClient. Os testes passam; revisar compatibilidade no próximo ajuste de dependências, sem ocultar o aviso. A auditoria npm completa sugeriu downgrade do eslint-config-next para 14; não aplicado por incompatibilidade com a base Next 16.

## Gates para avançar com dados reais

1. Confirmar escopo e política social; obter os arquivos comuns faltantes e verificar invariantes/grants do destino. Não habilitar `ssframework` antecipadamente.
2. Homologar autenticação original e revisar/aplicar apenas a migração própria autorizada com backup. Implementar limpeza/retenção e auditoria durável antes de habilitar leituras reais.
3. Aprovar regras cadastrais ausentes no PDF e modelo físico social; implementar transações, idempotência, CAS e isolamento por recurso.
4. Validar termo, finalidades, representação/menores, decisões de imagem, retenção e procedimentos de papel; definir storage privado, antimalware/quarentena e recuperação.
5. Concluir PDF/documentos/análises e respectivos testes de segurança, fidelidade visual e integração antes do deploy.

A aplicação respeita os limites conhecidos desta fase ao bloquear operações não confirmadas. Isso **não substitui implementar e homologar os critérios pendentes**.
