import os
import importlib

# ⚠️ IMPORTANTE: A variável de ambiente DEVE ser definida ANTES de importar o módulo 'services.gemini'.
# Caso contrário, a validação no escopo global do módulo levantará um ValueError de imediato.
os.environ["GEMINI_API_KEY"] = "fake-test-key-123456"

import pytest
from unittest.mock import MagicMock, patch, mock_open
from services.gemini import get_image_data, generate_first_question, generate_next_question


def test_get_image_data_success():
    """Testa se get_image_data lê a imagem e retorna os bytes e o mime_type correto."""
    fake_image_bytes = b"fake_png_data"
    
    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=fake_image_bytes)):
        
        result = get_image_data("path/to/image.png")
        
        assert result["mime_type"] == "image/png"
        assert result["data"] == fake_image_bytes


def test_get_image_data_jpg_mime():
    """Testa se a extensão .jpg é convertida para image/jpeg."""
    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=b"jpg_data")):
        
        result = get_image_data("path/to/image.jpg")
        assert result["mime_type"] == "image/jpeg"


def test_get_image_data_file_not_found():
    """Testa se lança FileNotFoundError se a imagem não existir."""
    with patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            get_image_data("non_existent.png")


@patch("services.gemini.model")
@patch("services.gemini.get_image_data")
def test_generate_first_question(mock_get_image, mock_model):
    """Testa se generate_first_question chama a API do Gemini com os parâmetros corretos."""
    mock_get_image.return_value = {"mime_type": "image/png", "data": b"bytes"}
    
    # Mock da resposta da API do Gemini
    mock_response = MagicMock()
    mock_response.text = "  What was your biggest challenge in the match?  "
    mock_model.generate_content.return_value = mock_response
    
    question = generate_first_question("fake_image.png", "We won the game in a tough battle")
    
    # O resultado deve ter o strip() aplicado (removendo os espaços adicionados no mock)
    assert question == "What was your biggest challenge in the match?"
    
    # Verifica se o método generate_content foi chamado
    mock_model.generate_content.assert_called_once()
    
    # Captura os argumentos passados para a geração de conteúdo
    called_args = mock_model.generate_content.call_args[0][0]
    assert called_args[0] == {"mime_type": "image/png", "data": b"bytes"}
    assert "We won the game in a tough battle" in called_args[1]


@patch("services.gemini.model")
@patch("services.gemini.get_image_data")
def test_generate_next_question(mock_get_image, mock_model):
    """Testa se generate_next_question envia o histórico de conversa corretamente no prompt."""
    mock_get_image.return_value = {"mime_type": "image/png", "data": b"bytes"}
    
    mock_response = MagicMock()
    mock_response.text = "Why did you substitute the striker?"
    mock_model.generate_content.return_value = mock_response
    
    history = [
        {"question": "How do you feel?", "answer": "Happy."},
        {"question": "And the fans?", "answer": "They supported us a lot."}
    ]
    
    question = generate_next_question("fake_image.png", "Coach's notes", history)
    
    assert question == "Why did you substitute the striker?"
    mock_model.generate_content.assert_called_once()
    
    # Captura e valida se o histórico de diálogo foi inserido no prompt
    called_args = mock_model.generate_content.call_args[0][0]
    prompt_sent = called_args[1]
    assert "Reporter: How do you feel?\nCoach: Happy." in prompt_sent
    assert "Reporter: And the fans?\nCoach: They supported us a lot." in prompt_sent


def test_missing_api_key_raises_error():
    """Testa se a ausência de GEMINI_API_KEY de fato gera ValueError ao carregar o módulo."""
    # Removemos a chave do ambiente de testes temporariamente
    with patch.dict(os.environ, {}, clear=True):
        import services.gemini
        # Como o módulo já foi importado no início do arquivo, precisamos forçar um recarregamento
        # para que o código de validação global dele execute novamente sob o ambiente sem a variável.
        with pytest.raises(ValueError, match="GEMINI_API_KEY is missing"):
            importlib.reload(services.gemini)
