import os
import pytest
# pyrefly: ignore [missing-import]
from playwright.sync_api import expect

def test_setup_page_ui(live_server, page):
    # 1. Registrar um usuário para conseguir acessar o /setup diretamente
    page.goto(f"{live_server}/register")
    page.fill('input[name="username"]', "ui_tester_coach")
    page.fill('input[name="password"]', "securepassword123")
    page.fill('input[name="confirm_password"]', "securepassword123")
    page.click('button[type="submit"]')
    
    # Após o cadastro com sucesso, deve redirecionar para a tela de /setup
    expect(page).to_have_url(f"{live_server}/setup")
    
    # 2. Verificar se os elementos essenciais da UI de Setup estão visíveis na tela
    expect(page.locator("#drop-zone")).to_be_visible()
    expect(page.locator("#initial_context")).to_be_visible()
    expect(page.locator("#char-counter")).to_contain_text("200 characters remaining")
    
    # 3. Testar o comportamento do contador de caracteres em tempo real
    # Preenche 100 caracteres e valida se o contador mostra 100 restantes
    page.fill("#initial_context", "A" * 100)
    expect(page.locator("#char-counter")).to_contain_text("100 characters remaining")
    
    # Preenche 250 caracteres (acima do limite)
    page.fill("#initial_context", "B" * 250)
    
    # Verifica se o navegador fisicamente limitou a caixa de texto a 200 caracteres (devido ao maxlength)
    val = page.locator("#initial_context").input_value()
    assert len(val) == 200
    expect(page.locator("#char-counter")).to_contain_text("0 characters remaining")
    
    # 4. Testar o upload e a exibição da pré-visualização (Preview)
    # Cria uma imagem temporária válida de teste
    test_image_path = "tests/test_temp_screenshot.png"
    with open(test_image_path, "wb") as f:
        # Escreve um arquivo de imagem dummy para simular o upload
        f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82")
        
    try:
        # Seleciona o arquivo no input oculto de screenshot
        page.set_input_files("#screenshot", test_image_path)
        
        # Verifica se a pré-visualização de imagem aparece na tela
        expect(page.locator("#preview-container")).to_be_visible()
        expect(page.locator("#preview-image")).to_be_visible()
        
    finally:
        # Garante a remoção da imagem temporária criada para o teste
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

def test_setup_page_invalid_upload_alert(live_server, page):
    # Logar com o usuário já cadastrado
    page.goto(f"{live_server}/login")
    page.fill('input[name="username"]', "ui_tester_coach")
    page.fill('input[name="password"]', "securepassword123")
    page.click('button[type="submit"]')
    expect(page).to_have_url(f"{live_server}/setup")
    
    # Captura e aceita o alerta que o JS deve disparar na tela
    dialog_messages = []
    page.on("dialog", lambda dialog: [dialog_messages.append(dialog.message), dialog.accept()])
    
    # Cria um arquivo de texto simulando um tipo de arquivo inválido
    invalid_file_path = "tests/test_temp_invalid.txt"
    with open(invalid_file_path, "w") as f:
        f.write("dados de texto inválidos para screenshot")
        
    try:
        # Tenta enviar o arquivo inválido
        page.set_input_files("#screenshot", invalid_file_path)
        
        # Verifica se o alerta foi exibido com a mensagem correta
        assert len(dialog_messages) > 0
        assert "Please upload a valid image file" in dialog_messages[0]
        
        # Garante que a pré-visualização continua oculta
        expect(page.locator("#preview-container")).not_to_be_visible()
        
    finally:
        # Remove o arquivo temporário
        if os.path.exists(invalid_file_path):
            os.remove(invalid_file_path)
