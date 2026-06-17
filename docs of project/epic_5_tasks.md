# Epic 5: Chronicle Generation & Newspaper Styling
Transforming the transcript into a stylized sports article.

This document breaks down the tasks of Epic 5 into atomized steps to track implementation progress, commits, and Pull Requests.

---

## Technical Tasks

### Fase 1: Backend & Integração com Gemini (Services Layer)
- [x] **Task 5.1.1:** Criar a classe/modelo Pydantic `ChronicleResponse` com os campos `headline: str` e `chronicle: str` em [services/gemini.py](../services/gemini.py).
- [x] **Task 5.1.2:** Implementar a função `generate_chronicle(image_path: str, context: str, history: list) -> dict` em [services/gemini.py](../services/gemini.py), utilizando `response_mime_type="application/json"` e passando a classe `ChronicleResponse` no `response_schema` do Gemini SDK.
- [x] **Task 5.1.3:** Escrever testes unitários em [tests/test_gemini.py](../tests/test_gemini.py) para mockar a API do Gemini e garantir que `generate_chronicle` processe e retorne a estrutura de JSON correta.

### Fase 2: Persistência & Fluxo dos Endpoints (Database & Routes Layer)
- [x] **Task 5.2.1:** Atualizar o endpoint `POST /api/conference/answer` em [routes/api.py](../routes/api.py) para detectar quando a rodada finalizada for a **Rodada 3**.
- [x] **Task 5.2.2:** Integrar a chamada a `generate_chronicle` quando a Rodada 3 for respondida, passando o histórico de perguntas/respostas acumulado no banco, o screenshot e o contexto inicial.
- [x] **Task 5.2.3:** Criar uma transação/query SQL para atualizar os campos `headline` e `chronicle` na tabela `conferences` para a conferência atual.
- [x] **Task 5.2.4:** Criar uma nova rota `GET /conference/<int:conference_id>/newspaper` em [routes/main.py](../routes/main.py) protegida por `@login_required` que valida se a conferência pertence ao usuário logado, recupera os dados do banco e renderiza o template do jornal.
- [x] **Task 5.2.5:** Adicionar testes de integração em [tests/test_api.py](../tests/test_api.py) cobrindo:
  - O sucesso do salvamento da manchete e crônica na finalização da Rodada 3.
  - A proteção de acesso não autorizado e autorização correta ao visualizar a rota `/conference/<id>/newspaper`.
  - O rollback do banco caso a geração da crônica pelo Gemini falhe na Rodada 3.

### Fase 3: Interface do Jornal & Estilização (Frontend Layer)
- [x] **Task 5.3.1:** Criar o novo template `templates/newspaper.html` herdando de [templates/base.html](../templates/base.html).
- [ ] **Task 5.3.2:** Desenhar a marcação HTML semântica em `newspaper.html` contendo:
  - Cabeçalho de jornal clássico (ex: "THE DAILY PRESS" com fonte gótica/serifada, data e autoria).
  - A manchete principal (`headline`) com destaque visual.
  - A imagem do screenshot (estilizada com filtro vintage, como tons de cinza ou sépia).
  - O texto da crônica (`chronicle`).
- [ ] **Task 5.3.3:** Criar a folha de estilo [static/css/newspaper.css](../static/css/newspaper.css) aplicando cores de fundo estilo pergaminho/papel envelhecido (`#f4ebd0` ou similar) e tipografia clássica com fontes serifadas.
- [ ] **Task 5.3.4:** Implementar layout de colunas no corpo da crônica usando CSS Columns (`column-count`, `column-gap`, e `column-rule`).
- [ ] **Task 5.3.5:** Aplicar efeitos de micro-animação (ex: textura sutil de papel) e estilo de Drop Cap (primeira letra do texto da crônica estilizada de forma clássica).
- [ ] **Task 5.3.6:** Atualizar a lógica do JavaScript frontend (que faz as requisições de Q&A) para redirecionar o usuário para a rota `/conference/<id>/newspaper` assim que receber o status de conclusão da Rodada 3.

### Fase 4: Testes de Interface E2E (UI Quality Assurance)
- [ ] **Task 5.4.1:** Escrever um teste E2E com Playwright em [tests/test_ui.py](../tests/test_ui.py) simulando o fluxo de envio de respostas de um técnico até a finalização da Rodada 3 e o redirecionamento.
- [ ] **Task 5.4.2:** Adicionar asserts no teste E2E para checar se a manchete, o texto da crônica e o screenshot estilizado estão visíveis na página do jornal.
