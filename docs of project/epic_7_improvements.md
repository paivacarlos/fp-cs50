# Epic 7: Refinements & User Experience (UX) Optimizations
Polishing navigation, direct history access, and robust error handling.

This document breaks down the tasks of Epic 7 into atomized steps to track implementation progress, commits, and Pull Requests.

---

## Technical Tasks

### Fase 1: Redirecionamento Direto do Histórico (Remoção do Modal)
- [ ] **Task 7.1.1:** Atualizar a marcação em [templates/history.html](../templates/history.html) para converter os cartões `.history-card` em links `<a>` apontando para `/conference/<id>/newspaper`, removendo o esqueleto do modal `#retro-modal`.
- [ ] **Task 7.1.2:** Limpar o bloco de scripts `{% block extra_js %}` em [templates/history.html](../templates/history.html) removendo os ouvintes de evento de clique, fetches e controle de modal que se tornaram obsoletos.
- [ ] **Task 7.1.3:** Limpar a folha de estilo [static/css/history.css](../static/css/history.css) removendo as regras de estilos destinadas ao modal (`.modal-overlay`, `.modal-content`, `.chat-transcript`, etc.).
- [ ] **Task 7.1.4:** Garantir que o link `.history-card` herde as cores padrões e não exiba decorações de sublinhado padrão dos links (`text-decoration: none; color: inherit;`).

### Fase 2: Navegação Cruzada & Botões de Retorno
- [ ] **Task 7.2.1:** Atualizar a estilização do link de rodapé `.back-link` em [static/css/history.css](../static/css/history.css) para que seja exibido como um botão moderno e proeminente, mantendo o alinhamento visual do projeto.
- [ ] **Task 7.2.2:** Atualizar a página de jornal [templates/newspaper.html](../templates/newspaper.html) na seção `.newspaper-actions` para adicionar um botão secundário para "Ver Histórico".
- [ ] **Task 7.2.3:** Ajustar a folha de estilo [static/css/newspaper.css](../static/css/newspaper.css) para estilizar o novo botão secundário "Ver Histórico" de forma harmônica com o design clássico do jornal.

### Fase 3: Tratamento de Erro do Gemini (Experiência de Cota Esgotada)
- [ ] **Task 7.3.1:** Modificar o tratamento de exceções no endpoint `/api/conference/start` em [routes/api.py](../routes/api.py) para retornar uma mensagem amigável em português quando a API do Gemini falhar por limite de cota ou outros problemas.
- [ ] **Task 7.3.2:** Modificar o tratamento de exceções no endpoint `/api/conference/answer` (tanto no avanço de rodada quanto no fechamento da crônica) em [routes/api.py](../routes/api.py) para retornar mensagens amigáveis em português ao usuário quando a IA falhar.
- [ ] **Task 7.3.3:** Refatorar a exibição de alertas de erro em [templates/setup.html](../templates/setup.html) para apresentar as mensagens amigáveis de forma legível e sem alertas em inglês técnicos do sistema.

### Fase 4: Validação & Garantia de Qualidade
- [ ] **Task 7.4.1:** Executar a suíte de testes do projeto via `pytest` para garantir a integridade das rotas e das regras de negócio após as refatorações.
- [ ] **Task 7.4.2:** Atualizar os testes em [tests/test_api.py](../tests/test_api.py) para validar que os endpoints retornam as mensagens amigáveis de erro esperadas.
