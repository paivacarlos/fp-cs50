import os
import pytest

# Configura o banco de dados de teste ANTES de importar o app e os serviços
os.environ["DATABASE_PATH"] = "test_conference_data.db"

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
    if os.path.exists("test_conference_data.db"):
        os.remove("test_conference_data.db")

def test_register_page_loads(client):
    # Faz uma requisição GET para /register
    response = client.get("/register")
    
    # Asserts
    assert response.status_code == 200
    assert b"Register" in response.data
    assert b'name="username"' in response.data
    assert b'name="password"' in response.data

def test_register_user_success(client):
    # Simula o envio do formulário de cadastro (POST)
    response = client.post("/register", data={
        "username": "junior_dev_cs50",
        "password": "safety_password_123",
        "confirm_password": "safety_password_123"
    })
    
    # 1. Deve redirecionar (status 302) para a tela de setup
    assert response.status_code == 302
    assert response.headers["Location"] == "/setup"
    
    # 2. O usuário deve ter sido logado automaticamente (user_id na sessão)
    with client.session_transaction() as sess:
        assert "user_id" in sess
        assert sess["username"] == "junior_dev_cs50"

def test_register_password_mismatch(client):
    response = client.post("/register", data={
        "username": "dev_mismatch",
        "password": "safety_password_123",
        "confirm_password": "different_password_123"
    })
    
    # 1. Deve recarregar a página com status 200 e erro correspondente
    assert response.status_code == 200
    assert b"Passwords do not match." in response.data
    
    # 2. Não deve ter salvo no banco de dados
    user = query_db("SELECT * FROM users WHERE username = ?", ("dev_mismatch",), one=True)
    assert user is None
    
    # 3. Não deve ter logado na sessão
    with client.session_transaction() as sess:
        assert "user_id" not in sess

def test_register_duplicate_username(client):
    # 1. Primeiro cadastro com sucesso
    response1 = client.post("/register", data={
        "username": "duplicate_user",
        "password": "safety_password_123",
        "confirm_password": "safety_password_123"
    })
    assert response1.status_code == 302
    
    # 2. Segundo cadastro com o mesmo username
    response2 = client.post("/register", data={
        "username": "duplicate_user",
        "password": "another_password_123",
        "confirm_password": "another_password_123"
    })
    
    # Deve retornar 200 e erro de usuário duplicado
    assert response2.status_code == 200
    assert b"User already exists." in response2.data

