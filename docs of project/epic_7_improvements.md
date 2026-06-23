# Epic 7: Refinements & User Experience (UX) Optimizations
Polishing navigation, direct history access, and robust error handling.

This document breaks down the tasks of Epic 7 into atomized steps to track implementation progress, commits, and Pull Requests.

---

## Technical Tasks

### Fase 1: Redirecionamento Direto do Histórico (Remoção do Modal)
- [x] **Task 7.1.1:** Atualizar a marcação em [templates/history.html](../templates/history.html) para converter os cartões `.history-card` em links `<a>` apontando para `/conference/<id>/newspaper`, removendo o esqueleto do modal `#retro-modal`.
- [x] **Task 7.1.2:** Limpar o bloco de scripts `{% block extra_js %}` em [templates/history.html](../templates/history.html) removendo os ouvintes de evento de clique, fetches e controle de modal que se tornaram obsoletos.
- [x] **Task 7.1.3:** Limpar a folha de estilo [static/css/history.css](../static/css/history.css) removendo as regras de estilos destinadas ao modal (`.modal-overlay`, `.modal-content`, `.chat-transcript`, etc.).
- [x] **Task 7.1.4:** Garantir que o link `.history-card` herde as cores padrões e não exiba decorações de sublinhado padrão dos links (`text-decoration: none; color: inherit;`).

### Fase 2: Navegação Cruzada & Botões de Retorno
- [x] **Task 7.2.1:** Atualizar a estilização do link de rodapé `.back-link` em [static/css/history.css](../static/css/history.css) para que seja exibido como um botão moderno e proeminente, mantendo o alinhamento visual do projeto.
- [x] **Task 7.2.2:** Atualizar a página de jornal [templates/newspaper.html](../templates/newspaper.html) na seção `.newspaper-actions` para adicionar um botão secundário para "Ver Histórico".
- [x] **Task 7.2.3:** Ajustar a folha de estilo [static/css/newspaper.css](../static/css/newspaper.css) para estilizar o novo botão secundário "Ver Histórico" de forma harmônica com o design clássico do jornal.

### Fase 3: Tratamento de Erro do Gemini & Modo Simulado (Robustez e Resiliência)
- [x] **Task 7.3.1:** Modificar o tratamento de exceções no endpoint `/api/conference/start` em [routes/api.py](../routes/api.py) para retornar uma mensagem amigável em inglês quando a API do Gemini falhar por limite de cota ou outros problemas.
- [x] **Task 7.3.2:** Modificar o tratamento de exceções no endpoint `/api/conference/answer` (tanto no avanço de rodada quanto no fechamento da crônica) em [routes/api.py](../routes/api.py) para retornar mensagens amigáveis em inglês ao usuário quando a IA falhar.
- [x] **Task 7.3.3:** Refatorar a exibição de alertas de erro em [templates/setup.html](../templates/setup.html) para apresentar as mensagens amigáveis de forma legível e sem alertas de diálogo nativos do navegador.
- [x] **Task 7.3.4:** Implementar a leitura dinâmica do modelo através de `GEMINI_MODEL` (lido do `.env` com fallback) em [services/gemini.py](../services/gemini.py) e documentá-la no arquivo `.env.example`.
- [x] **Task 7.3.5:** Criar o "Modo Simulado" (Mock Mode) em [services/gemini.py](../services/gemini.py) controlado por `MOCK_GEMINI=true` no `.env` para retornar perguntas e crônicas pré-definidas e realistas instantaneamente, eliminando riscos de queda ou cotas estouradas durante a gravação.
- [x] **Task 7.3.6:** Escrever testes unitários em [tests/test_gemini.py](../tests/test_gemini.py) cobrindo tanto o comportamento da aplicação no Modo Simulado quanto no modo de chamada real à API.
- [ ] **Task 7.3.7:** Restringir o campo de drag-and-drop no frontend (setup.html) para aceitar apenas um arquivo por vez, apresentando mensagem de erro amigável via #error-alert.

### Fase 4: Validação & Garantia de Qualidade
- [x] **Task 7.4.1:** Executar a suíte de testes do projeto via `pytest` para garantir a integridade das rotas e das regras de negócio após as refatorações.
- [x] **Task 7.4.2:** Atualizar os testes em [tests/test_api.py](../tests/test_api.py) para validar que os endpoints retornam as mensagens amigáveis de erro esperadas.

### Fase 5: Verificação de Validade da Imagem (Guardrails contra Imagens Inválidas)
- [ ] **Task 7.5.1:** Modificar o prompt do Gemini em `generate_first_question` em [services/gemini.py](../services/gemini.py) para validar se a imagem enviada é um print de jogo/estatísticas de futebol (como EA FC). Caso contrário, retornar a resposta de erro `"ERROR: INVALID_IMAGE"`.
- [ ] **Task 7.5.2:** Atualizar a lógica do endpoint `/api/conference/start` em [routes/api.py](../routes/api.py) para identificar a resposta `"ERROR: INVALID_IMAGE"` e retornar um erro `400 Bad Request` com uma mensagem amigável, deletando a imagem do disco.
- [ ] **Task 7.5.3:** Adicionar um teste unitário em [tests/test_api.py](../tests/test_api.py) para validar que o envio de imagens inválidas simula o comportamento de erro e retorna `400` corretamente com a limpeza da imagem.
