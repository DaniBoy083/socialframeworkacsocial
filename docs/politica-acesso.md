# Política de acesso do Social Framework

Revisão de 21/10/2026. Autoridade: instrução expressa do responsável para permitir login somente a Serviço Social e Tecnologia. Os nomes físicos foram confirmados em consulta READ ONLY a `equipes_profissionais.name`: **`Serviço social`** (segundo “social” em minúscula) e **`Tecnologia`**.

## Login e sessão

É necessário fornecer e-mail/senha institucionais válidos e pertencer a pelo menos uma dessas duas equipes. O servidor consulta a associação pelo ID do profissional, usando `professional_ids_json`; não recebe equipe, papel ou escopo do navegador. A comparação usa nomes exatos, sem aliases, aproximação, remoção de acentos, conversão de caixa ou dedução por cargo/e-mail. Equipes adicionais no cadastro não impedem o acesso de quem também pertence a uma equipe autorizada, mas não concedem permissões extras.

A elegibilidade está fixa em `backend/app/domain/access.py` (`LOGIN_TEAMS`, `can_login`), aplicada pelo serviço de autenticação no login e na revalidação de cada operação. `SOCIAL_ACCESS_POLICY` não pode ampliar a lista: a configuração rejeita chaves de outras equipes e o domínio também ignora concessões por equipes alheias. Não existe conta local/fallback nem exceção de produção/desenvolvimento para terceiros.

| Vínculo institucional atual | Login com senha válida | Acesso técnico | Acesso a dados sociais |
|---|---|---|---|
| `Serviço social` | Permitido | Negado | Exige permissão de módulo aprovada |
| `Tecnologia` | Permitido | Permitido | Não é concedido implicitamente |
| Ambas | Permitido | Permitido | Somente permissões explícitas das equipes autorizadas |
| Uma das duas + outras equipes | Permitido | Conforme vínculo com Tecnologia | Outras equipes não acrescentam permissões |
| Apenas outra equipe ou nenhum vínculo | Negado | Negado | Negado |
| Nome parecido, caixa/acentuação diferente ou espaço extra | Negado, salvo outro vínculo autorizado | Negado | Negado |

No login, senha incorreta ou ausência de equipe autorizada devolvem o mesmo **401** genérico, sem criar cookie/sessão e contando a tentativa recusada. Falha de infraestrutura/configuração continua **503**, sem simular senha incorreta. A sessão é reavaliada contra as equipes atuais: perder o último vínculo autorizado faz os endpoints retornarem **401** na próxima verificação. O frontend limpa seu cache em memória e volta ao login ao receber 401. Ter sessão válida, porém faltar permissão de uma operação, retorna **403** e não é tratado como senha errada.

A perda do vínculo bloqueia o uso do token enquanto o profissional estiver fora das equipes; este fluxo não apaga fisicamente o token no banco e não é anunciado como revogação permanente. Logout e expiração mantêm seus controles próprios. A troca entre equipes autorizadas recalcula permissões e acesso técnico na próxima requisição.

## Permissões de módulos

Entrar na aplicação é diferente de consultar cadastros/prontuários. `SOCIAL_POLICY_APPROVED=false` e `SOCIAL_ACCESS_POLICY={}` continuam seguros por padrão: ambas as equipes podem autenticar quando a infraestrutura estiver pronta, mas não recebem leitura de dados pessoais implicitamente. Nesta etapa, as únicas permissões reconhecidas são `registry:read`, `registrations:read` e `analytics:read`; a matriz de operações ainda requer homologação e auditoria durável antes de habilitar dados reais.

A tela de diagnóstico continua exclusiva de Tecnologia no servidor e na API. Não alterar essa regra para permitir acesso técnico ao Serviço Social. A autenticação não habilita escrita, documentos, impressão, download ou serviços ainda pendentes.

## Evidência e operação

Consulta de 21/10/2026 confirmou ambas as equipes, sem ler membros ou credenciais. O diagnóstico `backend/scripts/check_access.py` verifica apenas nomes das equipes, presença das tabelas próprias de autenticação e flags de configuração. Nesta revisão, o escopo estava **não configurado**, a política de módulos **desativada** e as tabelas `ss_sessions`/`ss_login_attempts` **ausentes**. Portanto, a regra está implementada e testada, mas o login real ainda depende da preparação/homologação da infraestrutura. Nenhuma migração ou alteração de membros foi executada.

O verificador scrypt foi conferido por leitura do adaptador ABA em `../abaframeworkacsocial/src/modules/auth/application/passwordHash.ts`; usa derivação de 64 bytes com parâmetros padrão do Node, salt textual e comparação constante. O teste Python usa um vetor sintético independente produzido pelo Node 22. Isso verifica compatibilidade de implementação; não substitui teste de credenciais reais no destino.

Os testes cobrem as duas equipes, dupla associação, senha errada, ausência/variação de equipe, política indevida, adulteração de campos/cabeçalhos, perda de vínculo, troca de equipe, cookie/sessão e negação dos endpoints. Repositórios HTTP de teste são sintéticos e isolados do banco institucional. Veja a [auditoria](AUDITORIA_APLICACAO_E_PRINCIPIOS.md) para os resultados e os demais critérios ainda pendentes do MVP.
