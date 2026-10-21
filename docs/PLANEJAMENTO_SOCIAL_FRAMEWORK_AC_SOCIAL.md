Planejamento de Desenvolvimento — Social Framework | AC Social

Versão: 1.1 — tabela de cadastros, documentos de atendimento e visualizador PDF imprimível
Data: 21/10/2026
Status: requisitos iniciais consolidados; iniciar implementação após leitura dos anexos e contratos técnicos existentes
Destinatário: agente de desenvolvimento do Social Framework

1. Instrução principal ao agente

Inicie o desenvolvimento do Social Framework. Configure o ambiente do projeto, inicialize o frontend em Next.js e o backend em FastAPI, instale e configure as dependências descritas neste planejamento, examine a documentação técnica e os arquivos de referência já disponibilizados no Workspace e avance pelas etapas do MVP. Não se limite a produzir wireframes ou textos: implemente a base operacional, a autenticação, a navegação, os fluxos de cadastro, a integração segura com o banco, os controles para documentos assinados e a visualização/impressão de fichas cadastrais em PDF. Mantenha o projeto executável e registre as decisões em documentação.

Antes de implementar os formulários e as integrações, examine obrigatoriamente:

O PDF-modelo de cadastro do Serviço Social presente na documentação do Workspace. Ele é a fonte para a ordem dos campos, rótulos, seções, obrigatoriedade, máscaras e regras do formulário. Não invente campos onde o modelo/documentação já os especifica.

A documentação do banco existente, especialmente autenticação, profissionais, equipes, usuários atendidos, IDs, relacionamentos, convenções e regras de cadastro. Descubra nomes de tabelas/colunas reais antes de escrever consultas ou migrações.

Os prints enviados diretamente ao agente com as referências de tela de login, sidebar e páginas. Utilize-os para o layout e mantenha responsividade e acessibilidade.

O link da Agenda Digital enviado ao agente como referência de navegação, identidade, integração e padrões do ecossistema. Não há URL informada neste planejamento: usar aquela efetivamente recebida no canal de desenvolvimento.

O modelo oficial do termo de imagem/ciência de cadastro, se disponível. Confirmar com a AC Social a versão institucional, os campos e o procedimento de assinatura.

Atenção às referências: o PDF, os prints e o link foram mencionados pelo responsável pelo projeto, mas não foram disponibilizados nesta conversa de planejamento. O agente que os recebeu deve consultá-los diretamente; não considerar que foram inspecionados aqui.

2. Objetivo e contexto

Construir uma aplicação interna do Serviço Social da AC Social, inspirada no fluxo operacional do ABA Framework, para cadastrar, localizar, consultar e acompanhar pessoas atendidas; registrar os dados próprios do Serviço Social; associar documentos de formalização assinados; fornecer uma página de análise de dados; e oferecer funcionalidades técnicas restritas à equipe de Tecnologia. Permitir consultar a ficha completa em um modal de PDF, imprimi-la e baixá-la para arquivo físico institucional, de acordo com as permissões aplicáveis.

O Social Framework integra o ecossistema da AC Social e deve reutilizar a identidade única da pessoa atendida, de modo compatível com Agenda Digital, Acesso Digital e demais frameworks. Manter separação entre cadastros institucionais compartilhados e registros específicos do Serviço Social. O projeto deve respeitar a arquitetura institucional prévia, sem duplicar pessoas ou credenciais.

3. Stack e dependências

Frontend

Next.js (App Router), React, TypeScript, com ESLint e TypeScript em modo estrito.

Material UI (MUI): componentes, tema, diálogos, tabelas, responsividade.

React Icons: ícones da interface.

TanStack React Query: fetching, cache, invalidação, loading, estados de erro e sincronização dos dados vindos da API.

Axios: cliente de requisições HTTP, interceptadores, tratamento de erros. Na fala foi mencionado um nome semelhante a “Agiles”; assumir Axios provisoriamente, alinhado aos projetos anteriores, e confirmar pela documentação do repositório caso haja outra biblioteca pretendida.

React Hook Form + Zod (recomendados): formulários e validação tipada; backend permanece responsável pela validação definitiva.

Recursos nativos do navegador para captura de foto (input accept="image/*" capture="environment" em dispositivos compatíveis), com fallback para câmera via getUserMedia onde autorizado e suportado.

Visualizador de PDF em modal com suporte a impressão e download: usar visualização embutida do navegador ou PDF.js quando necessário para toolbar, acessibilidade e compatibilidade. A geração do documento fica no backend, não no componente de tabela.

Backend

Python + FastAPI: API de negócio, autenticação/autorizações, validação, persistência e integração.

Pydantic: contratos tipados, DTOs e validação da API.

SQLAlchemy + Alembic (recomendados): acesso ao PostgreSQL e migrações apenas para novas estruturas, compatíveis com o esquema existente.

Pandas e NumPy: tratamento, agregações e cálculo de indicadores do Serviço Social. Não empregar Pandas/NumPy onde simples consultas SQL sejam mais adequadas; utilizar a ferramenta certa para o volume e o cálculo.

Cliente PostgreSQL apropriado à stack instalada e gerenciador de configuração por variáveis de ambiente.

Dados e infraestrutura

Banco institucional AC Social em PostgreSQL/Neon, de acordo com a documentação já entregue ao agente.

Armazenamento privado de objetos para PDFs/fotos digitalizadas (serviço privado a definir na infraestrutura da AC Social), com apenas metadados/referências no PostgreSQL. Não guardar documentos sensíveis em /public, em URL permanente aberta nem diretamente nos registros do banco, salvo decisão arquitetural expressa e justificada.

Configurar ambientes .env.example, .env.local e variáveis de servidor; segredos e tokens nunca devem aparecer no repositório, no navegador ou no log.

Respeitar o provedor de hospedagem já escolhido para o projeto; avaliar compatibilidade do backend Python e do processamento de arquivos sem assumir deploy automático em Vercel.

4. Princípios obrigatórios

Clean Architecture: camadas de apresentação, aplicação, domínio e infraestrutura; regras de negócio independentes do framework web.

Clean Code: código legível, componentes pequenos, responsabilidades claras, nomes descritivos e documentação relevante.

Segurança por padrão: mínimo privilégio, autenticação, autorização server-side, validação, logs seguros e proteção dos dados pessoais.

Abstração e reutilização: componentes de UI, hooks, serviços, schemas e políticas de autorização reutilizáveis.

Responsividade e acessibilidade: desktop, tablet e celular; uso por teclado, foco visível, rótulos corretos, mensagens de validação e contraste adequado.

Integração sem duplicidade: preservar IDs compartilhados e não copiar credenciais ou dados mestres sem necessidade.

Privacidade desde a concepção (privacy by design): finalidade explícita, minimização de dados, retenção definida, transparência e trilha de auditoria.

5. Navegação e telas

A aplicação autenticada usa sidebar, conforme prints recebidos pelo agente. As rotas sugeridas podem ser ajustadas aos padrões do projeto.

Rota sugerida

Tela

Visibilidade

/login

Login institucional, com visual baseado no print

Não autenticado

/cadastros

Lista de cadastros + botão Novo cadastro

Perfis autorizados do Serviço Social e outros explicitamente permitidos

/cadastros/[id]

Detalhes, histórico, documentos e ações de um cadastro

Perfil autorizado conforme regras de acesso

/analises

Indicadores, filtros e gráficos do Serviço Social

Perfis autorizados ao módulo

/tecnologia/conexao

Diagnóstico controlado de conexão e integrações

Somente equipe Tecnologia

Na sidebar, mostrar também atalho para Agenda Digital, usando a URL efetivamente recebida pelo agente. O atalho não substitui autenticação nem concede novos privilégios. Não exibir /tecnologia/conexao para outras equipes; adicionalmente, bloquear a rota e os endpoints no servidor. Esconder links na interface, sozinho, não constitui controle de acesso.

5.1 Tela de cadastros

Buscar pessoas já cadastradas e a existência de sua ficha no Serviço Social.

Exibir tabela apenas quando houver registros. Em caso de zero registros, mostrar um estado vazio bem identificado (“Nenhum cadastro encontrado”) e o botão Novo cadastro; não renderizar tabela vazia.

Colunas da tabela, conforme pedido: Nome do usuário, Data e horário do último atendimento, WhatsApp e Ações. Não incluir a coluna “Serviços de que participa”, pois essa ideia foi retirada expressamente.

Último atendimento: obter do registro de atendimentos institucionais associado à identidade única (usuario_id), respeitando o escopo autorizado para o Serviço Social e os contratos existentes. Exibir data/hora no fuso de João Pessoa (America/Fortaleza), com formatação legível. Se não houver atendimento, exibir “Sem atendimentos” em vez de inventar data.

WhatsApp: recuperar o telefone cadastrado no formulário e armazenar o valor normalizado (preferir E.164); exibir uma máscara legível (por exemplo (83) 9XXXX-XXXX, se for número brasileiro compatível) sem alterar o valor usado no link. O atalho deve abrir https://wa.me/<DDI+DDD+numero> somente com dígitos, sem o sinal +, espaços ou pontuação. Validar DDI/DDD/número, evitar gerar links inválidos e não incluir mensagem automática ou informações sensíveis. Se contato ausente/inválido, renderizar “Sem contato” e desabilitar o link. Usar rótulo acessível, indicar link externo e aplicar rel="noopener noreferrer" quando aplicável.

Ações por linha: Ver cadastro (abre modal visualizador PDF), Editar cadastro e Excluir cadastro. Também permitir consultar documentos em área autorizada. Exibir botões conforme permissões; confirmar exclusão e preferir exclusão lógica/arquivamento quando houver obrigação de guarda e histórico. A exclusão não deve remover automaticamente o registro institucional compartilhado ou documentos sujeitos a retenção.

Filtros, busca, paginação e loading/erro claros; evitar carregar todos os cadastros no navegador. A tabela e seus dados devem estar protegidos no backend, não apenas pela interface.

O botão Novo cadastro abre um modal acessível. Para formulários longos, utilizar etapas internas no modal ou diálogo em tela cheia no celular, preservando o requisito de abertura em modal.

5.2 Modal de cadastro

Seguir rigorosamente as seções, campos, máscaras e orientações do PDF de cadastro do Workspace.

Validar dados no frontend e no backend; mostrar erros próximos aos campos.

Antes de criar pessoa institucional nova, realizar busca de correspondência por ID e pesquisa por nome conforme a documentação do banco. ID existente é vínculo autoritativo; nome, isoladamente, gera alerta de possível duplicidade, nunca mesclagem automática. Quando disponíveis e permitidos, outros identificadores podem ajudar a confirmar correspondência.

Quando já existir a pessoa, associar o registro de Serviço Social ao usuario_id institucional, respeitando regras de cardinalidade e histórico.

Quando não existir, seguir o fluxo de criação autorizado no domínio institucional, sem criar uma segunda identidade para a mesma pessoa.

Operações devem ser transacionais e idempotentes quando couber, prevenindo duplo envio e registros duplicados.

5.3 Ação “Ver cadastro” — modal com visualizador de PDF

Requisito obrigatório acrescentado em 21/10/2026: na coluna Ações, o botão Ver cadastro deve abrir um modal com a ficha de cadastro renderizada em PDF, sem precisar sair da página de cadastros. No modal, devem existir as ações Imprimir e Baixar PDF, para imprimir uma cópia da ficha e arquivá-la fisicamente quando necessário.

Comportamento esperado:

Ao clicar em Ver cadastro, identificar o cadastro_servico_social_id da linha e requisitar ao backend o PDF completo da ficha, gerado a partir dos dados institucionais e específicos do Serviço Social autorizados, respeitando a estrutura do PDF-modelo de cadastro entregue ao agente.

Enquanto o arquivo é preparado, exibir indicador de carregamento; caso não haja permissão, cadastro ou falhe a geração, apresentar mensagem clara e permitir fechar o modal, sem vazar dados.

Abrir um Dialog do Material UI, com visualizador PDF incorporado (por exemplo visualizador nativo com fallback ou PDF.js), rolagem, zoom quando disponível, título contextual (“Cadastro — [nome]”) e botão de fechar. Usar diálogo amplo no desktop e tela cheia em celular; navegação por teclado, foco gerenciado e rótulos acessíveis.

Imprimir: disponibilizar botão próprio para acionar a impressão do documento PDF exibido, delegando a escolha da impressora e a confirmação ao diálogo do sistema/navegador; prever fallback de abertura segura do PDF caso um navegador bloqueie impressão embutida. Não imprimir automaticamente sem ação do usuário.

Baixar PDF: disponibilizar download autenticado do arquivo com nome sanitizado e previsível, por exemplo cadastro-servico-social-<id>-<data>.pdf, para arquivo físico/digital institucional. O botão deve entregar o mesmo conteúdo visualizado, sem expor URL de armazenamento pública.

Ao editar dados e salvar a ficha, novas visualizações devem refletir a versão atualizada dos dados; não entregar PDF desatualizado por cache. Incluir data/hora de geração e identificação ou versão do cadastro no documento para rastreabilidade.

Fechar o modal deve liberar recursos temporários, como URL.createObjectURL via URL.revokeObjectURL. Não armazenar PDF sensível no cache público, em /public, no localStorage ou em URL permanente acessível sem autenticação.

Implementação recomendada: endpoint próprio no FastAPI que monta PDF em memória com biblioteca server-side apropriada (por exemplo ReportLab ou WeasyPrint, segundo as dependências do ambiente e a fidelidade exigida pelo modelo). Usar HTTPS, checagem de autenticação e autorização antes de gerar ou transmitir o PDF, Content-Type: application/pdf, Content-Disposition: inline para visualizar e attachment para baixar. Aplicar Cache-Control: private, no-store, política de headers adequada e auditoria de visualização, download e pedido de impressão (o sistema registra o acionamento da impressão, não afirma que a impressora concluiu o trabalho). Os controles de impressão/baixar devem continuar sujeitos a permissões de acesso, e a cópia impressa deve seguir os procedimentos internos de guarda, circulação e descarte seguro.

Escopo do PDF: ficha cadastral formatada de forma legível e imprimível, conforme o modelo oficial; não anexar automaticamente laudos, fotografias, termos assinados ou outros documentos pessoais ao PDF principal. Esses anexos são visualizados separadamente, sob autorização, a menos que haja requisito institucional confirmado para uma composição específica.

5.4 Anexos dos atendimentos

Além do termo assinado ao final do cadastro, o registro de cada atendimento deve permitir anexar laudos, declarações e documentos apresentados pela pessoa atendida, por PDF ou imagem (seleção de arquivo, digitalização ou foto feita na aplicação). Vincular cada anexo ao atendimento e à pessoa/cadastro corretos, armazenar metadados, exibir lista de anexos, pré-visualização privada e operações permitidas conforme a política institucional.

Aceitar PDF e os formatos de imagem aprovados por segurança e compatibilidade; quando o aparelho produzir HEIC/HEIF ou outro formato não suportado no visualizador, oferecer conversão segura no servidor ou instrução para exportar em JPG/PNG. Não aceitar automaticamente todo MIME de imagem: vetar formatos ativos/perigosos, como SVG não sanitizado. Validar tipo real e tamanho no backend.

Associar a origem ao atendimento existente (atendimento_id) e garantir que este pertence ao mesmo usuario_id; não criar uma segunda identidade institucional para anexar arquivos.

Tratar separadamente documento de atendimento e termo de imagem/ciência do cadastro, com tipos, permissões e políticas de guarda específicos.

Em caso de cancelamento/falha do upload, não associar arquivo incompleto. Exibir sucesso/erro e manter trilha de auditoria para inclusão, consulta, substituição e eventual exclusão autorizada.

6. Fluxo de cadastro e termo assinado

Requisito adicionado em 21/10/2026: ao final do cadastro, permitir anexar o termo institucional assinado pelo usuário/responsável. O termo contém, segundo o relato, disposições sobre uso de imagem e concordância/ciência do cadastro. A aplicação precisa aceitar PDF, fotografia digitalizada ou imagem capturada na própria interface.

6.1 Etapas do fluxo

Identificação: procurar a pessoa por ID ou nome e confirmar vinculação ou novo cadastro institucional, seguindo a documentação existente.

Preenchimento: completar os dados do Serviço Social de acordo com o PDF-modelo.

Revisão: mostrar resumo antes de confirmar; permitir retornar para correções.

Formalização: apresentar orientações para imprimir/obter e assinar a versão institucional vigente do termo fora da aplicação. Oferecer botão Anexar termo assinado e opções Selecionar PDF, Selecionar imagem e Tirar foto.

Upload: receber arquivo ou captura, validar formato e tamanho no servidor, vincular ao cadastro e mostrar pré-visualização segura antes da confirmação.

Registro da decisão: registrar separadamente a ciência/aceite cadastral e, quando houver, a autorização ou não autorização de uso de imagem, conforme a versão assinada do termo. Não inferir consentimento apenas da presença de um arquivo. A equipe precisa registrar o resultado da leitura do documento; se o termo não individualizar essa decisão, revisar o modelo com a instituição antes de automatizar o campo.

Conclusão: apresentar confirmação do cadastro, status documental e identificação interna do registro. Se a formalização for institucionalmente obrigatória e faltar arquivo, manter pendente_documentacao em vez de marcar a etapa documental como concluída. Permitir retomada posterior a usuários autorizados.

6.2 Regras dos documentos

Formatos inicialmente permitidos: PDF, JPEG, PNG; outros formatos de imagem apenas após validação de segurança, compatibilidade e eventual conversão controlada. Limite configurável de tamanho, com mensagem de erro clara. Aplicar as mesmas garantias aos anexos de atendimentos.

Validar MIME real e assinatura/magic bytes no backend, e não confiar na extensão declarada pelo navegador; normalizar nomes de arquivo e impedir path traversal.

Fazer verificação antimalware ou quarentena conforme capacidade do ambiente; não disponibilizar o arquivo até validação.

Preferir captura do documento já assinado, não uma imagem recortada da assinatura isolada.

Em celular, abrir seletor/câmera quando disponível; em computador, oferecer upload de arquivo escaneado, com fallback caso acesso à câmera seja negado.

Usar object storage privado com ID aleatório por objeto, criptografia em trânsito e em repouso, acesso por backend ou URL assinada de curta duração e checagem de autorização a cada solicitação.

Exibir visualizador privado de PDF/imagem, sem indexação pública; permitir substituição controlada, com versionamento e auditoria.

Guardar metadados: id, usuario_id, cadastro_servico_social_id, tipo_documento, versao_termo, nome_original_sanitizado, mime, tamanho, hash_sha256, storage_key, enviado_por, enviado_em, status_verificacao, substitui_documento_id (se aplicável) e política de retenção definida.

Não chamar o escaneamento/foto de assinatura digital certificada. O upload fornece evidência documental de assinatura manuscrita; validade/procedimento devem ser definidos institucionalmente com orientação jurídica.

6.3 Separação entre cadastro e autorização de imagem

O termo físico pode combinar assuntos, mas o sistema precisa separar finalidades. A ciência do cadastro ou o fundamento jurídico necessário ao atendimento não equivale automaticamente a uma autorização para captar/divulgar imagem. Registrar autorização específica, seu alcance, versão, data, eventual revogação e responsável quando necessário. Recusar uso de imagem não deve, por si só, impedir o atendimento. Fluxos de alteração/revogação e o destino de imagens já publicadas precisam ser definidos com a AC Social.

Atenção especial: identificar crianças/adolescentes e pessoas representadas legalmente, confirmar regras de assinatura por responsável e submeter o conteúdo do termo e a base legal de cada operação à revisão do encarregado/jurídico. Não assumir que consentimento é necessariamente a única base legal para todos os dados do Serviço Social.

7. Autenticação e autorização

Reaproveitar a infraestrutura institucional existente, conforme documentação do banco. Não criar usuários paralelos nem copiar senhas para o Social Framework.

Identificar profissional autenticado e seu vínculo com a tabela real de equipes; conferir relações, status, papéis e permissões descritos na documentação.

Acesso às telas regulares: somente profissionais formalmente autorizados. Matriz de perfis exata depende da documentação e aprovação da instituição.

Página técnica /tecnologia/conexao: permitir exclusivamente quem pertence à equipe Tecnologia, verificada por dados atuais do banco. Não equiparar cargo administrativo, e-mail específico ou nome informal de equipe a essa permissão.

Implementar RBAC/ABAC com função centralizada de autorização na API e checagem por recurso; retornar 401/403 corretamente.

Incluir sessão segura, política de expiração/renovação, cookies HttpOnly/Secure/SameSite quando aplicável e proteção CSRF no modelo escolhido.

Nunca oferecer SQL arbitrário, credenciais, dumps de tabelas nem string de conexão na tela técnica. Nela, mostrar apenas status sanitizado de banco/API, latência, integridade das integrações e diagnóstico não sensível.

8. Modelo lógico de dados (conceitual; conferir nomes reais)

Não executar migrações sobre tabelas compartilhadas antes de inspecionar contratos existentes. A documentação prévia do ecossistema recomenda pessoas com ID único, além de módulos específicos por serviço e eventos da jornada. Novas estruturas propostas:

cadastros_servico_social
- id
- usuario_id                    -> FK para pessoa institucional existente
- dados_formulario              -> modelo estruturado a derivar do PDF, não JSON genérico sem validação
- status                        -> rascunho | pendente_documentacao | concluido | inativo
- criado_por_profissional_id
- atualizado_por_profissional_id
- criado_em
- atualizado_em

documentos_servico_social
- id
- cadastro_servico_social_id
- usuario_id
- tipo_documento               -> termo_imagem_ciencia | laudo | documentacao_atendimento | outro_tipo_permitido
- atendimento_id                -> FK opcional para atendimento existente, exigido em anexos de atendimento
- storage_key                   -> referência privada, nunca URL pública
- versao_termo
- nome_original_sanitizado
- mime_type
- tamanho_bytes
- hash_sha256
- status_verificacao
- criado_por_profissional_id
- criado_em
- substitui_documento_id

manifestacoes_servico_social
- id
- cadastro_servico_social_id
- documento_id                  -> evidência vinculada
- finalidade                    -> ciencia_cadastro | uso_imagem (se aplicável)
- resultado                     -> aceito | recusado | nao_registrado | revogado
- fundamento_juridico           -> definido pela instituição para cada finalidade
- versao_texto
- registrado_por_profissional_id
- registrado_em
- revogado_em

auditoria_servico_social
- id
- ator_profissional_id
- acao
- entidade_tipo
- entidade_id
- timestamp
- metadados_minimos             -> sem conteúdo sensível ou arquivo em logs

Respeitar as entidades compartilhadas do ecossistema (usuarios, profissionais, atendimentos, encaminhamentos, histórico), se existirem com esses nomes no banco real. Nomes acima são propostas lógicas, não confirmação do esquema físico. Antes de gravar eventos compartilhados, conferir APIs e responsabilidades dos módulos proprietários.

9. API sugerida (contratos iniciais)

Os endpoints são sugestões internas versionadas, sujeitas às convenções e permissões existentes:

GET    /api/v1/me
GET    /api/v1/usuarios?busca=...             # consulta autorizada para evitar duplicatas
GET    /api/v1/servico-social/cadastros
POST   /api/v1/servico-social/cadastros
GET    /api/v1/servico-social/cadastros/{id}
PATCH  /api/v1/servico-social/cadastros/{id}
DELETE /api/v1/servico-social/cadastros/{id}    # política de exclusão lógica/retencao; permissão específica
GET    /api/v1/servico-social/cadastros/{id}/pdf               # visualizar (inline), autenticado
GET    /api/v1/servico-social/cadastros/{id}/pdf?download=true # baixar (attachment), autenticado
POST   /api/v1/servico-social/cadastros/{id}/documentos
GET    /api/v1/servico-social/cadastros/{id}/documentos
GET    /api/v1/servico-social/documentos/{id}/visualizar
GET    /api/v1/servico-social/atendimentos/{id}/documentos
POST   /api/v1/servico-social/atendimentos/{id}/documentos   # laudos, comprovantes e demais imagens/PDFs
POST   /api/v1/servico-social/cadastros/{id}/manifestacoes
GET    /api/v1/servico-social/analises/resumo
GET    /api/v1/tecnologia/conexao/status    # equipe Tecnologia somente

Criar contratos Pydantic, erros padronizados, OpenAPI documentado, limites de paginação e rate limiting adequado. Para os endpoints de PDF, enviar conteúdo binário correto, impedir caching compartilhado e exigir autorização também no acesso e no download; para documentos de atendimento, conferir vínculo e permissões sobre atendimento_id. Restringir consultas à informação necessária ao trabalho; aplicar autorização por usuário e por operação também nos downloads. Não retornar storage_key ou dados confidenciais diretamente ao cliente, exceto quando estritamente necessário e seguro.

10. Análise de dados

Na rota /analises, apresentar indicadores derivados dos registros autorizados do Serviço Social, como total de cadastros, novos cadastros no período, pendências documentais, evolução temporal e outras métricas formalmente aprovadas. Permitir filtro temporal e estados de carregamento/erro. Não definir indicadores adicionais por inferência de campos inexistentes; primeiro validar o PDF, a documentação do banco e necessidades do setor.

Fluxo recomendado: SQL parametrizado e consultas agregadas -> serviço Python -> Pandas/NumPy quando necessários -> API com JSON resumido -> React Query -> componentes MUI e gráficos da biblioteca escolhida após validação. Restringir dados exportados, minimizar identificadores e evitar detalhamento que permita reidentificação em grupos pequenos. Avaliar futuramente integração dos indicadores à Plataforma Consolidada de Análise de Dados, segundo os contratos existentes.

11. LGPD e segurança — requisitos não funcionais obrigatórios

O Social Framework lida potencialmente com dados pessoais e dados pessoais sensíveis; a classificação de cada campo depende do PDF. Implementar:

Mapeamento de finalidades, dados e bases legais: documentar para cada campo/documento por que é coletado, quem acessa, por quanto tempo é retido e qual fundamento jurídico se aplica. Para dados sensíveis, avaliar especificamente art. 11 da LGPD.

Necessidade e minimização: coletar apenas o que serve ao atendimento e exigir apenas o estritamente necessário.

Transparência: informar os titulares sobre uso, acesso, compartilhamento, retenção e contato do controlador/encarregado conforme política institucional.

Separação de consentimentos/autorizações: não confundir formalização do cadastro com autorização de uso de imagem; registrar manifestação específica e permitir revisão/revogação onde aplicável.

Acesso mínimo necessário: autorização por equipe/papel, por registro, nos arquivos e nos endpoints; sem exposição de documentos por links permanentes.

Transporte e armazenamento seguros: HTTPS/TLS, criptografia adequada em repouso, controle de chaves e segregação de ambientes.

Auditoria: registrar acesso e alterações a registros e documentos (quem/quando/o quê), sem copiar conteúdo sensível para logs. Proteger logs e determinar retenção própria.

Retenção e descarte: definir política institucional antes de implementar exclusão definitiva. Respeitar obrigações legais de guarda, pedidos de titulares, backups e fluxo de exclusão/anonimização quando cabível. Não presumir eliminação automática após revogação sem avaliação da base legal.

Direitos dos titulares: criar procedimento administrativo rastreável para consulta, correção, informação, revogação e pedidos de eliminação quando aplicável; controles no sistema podem ser graduais.

Resposta a incidentes: mecanismo de detecção, isolamento, investigação, preservação de evidências e reporte segundo processo institucional e regras aplicáveis da ANPD.

Terceiros: verificar contratos e condições de provedores de hospedagem, storage, telemetria e backup; evitar transferência ou exposição não autorizada.

Teste e revisão: testar autorização horizontal e vertical, uploads maliciosos, exposição de PDFs, enumeração de IDs, segredos, logs e comportamento em erro.

A LGPD exige medidas técnicas e administrativas de segurança desde a concepção (art. 46). A ANPD recomenda controles de autenticação, autorização e auditoria. Este planejamento é técnico e não substitui a validação jurídica do termo, das bases legais, da retenção nem da política de privacidade.

12. Estrutura de pastas sugerida

social-framework/
├── frontend/
│   ├── src/app/                 # rotas Next.js
│   ├── src/components/          # sidebar, tabela, modais, uploader, PDFViewer, toolbar imprimir/baixar
│   ├── src/features/            # auth, cadastros, documentos, analises, tecnologia
│   ├── src/lib/                 # axios, React Query, tema e utilitários
│   └── src/types/
├── backend/
│   ├── app/api/v1/
│   ├── app/core/                # configurações, segurança, autorização
│   ├── app/domain/              # entidades e regras
│   ├── app/application/         # casos de uso
│   ├── app/infrastructure/      # repositórios, PostgreSQL, object storage
│   ├── app/schemas/             # Pydantic
│   ├── app/analytics/           # Pandas/NumPy
│   └── tests/
├── docs/
│   ├── arquitetura.md
│   ├── banco-contratos.md
│   ├── api.md
│   ├── lgpd-matriz-tratamentos.md
│   └── decisoes.md
├── .env.example
└── README.md

Pode adaptar para monorepo ou convenção já adotada no repositório; evitar duplicar configuração.

13. Plano de execução em etapas

Fase 0 — levantamento e compatibilidade: conferir PDF, prints, link da Agenda, documentação do banco, tabelas e políticas de autenticação; identificar campos sensíveis; mapear relações reais e revisar modelo do termo. Registrar pendências sem inventar contratos.

Fase 1 — bootstrap: iniciar Next.js/TypeScript e FastAPI/Python; instalar MUI, React Icons, Axios, TanStack React Query, React Hook Form, Zod, Pydantic, Pandas, NumPy e bibliotecas de persistência; configurar lint, format, testes, .env.example, CORS restrito e healthcheck.

Fase 2 — login e layout: integrar autenticação institucional, implementar página de login seguindo print, app shell com sidebar responsiva, atalho Agenda Digital e guards nas rotas e APIs; restringir tela técnica à equipe Tecnologia.

Fase 3 — cadastro, tabela e persistência: relacionar pessoa institucional por ID e identificar potenciais duplicidades; tabela condicional com nome, última data/hora de atendimento, WhatsApp formatado e ações Ver/Editar/Excluir; modal de cadastro fiel ao PDF; validar, gravar, listar, visualizar e editar segundo permissões; exclusão conforme política de guarda; atualizar React Query com invalidação de cache após mutações.

Fase 4 — impressão e documentos: implementar modal "Ver cadastro" com PDF gerado pelo backend e botões Imprimir e Baixar PDF; aplicar permissões, auditoria e layout imprimível. Adicionar etapa final de formalização; upload do termo PDF/foto/câmera; anexos PDF/imagem por atendimento (laudos, documentação), validações e storage privado; preview seguro; status pendente/concluído; registrar manifestação distinta sobre uso de imagem; versionar anexos e auditar ações.

Fase 5 — análises: implementar endpoints agregados, uso de Pandas/NumPy quando necessário, filtros e dashboards responsivos; testar confidencialidade e agregações.

Fase 6 — qualidade e entrega: testes unitários/integrados/E2E, revisão de segurança e privacidade, migração revisada, deploy seguro, documentação, instruções de uso, backup/recuperação e checklist de produção.

14. Critérios de aceite do MVP

Projeto iniciado, bibliotecas instaladas, README e exemplo de variáveis de ambiente disponíveis.

Login institucional funcional e perfis/autorização conferidos no banco existente.

Sidebar consistente com prints, responsiva, incluindo Cadastros, Análises, atalho Agenda Digital e tela técnica apenas para Tecnologia.

Usuário de outra equipe não acessa nem a interface nem endpoints da área técnica.

Lista de cadastros oculta a tabela quando vazia e mostra estado vazio com botão de ação.

Tabela com Nome, Data e horário do último atendimento (ou "Sem atendimentos"), WhatsApp com máscara e link validado, e Ações: Ver cadastro / Editar cadastro / Excluir cadastro; sem coluna de serviços participantes.

Botão Ver cadastro abre modal com ficha renderizada em PDF, sem sair da tabela, com carregamento/erro e visualização adequada em desktop e celular.

Modal PDF possui botões Imprimir (abre impressão do navegador/sistema sob comando do usuário) e Baixar PDF (download autorizado, nome adequado) para guardar uma cópia da ficha em arquivo físico.

PDF reproduz dados atualizados do cadastro e segue modelo oficial; autorização server-side e proteção contra acesso não autorizado, cache público e vazamento de URLs.

Editar atualiza os dados da tabela/PDF; excluir exige permissão, confirmação e respeita retenção e vínculos com o banco compartilhado.

Botão Novo cadastro abre modal fiel aos campos do PDF.

Pesquisa por ID/nome evita cadastros duplicados sem mesclar pessoas apenas pelo nome.

Dados novos do Serviço Social mantêm usuario_id institucional.

Cadastro permite anexar termo assinado por PDF, imagem digitalizada e captura pela câmera, com preview seguro e opção de substituir versão.

Registros de atendimento permitem anexar laudos e outros documentos por PDF/imagem (inclusive foto), associar ao atendimento correto e consultar arquivos em visualizador protegido.

Documentos não possuem URLs públicas ou acesso sem autorização.

Termo, ciência cadastral e decisão sobre imagem possuem rastreabilidade sem tratar arquivo anexado como autorização automática.

Pendência documental é identificável e pode ser resolvida posteriormente.

Página de análises fornece indicadores autorizados e consistentes.

Logs, retenção, privilégio mínimo e controles LGPD implementados e revisados com a instituição.

Testes de autorização, uploads, validação e erros passam antes do deploy.

15. Pendências que o agente deve conferir — não bloquear bootstrap

Versão e conteúdo exatos do PDF-modelo de cadastro e do termo institucional; se existirem dados sensíveis, ajustar permissões por campo/documento.

Nomes físicos, tipos e relacionamentos das tabelas do Neon, mecanismos de autenticação, profissionais e equipes.

Prints de login/sidebar/telas já enviados ao agente de desenvolvimento e URL da Agenda Digital.

Provedor privado de objetos para documentos, quotas e política de backup/retention.

Matriz aprovada de quem pode ver, editar, excluir, imprimir ou baixar fichas e documentos, incluindo guarda física e acesso à informação em papel.

Bases legais por finalidade, termo de imagem, regras para menores/responsáveis, período de guarda e processo de revogação.

Enquanto essas pendências são validadas, o agente deve executar as fases independentes, como estrutura do projeto, dependências, arquitetura, tema base, testes e preparação de clientes de API, sem inventar detalhes do domínio.

16. Referências

Arquitetura institucional já documentada: ac-social-arquitetura.md e ac-social-arquitetura-jornada-unificada.md (referências anteriores da AC Social; verificar o conteúdo vigente no repositório).

Lei nº 13.709/2018 (LGPD): https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm

Guia da ANPD sobre segurança da informação: https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/guia-orientativo-sobre-seguranca-da-informacao-para-agentes-de-tratamento-de-pequeno-porte

Ordem de trabalho ao agente: comece agora pelo levantamento técnico e bootstrap (Fases 0 e 1), configure as dependências, examine os materiais já enviados no Workspace, implemente as camadas e evolua até os critérios de aceite. Documente incompatibilidades reais; nunca improvise campos, tabelas, permissões ou conteúdo de consentimento não confirmados.