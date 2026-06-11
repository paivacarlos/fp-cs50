import os
import io
import pytest
from unittest.mock import patch, MagicMock

# Configura o banco de dados de teste ANTES de importar o app e os serviços
os.environ["DATABASE_PATH"] = "test_api_conference_data.db"
# Define a chave mockada do Gemini para o import não quebrar
os.environ["GEMINI_API_KEY"] = "fake-api-key-for-endpoint-tests"

from app import app
from services.db import init_db, query_db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    
    # Inicializa o banco de testes criando as tabelas limpas
    init_db()
    
    with app.test_client() as client:
        yield client
        
    # Limpeza: Deleta o banco de testes após a execução dos testes
    if os.path.exists("test_api_conference_data.db"):
        try:
            os.remove("test_api_conference_data.db")
        except Exception:
            pass

@pytest.fixture
def authed_client(client):
    import uuid
    username = f"user_{uuid.uuid4().hex[:8]}"
    # Registra e loga o usuário automaticamente
    client.post("/register", data={
        "username": username,
        "password": "securepassword123",
        "confirm_password": "securepassword123"
    })
    return client

def test_start_conference_requires_login(client):
    # Tenta iniciar sem estar logado
    response = client.post("/api/conference/start")
    assert response.status_code == 302 # login_required redireciona para /login

@patch("routes.api.generate_first_question")
@patch("routes.api.save_upload_file")
def test_start_conference_success(mock_save_file, mock_gemini, authed_client):
    mock_save_file.return_value = "/static/uploads/mocked_filename.png"
    mock_gemini.return_value = "What is your opinion on the game?"
    
    # Prepara o arquivo simulado (multipart/form-data)
    data = {
        "screenshot": (io.BytesIO(b"fake_image_bytes"), "match.png"),
        "initial_context": "We played well and dominated the possession."
    }
    
    response = authed_client.post(
        "/api/conference/start",
        data=data,
        content_type="multipart/form-data"
    )
    
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["conference_id"] is not None
    assert json_data["round_number"] == 1
    assert json_data["question"] == "What is your opinion on the game?"
    
    # Verifica se os dados foram persistidos no banco
    conf_id = json_data["conference_id"]
    conf = query_db("SELECT * FROM conferences WHERE id = ?", (conf_id,), one=True)
    assert conf is not None
    assert conf["initial_context"] == "We played well and dominated the possession."
    assert "uploads" in conf["screenshot_path"]
    
    rnd = query_db("SELECT * FROM rounds WHERE conference_id = ? AND round_number = 1", (conf_id,), one=True)
    assert rnd is not None
    assert rnd["question"] == "What is your opinion on the game?"
    assert rnd["answer"] is None

def test_start_conference_missing_screenshot(authed_client):
    data = {
        "initial_context": "We played well."
    }
    response = authed_client.post(
        "/api/conference/start",
        data=data,
        content_type="multipart/form-data"
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "No screenshot file uploaded"

def test_start_conference_invalid_extension(authed_client):
    data = {
        "screenshot": (io.BytesIO(b"fake_text"), "match.txt"),
        "initial_context": "We played well."
    }
    response = authed_client.post(
        "/api/conference/start",
        data=data,
        content_type="multipart/form-data"
    )
    assert response.status_code == 400
    assert "File type not allowed" in response.get_json()["error"]

def test_start_conference_missing_context(authed_client):
    data = {
        "screenshot": (io.BytesIO(b"fake_image"), "match.png"),
        "initial_context": ""
    }
    response = authed_client.post(
        "/api/conference/start",
        data=data,
        content_type="multipart/form-data"
    )
    assert response.status_code == 400
    assert "initial_context is required" in response.get_json()["error"]

def test_start_conference_context_too_long(authed_client):
    data = {
        "screenshot": (io.BytesIO(b"fake_image"), "match.png"),
        "initial_context": "a" * 201
    }
    response = authed_client.post(
        "/api/conference/start",
        data=data,
        content_type="multipart/form-data"
    )
    assert response.status_code == 400
    assert "initial_context must be between 1 and 200 characters" in response.get_json()["error"]

@patch("routes.api.generate_first_question")
@patch("routes.api.save_upload_file")
def test_start_conference_gemini_failure_cleans_file(mock_save_file, mock_gemini, authed_client):
    mock_save_file.return_value = "/static/uploads/mocked_filename.png"
    mock_gemini.side_effect = Exception("Gemini service offline")
    
    # Vamos mockar o os.path.exists e os.remove para verificar se houve a remoção do arquivo
    with patch("os.path.exists", return_value=True) as mock_exists, \
         patch("os.remove") as mock_remove:
        
        data = {
            "screenshot": (io.BytesIO(b"fake_image"), "match.png"),
            "initial_context": "Tough game"
        }
        
        response = authed_client.post(
            "/api/conference/start",
            data=data,
            content_type="multipart/form-data"
        )
        
        assert response.status_code == 500
        assert "Gemini service offline" in response.get_json()["error"]
        
        # Garante que tentou apagar o arquivo
        mock_exists.assert_called()
        mock_remove.assert_called_once()
