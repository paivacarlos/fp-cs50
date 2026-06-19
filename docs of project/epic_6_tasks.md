# Epic 6: History Dashboard & Retro Modal
Viewing past conferences securely.

This document breaks down the tasks of Epic 6 into atomized steps to track implementation progress, commits, and Pull Requests. It also includes the postponed E2E Playwright UI tests at the end.

---

## Technical Tasks

### Fase 1: Backend & API (Database & Routes Layer)
- [x] **Task 6.1.1:** Criar a rota `GET /history` em [routes/main.py](../routes/main.py) protegida por `@login_required` que renderiza o template `templates/history.html` com uma lista vazia.
- [x] **Task 6.1.2:** Implementar a query no banco de dados na rota `GET /history` para recuperar apenas as conferências finalizadas (`headline IS NOT NULL AND chronicle IS NOT NULL`) associadas ao `user_id` da sessão, ordenadas por `created_at DESC`, e passá-las ao template.
- [x] **Task 6.1.3:** Escrever testes de integração em [tests/test_api.py](../tests/test_api.py) para garantir que o acesso à rota `/history` redirecione usuários não autorizados para `/login` e retorne `200 OK` para usuários logados.
- [ ] **Task 6.1.4:** Criar o novo endpoint `GET /api/conference/<int:conference_id>/details` em [routes/api.py](../routes/api.py) protegido por `@login_required` que valida a propriedade da conferência, busca os dados da conferência e todas as rodadas (`rounds`) associadas, e retorna em formato JSON.
- [ ] **Task 6.1.5:** Escrever testes de integração em [tests/test_api.py](../tests/test_api.py) cobrindo o endpoint de detalhes: sucesso (retorno correto de JSON estruturado), erro 404 (conferência não existente) e erro 403 (acesso não autorizado a conferências de outros usuários).

### Fase 2: Interface do Histórico & Navegação (Frontend Layer)
- [ ] **Task 6.2.1:** Criar o novo template `templates/history.html` herdando de [templates/base.html](../templates/base.html).
- [ ] **Task 6.2.2:** Desenhar a marcação HTML em `history.html` contendo um grid ou linha do tempo exibindo cartões (`.history-card`) para cada conferência (com data formatada, manchete e miniatura do screenshot).
- [ ] **Task 6.2.3:** Criar a folha de estilo [static/css/history.css](../static/css/history.css) (ou atualizar a existente) aplicando design moderno nos cartões do histórico (glassmorphism, bordas com degradê e micro-animações de escala no hover).
- [ ] **Task 6.2.4:** Atualizar a navegação global adicionando links cruzados:
  - Um link de acesso rápido ao histórico (ex: "Ver Histórico") no cabeçalho ou rodapé de [templates/setup.html](../templates/setup.html).
  - Um link de retorno (ex: "← Voltar ao Setup") no topo ou rodapé de [templates/history.html](../templates/history.html).

### Fase 3: Modal de Retrospectiva & Interatividade (JS Layer)
- [ ] **Task 6.3.1:** Desenhar a marcação HTML do Modal de Retrospectiva (`#retro-modal`) em `history.html` (contendo botão de fechar, área para transcrição das perguntas/respostas e área para renderizar o jornal).
- [ ] **Task 6.3.2:** Estilizar o modal (`.modal-overlay`, `.modal-content`, bolhas de chat de Q&A) em [static/css/history.css](../static/css/history.css), configurando um overlay translúcido e animações suaves de entrada (fade-in / scale).
- [ ] **Task 6.3.3:** Implementar a lógica JavaScript em `history.html` para:
  - Adicionar ouvintes de evento de clique em cada `.history-card`.
  - Fazer a requisição via `fetch()` para o endpoint `/api/conference/<id>/details`.
  - Preencher dinamicamente a estrutura de chat (perguntas/respostas) e o layout de jornal dentro do modal.
  - Exibir o modal e tratar as ações de fechamento (clique no botão "X", na área externa ou tecla Esc).

### Fase 4: Testes de Interface E2E do Projeto (UI Quality Assurance)
- [ ] **Task 6.4.1:** Escrever o teste E2E do **Epic 5** com Playwright em [tests/test_ui.py](../tests/test_ui.py) simulando o fluxo de envio de respostas de um técnico até a finalização da Rodada 3 e o redirecionamento para o jornal, validando os elementos visíveis na página final.
- [ ] **Task 6.4.2:** Escrever o teste E2E do **Epic 6** com Playwright em [tests/test_ui.py](../tests/test_ui.py) simulando o fluxo de navegação:
  - Fazer login e ir para a rota `/history`.
  - Clicar em um cartão de histórico e validar se o Modal de Retrospectiva abre corretamente.
  - Verificar se a transcrição da conferência (perguntas e respostas) e a manchete estão legíveis dentro do modal.
