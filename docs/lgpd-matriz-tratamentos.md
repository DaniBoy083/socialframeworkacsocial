# Matriz inicial de tratamentos — pendente de validação institucional

Este registro técnico identifica tratamentos previstos no planejamento/PDF. Não atribui bases legais, prazos de guarda ou consentimentos por suposição. A validação cabe à instituição e ao seu encarregado/jurídico; não há declaração de conformidade jurídica integral.

| Grupo | Finalidade prevista | Dados / atenção | Controle atual | Definições pendentes |
|---|---|---|---|---|
| Autenticação | Identificar profissional e autorizar operações | E-mail, ID, equipes; senha apenas para verificação do hash original | Sessão própria, origem, expiração, hash do token, erros sanitizados | Homologar verificador e migração; retenção de sessões/tentativas; rate limit global |
| Identidade da pessoa | Localizar pessoa sem duplicar UUID | Nome, nascimento, contato livre, escopo | Consulta preparada com escopo/paginação; política desligada | Matriz de leitura e auditoria durável de acessos |
| Identificação social | Atendimento cadastral | CPF, NIS, filiação, etnia, escolaridade; etnia requer tratamento especialmente restrito | Não coletado nesta etapa | Necessidade por campo, base legal, acesso, obrigatoriedade, prazo |
| Contato e endereço | Contato institucional | Endereço, CEP, telefone, moradia | Não coletado; normalizador de WhatsApp aceita apenas telefone explícito | Fonte de telefone social, uso autorizado, correção e retenção |
| Situação econômica/família | Avaliação social | Renda, benefícios, relações familiares, PCD; familiares são titulares distintos | Não coletado | Minimização, proteção de dados sensíveis, representação, guarda |
| Parecer técnico | Acompanhamento social | Narrativa e encaminhamentos; pode conter dados sensíveis | Não coletado | Permissão por registro/campo, regras profissionais, histórico e correção |
| Documentos | Evidência e acompanhamento | Termo, laudos, fotos, identificação e assinaturas | Upload/download ausentes | Storage privado, criptografia/chaves, quarentena/antimalware, acesso, retenção e versões |
| Manifestação sobre imagem | Registrar decisão específica | Resultado, finalidade, alcance, versão, data e representante | Sem manifestação inferida | Texto individualizado, procedimento de revogação e menores/responsáveis |
| Fichas PDF e impressos | Consulta e arquivo físico autorizado | Reprodução de dados cadastrais | Geração/download/impressão ainda ausentes | Permissões separadas, auditoria do pedido, guarda/circulação/descarte de papel |
| Análises | Gestão agregada | Contagens autorizadas | Sem dados demonstrativos nem métricas fabricadas | Indicadores, limite para grupos pequenos e risco de reidentificação |
| Auditoria | Rastreabilidade mínima | Ator, ação, recurso, resultado e data | Conteúdo de erro/SQL não é exposto; trilha durável ainda pendente | Repositório protegido, imutabilidade, retenção, leitura restrita e resposta a incidentes |

Antes de produção, formalizar transparência e canal do encarregado; procedimentos de consulta/correção/revogação; guarda e descarte de registros/backups/impressos; resposta a incidentes; contratos de terceiros e condições de hospedagem. Nenhum cadastro de pessoa ou documento foi inserido no banco nesta entrega.
