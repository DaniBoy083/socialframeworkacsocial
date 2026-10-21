# Inventário do PDF-modelo

Fonte: `docs/models/Cadastro_AC_Social novo.pdf`, duas páginas, inspecionadas por extração de texto e renderização visual em 21/10/2026. Documento original preservado. O logo em `public/brand/ac-social.png` é o recurso original extraído desse PDF, com seu canal de transparência; não foi redesenhado. Não é uma cópia da imagem de pacientes ou do termo.

## Ordem e rótulos observados

| Seção | Campos na ordem do modelo |
|---|---|
| 1. IDENTIFICAÇÃO DO USUÁRIO | Nome completo; Data de nascimento; CPF; NIS; Filiação; Etnia; Escolaridade |
| 2. CONTATO E ENDEREÇO | Endereço; CEP; Telefone; Situação habitacional |
| 3. SITUAÇÃO SOCIOECONÔMICA | Renda familiar; Beneficios (grafia do modelo) |
| 4. COMPOSIÇÃO FAMILIAR | Tabela: Nome; Parentesco; Idade/DN; Escolaridade; PCD; Trabalho; Renda; NIS. Continua no topo da segunda página |
| 5. PARECER TÉCNICO | Encaminhamento/acompanhamento; Responsável Técnico; Usuário/Responsável; Data |
| Formalização | TERMO DE RESPONSABILIDADE E USO DE IMAGEM; declaração conjunta; Assinatura |

## Ambiguidades que não podem virar regras inventadas

O PDF não especifica obrigatoriedade por campo, máscaras, enumerações de etnia/escolaridade/benefícios, limites de família, formato de renda nem se `Idade/DN` representa um campo ou duas alternativas. A área de parecer é livre. Confirmar essas definições com o Serviço Social antes de liberar formulário ou DTO de escrita. Os requisitos do cadastro comum (nome, nascimento, normalização e versões) continuam regidos pelo ACS-IDENTITY-1.

O termo existe no próprio modelo, mas não contém versão institucional explícita nem escolhas distintas para ciência do cadastro e uso de imagem. Portanto, sua existência não equivale a aprovação do texto ou do procedimento. A decisão de imagem deve ter finalidade, alcance, versão, responsável, data e eventual revogação próprios; recusa não impede atendimento. Não presumir consentimento pela assinatura ou pelo upload.

## Implementação desta etapa

O modal Novo cadastro informa as seções confirmadas e a indisponibilidade da integração. Não coleta dados que não pode gravar, não simula sucesso e não se apresenta como o formulário final. O formulário operacional, revisão e formalização permanecem pendentes na auditoria.

A ficha PDF futura será gerada no backend, com versão e data/hora, sem incorporar laudos ou anexos automaticamente. Ver cadastro abrirá um Dialog responsivo, com impressão/download autorizados e liberação de URLs temporárias. Esses fluxos ainda não foram implementados.
