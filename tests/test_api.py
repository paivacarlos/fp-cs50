import os
import io
import pytest
from unittest.mock import patch, MagicMock

# Configura o banco de dados de teste ANTES de importar o app e os serviços
os.environ["DATABASE_PATH"] = "test_api_conference_data.db"
# Define a chave mockada do Gemini para o import não quebrar
os.environ["GEMINI_API_KEY"] = "fake-api-key-for-endpoint-tests"

from app import app
from services.db import init_db, query_db, get_db

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
    assert response.status_code == 401 # api_login_required retorna 401 JSON
    assert "error" in response.get_json()

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
        assert "The AI model is temporarily exhausted" in response.get_json()["error"]
        
        # Garante que tentou apagar o arquivo
        mock_exists.assert_called()
        mock_remove.assert_called_once()


@patch("routes.api.generate_first_question")
@patch("routes.api.save_upload_file")
def test_start_conference_invalid_image_guardrail(mock_save_file, mock_gemini, authed_client):
    mock_save_file.return_value = "/static/uploads/mocked_filename.png"
    mock_gemini.return_value = "ERROR: INVALID_IMAGE"
    
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
        
        assert response.status_code == 400
        assert "The uploaded screenshot is invalid" in response.get_json()["error"]
        
        # Garante que tentou apagar o arquivo
        mock_exists.assert_called()
        mock_remove.assert_called_once()


def test_submit_answer_requires_login(client):
    response = client.post("/api/conference/answer", json={"conference_id": 1, "answer": "Yes"})
    assert response.status_code == 401 # Retorna 401 JSON
    assert "error" in response.get_json()


@patch("routes.api.generate_next_question")
@patch("routes.api.save_upload_file")
def test_submit_answer_success_round1_to_round2(mock_save_file, mock_gemini, authed_client):
    mock_save_file.return_value = "/static/uploads/mocked.png"
    mock_gemini.return_value = "What about the second half?"
    
    # 1. Cria a conferência no banco para o usuário logado
    # Descobre o ID do usuário criado pela fixture authed_client
    with app.test_client() as c:
        # Precisamos pegar o user_id da sessão ativa do authed_client
        # Mas para simplificar, vamos buscar o último usuário cadastrado no banco de testes
        user = query_db("SELECT id FROM users ORDER BY id DESC LIMIT 1", one=True)
        user_id = user["id"]
        
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO conferences (user_id, screenshot_path, initial_context) VALUES (?, ?, ?)",
            (user_id, "/static/uploads/mocked.png", "A tough game")
        )
        conf_id = cursor.lastrowid
        conn.execute(
            "INSERT INTO rounds (conference_id, round_number, question) VALUES (?, 1, ?)",
            (conf_id, "How do you feel?")
        )
        conn.commit()
        
    # 2. Envia a resposta da Rodada 1
    response = authed_client.post(
        "/api/conference/answer",
        json={"conference_id": conf_id, "answer": "I feel great."}
    )
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["round_number"] == 2
    assert json_data["question"] == "What about the second half?"
    
    # 3. Verifica se as alterações foram salvas no banco
    rnd1 = query_db("SELECT * FROM rounds WHERE conference_id = ? AND round_number = 1", (conf_id,), one=True)
    assert rnd1["answer"] == "I feel great."
    
    rnd2 = query_db("SELECT * FROM rounds WHERE conference_id = ? AND round_number = 2", (conf_id,), one=True)
    assert rnd2 is not None
    assert rnd2["question"] == "What about the second half?"
    assert rnd2["answer"] is None


@patch("routes.api.generate_chronicle")
def test_submit_answer_success_round3_completion(mock_chronicle, authed_client):
    mock_chronicle.return_value = {
        "headline": "Historic Victory!",
        "chronicle": "What a match! The coach was brilliant..."
    }
    
    user = query_db("SELECT id FROM users ORDER BY id DESC LIMIT 1", one=True)
    user_id = user["id"]
    
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO conferences (user_id, screenshot_path, initial_context) VALUES (?, ?, ?)",
            (user_id, "/static/uploads/mocked.png", "A tough game")
        )
        conf_id = cursor.lastrowid
        conn.execute(
            "INSERT INTO rounds (conference_id, round_number, question, answer) VALUES (?, 1, ?, ?)",
            (conf_id, "Q1", "A1")
        )
        conn.execute(
            "INSERT INTO rounds (conference_id, round_number, question, answer) VALUES (?, 2, ?, ?)",
            (conf_id, "Q2", "A2")
        )
        conn.execute(
            "INSERT INTO rounds (conference_id, round_number, question) VALUES (?, 3, ?)",
            (conf_id, "Q3")
        )
        conn.commit()
        
    response = authed_client.post(
        "/api/conference/answer",
        json={"conference_id": conf_id, "answer": "A3"}
    )
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "complete"
    assert json_data["headline"] == "Historic Victory!"
    assert json_data["chronicle"] == "What a match! The coach was brilliant..."
    
    rnd3 = query_db("SELECT * FROM rounds WHERE conference_id = ? AND round_number = 3", (conf_id,), one=True)
    assert rnd3["answer"] == "A3"
    
    # Nenhuma rodada 4 deve ter sido criada
    rnd4 = query_db("SELECT * FROM rounds WHERE conference_id = ? AND round_number = 4", (conf_id,), one=True)
    assert rnd4 is None

    # Verifica se os dados foram persistidos na tabela conferences
    conf = query_db("SELECT * FROM conferences WHERE id = ?", (conf_id,), one=True)
    assert conf["headline"] == "Historic Victory!"
    assert conf["chronicle"] == "What a match! The coach was brilliant..."


@patch("routes.api.generate_chronicle")
def test_submit_answer_chronicle_failure_rollbacks_db(mock_chronicle, authed_client):
    mock_chronicle.side_effect = Exception("Gemini API Timeout on Chronicle")
    
    user = query_db("SELECT id FROM users ORDER BY id DESC LIMIT 1", one=True)
    user_id = user["id"]
    
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO conferences (user_id, screenshot_path, initial_context) VALUES (?, ?, ?)",
            (user_id, "/static/uploads/mocked.png", "A tough game")
        )
        conf_id = cursor.lastrowid
        conn.execute(
            "INSERT INTO rounds (conference_id, round_number, question, answer) VALUES (?, 1, ?, ?)",
            (conf_id, "Q1", "A1")
        )
        conn.execute(
            "INSERT INTO rounds (conference_id, round_number, question, answer) VALUES (?, 2, ?, ?)",
            (conf_id, "Q2", "A2")
        )
        conn.execute(
            "INSERT INTO rounds (conference_id, round_number, question) VALUES (?, 3, ?)",
            (conf_id, "Q3")
        )
        conn.commit()
        
    response = authed_client.post(
        "/api/conference/answer",
        json={"conference_id": conf_id, "answer": "A3"}
    )
    
    assert response.status_code == 500
    assert "The AI model is temporarily exhausted" in response.get_json()["error"]
    
    # Valida que o answer da rodada 3 voltou a ser NULL (ou seja, houve o rollback)
    rnd3 = query_db("SELECT * FROM rounds WHERE conference_id = ? AND round_number = 3", (conf_id,), one=True)
    assert rnd3["answer"] is None
    
    # Valida que a conferência não foi atualizada com crônica ou manchete
    conf = query_db("SELECT * FROM conferences WHERE id = ?", (conf_id,), one=True)
    assert conf["headline"] is None
    assert conf["chronicle"] is None


def test_submit_answer_double_answer_error(authed_client):
    user = query_db("SELECT id FROM users ORDER BY id DESC LIMIT 1", one=True)
    user_id = user["id"]
    
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO conferences (user_id, screenshot_path, initial_context) VALUES (?, ?, ?)",
            (user_id, "/static/uploads/mocked.png", "A tough game")
        )
        conf_id = cursor.lastrowid
        conn.execute(
            "INSERT INTO rounds (conference_id, round_number, question, answer) VALUES (?, 1, ?, ?)",
            (conf_id, "Q1", "Already Answered")
        )
        conn.commit()
        
    response = authed_client.post(
        "/api/conference/answer",
        json={"conference_id": conf_id, "answer": "New Answer"}
    )
    
    assert response.status_code == 400
    assert response.get_json()["error"] == "Round already answered"


def test_submit_answer_unauthorized_conference(authed_client):
    # Cria outro usuário no banco para associar à conferência alheia
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            ("another_coach", "some_hash")
        )
        other_user_id = cursor.lastrowid
        
        cursor = conn.execute(
            "INSERT INTO conferences (user_id, screenshot_path, initial_context) VALUES (?, ?, ?)",
            (other_user_id, "/static/uploads/mocked.png", "A tough game")
        )
        conf_id = cursor.lastrowid
        conn.execute(
            "INSERT INTO rounds (conference_id, round_number, question) VALUES (?, 1, ?)",
            (conf_id, "Q1")
        )
        conn.commit()
        
    response = authed_client.post(
        "/api/conference/answer",
        json={"conference_id": conf_id, "answer": "My Answer"}
    )
    
    assert response.status_code == 404
    assert "not found or unauthorized" in response.get_json()["error"]


def test_submit_answer_validation_missing_fields(authed_client):
    response1 = authed_client.post(
        "/api/conference/answer",
        json={"answer": "My Answer"}
    )
    assert response1.status_code == 400
    assert "conference_id is required" in response1.get_json()["error"]
    
    response2 = authed_client.post(
        "/api/conference/answer",
        json={"conference_id": 1, "answer": ""}
    )
    assert response2.status_code == 400
    assert "answer is required" in response2.get_json()["error"]


@patch("routes.api.generate_next_question")
def test_submit_answer_gemini_failure_rollbacks_db(mock_gemini, authed_client):
    mock_gemini.side_effect = Exception("Gemini API Timeout")
    
    user = query_db("SELECT id FROM users ORDER BY id DESC LIMIT 1", one=True)
    user_id = user["id"]
    
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO conferences (user_id, screenshot_path, initial_context) VALUES (?, ?, ?)",
            (user_id, "/static/uploads/mocked.png", "A tough game")
        )
        conf_id = cursor.lastrowid
        conn.execute(
            "INSERT INTO rounds (conference_id, round_number, question) VALUES (?, 1, ?)",
            (conf_id, "Q1")
        )
        conn.commit()
        
    response = authed_client.post(
        "/api/conference/answer",
        json={"conference_id": conf_id, "answer": "Answer that should be rolled back"}
    )
    
    assert response.status_code == 500
    assert "The AI model is temporarily exhausted" in response.get_json()["error"]
    
    # Valida que o answer da rodada 1 voltou a ser NULL (ou seja, houve o rollback)
    rnd1 = query_db("SELECT * FROM rounds WHERE conference_id = ? AND round_number = 1", (conf_id,), one=True)
    assert rnd1["answer"] is None


def test_newspaper_route_requires_login(client):
    response = client.get("/conference/1/newspaper")
    assert response.status_code == 302 # login_required redirects to /login


def test_newspaper_route_success(authed_client):
    user = query_db("SELECT id FROM users ORDER BY id DESC LIMIT 1", one=True)
    user_id = user["id"]
    
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO conferences (user_id, screenshot_path, initial_context, headline, chronicle) VALUES (?, ?, ?, ?, ?)",
            (user_id, "/static/uploads/mocked.png", "A tough game", "Historic Victory!", "What a match!")
        )
        conf_id = cursor.lastrowid
        conn.commit()
        
    response = authed_client.get(f"/conference/{conf_id}/newspaper")
    assert response.status_code == 200
    assert b"Historic Victory!" in response.data
    assert b"What a match!" in response.data


def test_newspaper_route_unauthorized(authed_client):
    # Create another user and their conference
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            ("another_coach_newspaper", "some_hash")
        )
        other_user_id = cursor.lastrowid
        
        cursor = conn.execute(
            "INSERT INTO conferences (user_id, screenshot_path, initial_context, headline, chronicle) VALUES (?, ?, ?, ?, ?)",
            (other_user_id, "/static/uploads/mocked.png", "A tough game", "Another Victory!", "Another match!")
        )
        other_conf_id = cursor.lastrowid
        conn.commit()
        
    # Logged-in user tries to access other user's newspaper
    response = authed_client.get(f"/conference/{other_conf_id}/newspaper")
    assert response.status_code == 404


def test_newspaper_route_not_found(authed_client):
    # Non-existent conference
    response = authed_client.get("/conference/999999/newspaper")
    assert response.status_code == 404


def test_history_route_requires_login(client):
    response = client.get("/history")
    assert response.status_code == 302


def test_history_route_success(authed_client):
    response = authed_client.get("/history")
    assert response.status_code == 200


def test_get_conference_details_requires_login(client):
    response = client.get("/api/conference/1/details")
    assert response.status_code == 401
    assert "error" in response.get_json()


def test_get_conference_details_success(authed_client):
    user = query_db("SELECT id FROM users ORDER BY id DESC LIMIT 1", one=True)
    user_id = user["id"]
    
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO conferences (user_id, screenshot_path, initial_context, headline, chronicle) VALUES (?, ?, ?, ?, ?)",
            (user_id, "/static/uploads/mocked.png", "A tough game", "Historic Victory!", "What a match!")
        )
        conf_id = cursor.lastrowid
        conn.execute(
            "INSERT INTO rounds (conference_id, round_number, question, answer) VALUES (?, 1, ?, ?)",
            (conf_id, "Q1", "A1")
        )
        conn.execute(
            "INSERT INTO rounds (conference_id, round_number, question, answer) VALUES (?, 2, ?, ?)",
            (conf_id, "Q2", "A2")
        )
        conn.commit()
        
    response = authed_client.get(f"/api/conference/{conf_id}/details")
    assert response.status_code == 200
    json_data = response.get_json()
    assert "conference" in json_data
    assert "rounds" in json_data
    assert json_data["conference"]["id"] == conf_id
    assert json_data["conference"]["headline"] == "Historic Victory!"
    assert len(json_data["rounds"]) == 2
    assert json_data["rounds"][0]["question"] == "Q1"
    assert json_data["rounds"][0]["answer"] == "A1"
    assert json_data["rounds"][1]["question"] == "Q2"
    assert json_data["rounds"][1]["answer"] == "A2"


def test_get_conference_details_not_found(authed_client):
    response = authed_client.get("/api/conference/999999/details")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Conference not found"


def test_get_conference_details_unauthorized(authed_client):
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            ("another_coach_details", "some_hash")
        )
        other_user_id = cursor.lastrowid
        
        cursor = conn.execute(
            "INSERT INTO conferences (user_id, screenshot_path, initial_context) VALUES (?, ?, ?)",
            (other_user_id, "/static/uploads/mocked.png", "A tough game")
        )
        other_conf_id = cursor.lastrowid
        conn.commit()
        
    response = authed_client.get(f"/api/conference/{other_conf_id}/details")
    assert response.status_code == 403
    assert response.get_json()["error"] == "Unauthorized access to this conference"



