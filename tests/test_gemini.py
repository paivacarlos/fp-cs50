import os
import importlib

# ⚠️ IMPORTANTE: A variável de ambiente DEVE ser definida ANTES de importar o módulo 'services.gemini'.
# Caso contrário, a validação no escopo global do módulo levantará um ValueError de imediato.
os.environ["GEMINI_API_KEY"] = "fake-test-key-123456"

import pytest
from unittest.mock import MagicMock, patch, mock_open
from google.genai import types # type: ignore
from services.gemini import get_image_part, generate_first_question, generate_next_question, generate_chronicle, ChronicleResponse


def test_get_image_part_success():
    """Testa se get_image_part lê a imagem e retorna o types.Part binário correto."""
    fake_image_bytes = b"fake_png_data"
    
    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=fake_image_bytes)):
        
        result = get_image_part("path/to/image.png")
        
        assert isinstance(result, types.Part)
        assert result.inline_data.data == fake_image_bytes
        assert result.inline_data.mime_type == "image/png"


def test_get_image_part_jpg_mime():
    """Testa se a extensão .jpg é convertida para image/jpeg."""
    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=b"jpg_data")):
        
        result = get_image_part("path/to/image.jpg")
        assert result.inline_data.mime_type == "image/jpeg"


def test_get_image_part_file_not_found():
    """Testa se lança FileNotFoundError se a imagem não existir."""
    with patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            get_image_part("non_existent.png")


@patch("services.gemini.client")
@patch("services.gemini.get_image_part")
def test_generate_first_question(mock_get_image, mock_client):
    """Testa se generate_first_question chama a API do Gemini com os parâmetros corretos."""
    fake_part = types.Part.from_bytes(data=b"bytes", mime_type="image/png")
    mock_get_image.return_value = fake_part
    
    # Mock da resposta da API do Gemini
    mock_response = MagicMock()
    mock_response.text = "  What was your biggest challenge in the match?  "
    mock_client.models.generate_content.return_value = mock_response
    
    question = generate_first_question("fake_image.png", "We won the game in a tough battle")
    
    # O resultado deve ter o strip() aplicado (removendo os espaços adicionados no mock)
    assert question == "What was your biggest challenge in the match?"
    
    # Verifica se o método generate_content foi chamado em client.models
    mock_client.models.generate_content.assert_called_once()
    
    # Captura os argumentos passados para a geração de conteúdo
    called_kwargs = mock_client.models.generate_content.call_args[1]
    assert called_kwargs["model"] == "gemini-2.5-flash"
    contents = called_kwargs["contents"]
    assert contents[0] == fake_part
    assert "We won the game in a tough battle" in contents[1]


@patch("services.gemini.client")
@patch("services.gemini.get_image_part")
def test_generate_next_question(mock_get_image, mock_client):
    """Testa se generate_next_question envia o histórico de conversa corretamente no prompt."""
    fake_part = types.Part.from_bytes(data=b"bytes", mime_type="image/png")
    mock_get_image.return_value = fake_part
    
    mock_response = MagicMock()
    mock_response.text = "Why did you substitute the striker?"
    mock_client.models.generate_content.return_value = mock_response
    
    history = [
        {"question": "How do you feel?", "answer": "Happy."},
        {"question": "And the fans?", "answer": "They supported us a lot."}
    ]
    
    question = generate_next_question("fake_image.png", "Coach's notes", history)
    
    assert question == "Why did you substitute the striker?"
    mock_client.models.generate_content.assert_called_once()
    
    # Captura e valida se o histórico de diálogo foi inserido no prompt
    called_kwargs = mock_client.models.generate_content.call_args[1]
    contents = called_kwargs["contents"]
    prompt_sent = contents[1]
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


@patch("services.gemini.client")
@patch("services.gemini.get_image_part")
def test_generate_chronicle(mock_get_image, mock_client):
    """Testa se generate_chronicle envia o prompt e as configurações corretas e retorna o JSON estruturado."""
    fake_part = types.Part.from_bytes(data=b"bytes", mime_type="image/png")
    mock_get_image.return_value = fake_part
    
    # 1. Mockamos a resposta da API do Gemini
    # O SDK retorna a resposta estruturada em formato de string JSON dentro de response.text
    mock_response = MagicMock()
    mock_response.text = '{"headline": "Tough defeat at home", "chronicle": "The team fought hard but could not win."}'
    mock_client.models.generate_content.return_value = mock_response
    
    # 2. Dados de entrada simulados
    history = [
        {"question": "How do you feel?", "answer": "Sad."},
        {"question": "What is the plan?", "answer": "Work harder."}
    ]
    
    # 3. Executamos a função
    result = generate_chronicle("fake_image.png", "A tough loss", history)
    
    # 4. Asserts (Validações)
    # A função deve ter parseado a string do mock e retornado um dicionário Python válido
    assert isinstance(result, dict)
    assert result["headline"] == "Tough defeat at home"
    assert result["chronicle"] == "The team fought hard but could not win."
    
    # Garante que a API foi chamada
    mock_client.models.generate_content.assert_called_once()
    
    # Captura os argumentos da chamada de geração para validar as configurações de resposta estruturada
    called_kwargs = mock_client.models.generate_content.call_args[1]
    assert called_kwargs["model"] == "gemini-2.5-flash"
    
    # Valida se passamos o response_mime_type e o response_schema corretos
    config = called_kwargs["config"]
    assert config.response_mime_type == "application/json"
    assert config.response_schema.__name__ == "ChronicleResponse"


def test_mock_mode_active_no_api_key_needed():
    """Testa se com MOCK_GEMINI=true o modulo e carregado sem erro mesmo sem GEMINI_API_KEY."""
    with patch.dict(os.environ, {"MOCK_GEMINI": "true"}, clear=True):
        import services.gemini
        # Não deve levantar ValueError no reload
        importlib.reload(services.gemini)


def test_generate_first_question_mock_mode():
    """Testa se generate_first_question no Modo Simulado retorna a questao mockada imediatamente."""
    with patch.dict(os.environ, {"MOCK_GEMINI": "true"}, clear=True):
        import services.gemini
        importlib.reload(services.gemini)
        
        # Chama a funcao (nao deve fazer chamadas de API, portanto nao precisa mockar o client do SDK)
        res = services.gemini.generate_first_question("some_image.png", "A generic context")
        assert "defensive transitions" in res
        assert "Coach" in res


def test_generate_next_question_mock_mode():
    """Testa se generate_next_question no Modo Simulado retorna as questoes subsequentes esperadas."""
    with patch.dict(os.environ, {"MOCK_GEMINI": "true"}, clear=True):
        import services.gemini
        importlib.reload(services.gemini)
        
        # Rodada 2 (historico de tamanho 1)
        res1 = services.gemini.generate_next_question("some_image.png", "Context", [{"question": "Q1", "answer": "A1"}])
        assert "midfield was frequently bypassed" in res1
        
        # Rodada 3 (historico de tamanho 2)
        res2 = services.gemini.generate_next_question("some_image.png", "Context", [
            {"question": "Q1", "answer": "A1"},
            {"question": "Q2", "answer": "A2"}
        ])
        assert "roster rotations" in res2


def test_generate_chronicle_mock_mode():
    """Testa se generate_chronicle no Modo Simulado retorna a cronica estruturada estatica."""
    with patch.dict(os.environ, {"MOCK_GEMINI": "true"}, clear=True):
        import services.gemini
        importlib.reload(services.gemini)
        
        res = services.gemini.generate_chronicle("some_image.png", "Context", [])
        assert isinstance(res, dict)
        assert "headline" in res
        assert "chronicle" in res
        assert "TACTICAL REVOLUTION" in res["headline"]
        assert "post-match press conference" in res["chronicle"]


# Restaura o estado original do modulo apos os testes que alteraram as variaveis globais
@pytest.fixture(autouse=True)
def cleanup_gemini_module():
    yield
    # Limpa as variaveis de ambiente de teste para nao interferirem em outros testes
    os.environ["GEMINI_API_KEY"] = "fake-test-key-123456"
    if "MOCK_GEMINI" in os.environ:
        del os.environ["MOCK_GEMINI"]
    import services.gemini
    importlib.reload(services.gemini)


