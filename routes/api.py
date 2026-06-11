import os
from flask import Blueprint, request, jsonify, session
from utils.security import login_required
from utils.upload import save_upload_file
from services.db import get_db
from services.gemini import generate_first_question, generate_next_question

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/conference/start", methods=["POST"])
@login_required
def start_conference():
    # 1. Validar se o arquivo de screenshot está presente
    if "screenshot" not in request.files:
        return jsonify({"error": "No screenshot file uploaded"}), 400
        
    file = request.files["screenshot"]
    if file.filename == "":
        return jsonify({"error": "No screenshot file selected"}), 400

    # 2. Validar o initial_context
    initial_context = request.form.get("initial_context")
    if not initial_context:
        return jsonify({"error": "initial_context is required"}), 400
        
    initial_context = initial_context.strip()
    if len(initial_context) < 1 or len(initial_context) > 200:
        return jsonify({"error": "initial_context must be between 1 and 200 characters"}), 400

    # 3. Salvar o arquivo usando save_upload_file
    upload_folder = "static/uploads"
    try:
        screenshot_path = save_upload_file(file, upload_folder)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    local_path = screenshot_path.lstrip("/")

    # 4. Invocar a API do Gemini
    try:
        question = generate_first_question(local_path, initial_context)
    except Exception as e:
        # Cleanup do arquivo físico em caso de erro da IA para evitar arquivos órfãos
        if os.path.exists(local_path):
            try:
                os.remove(local_path)
            except Exception:
                pass
        return jsonify({"error": f"Failed to generate first question: {str(e)}"}), 500

    # 5. Persistir no banco de dados (conferences e rounds) em uma única transação
    user_id = session["user_id"]
    try:
        with get_db() as conn:
            cursor = conn.execute(
                "INSERT INTO conferences (user_id, screenshot_path, initial_context) VALUES (?, ?, ?)",
                (user_id, screenshot_path, initial_context)
            )
            conference_id = cursor.lastrowid
            
            conn.execute(
                "INSERT INTO rounds (conference_id, round_number, question) VALUES (?, 1, ?)",
                (conference_id, question)
            )
            conn.commit()
    except Exception as e:
        # Cleanup do arquivo físico em caso de erro de banco de dados
        if os.path.exists(local_path):
            try:
                os.remove(local_path)
            except Exception:
                pass
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    # 6. Retornar a resposta de sucesso
    return jsonify({
        "conference_id": conference_id,
        "round_number": 1,
        "question": question
    }), 201


@api_bp.route("/conference/answer", methods=["POST"])
@login_required
def submit_answer():
    # 1. Validar a presença de dados na requisição JSON
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
        
    conference_id = data.get("conference_id")
    answer = data.get("answer")
    
    if conference_id is None:
        return jsonify({"error": "conference_id is required"}), 400
        
    if not answer or not isinstance(answer, str) or answer.strip() == "":
        return jsonify({"error": "answer is required and cannot be empty"}), 400
        
    answer = answer.strip()
    user_id = session["user_id"]
    
    # 2. Verificar se a conferência existe e pertence ao usuário logado
    with get_db() as conn:
        conference = conn.execute(
            "SELECT * FROM conferences WHERE id = ? AND user_id = ?",
            (conference_id, user_id)
        ).fetchone()
        
    if not conference:
        return jsonify({"error": "Conference not found or unauthorized"}), 404

    # 3. Descobrir qual é a rodada ativa da conferência
    with get_db() as conn:
        active_round = conn.execute(
            "SELECT * FROM rounds WHERE conference_id = ? ORDER BY round_number DESC LIMIT 1",
            (conference_id,)
        ).fetchone()
        
    if not active_round:
        return jsonify({"error": "No rounds found for this conference"}), 400
        
    # 4. Validar se a rodada ativa já foi respondida
    if active_round["answer"] is not None:
        return jsonify({"error": "Round already answered"}), 400

    active_round_number = active_round["round_number"]

    # 5. Salvar a resposta do técnico na rodada ativa
    with get_db() as conn:
        conn.execute(
            "UPDATE rounds SET answer = ? WHERE id = ?",
            (answer, active_round["id"])
        )
        conn.commit()

    # 6. Se for rodada 1 ou 2, avançar para a próxima rodada chamando o Gemini
    if active_round_number in (1, 2):
        # Buscar o histórico completo de rodadas (incluindo a que acabamos de responder)
        with get_db() as conn:
            rounds_rows = conn.execute(
                "SELECT question, answer FROM rounds WHERE conference_id = ? ORDER BY round_number ASC",
                (conference_id,)
            ).fetchall()
            
        history = [
            {"question": r["question"], "answer": r["answer"]}
            for r in rounds_rows
        ]
        
        local_path = conference["screenshot_path"].lstrip("/")
        initial_context = conference["initial_context"]
        
        # Chamar a API externa (fora da transação de banco de dados)
        try:
            next_question = generate_next_question(local_path, initial_context, history)
        except Exception as e:
            # Em caso de falha da IA, fazemos o rollback da resposta inserida para manter integridade
            with get_db() as conn:
                conn.execute(
                    "UPDATE rounds SET answer = NULL WHERE id = ?",
                    (active_round["id"],)
                )
                conn.commit()
            return jsonify({"error": f"Failed to generate next question: {str(e)}"}), 500
            
        # Salvar a nova rodada com a pergunta gerada
        next_round_number = active_round_number + 1
        with get_db() as conn:
            conn.execute(
                "INSERT INTO rounds (conference_id, round_number, question) VALUES (?, ?, ?)",
                (conference_id, next_round_number, next_question)
            )
            conn.commit()
            
        return jsonify({
            "round_number": next_round_number,
            "question": next_question
        }), 200

    # 7. Se for a rodada 3, finalizar a coletiva
    elif active_round_number == 3:
        return jsonify({
            "status": "complete",
            "message": "All rounds finished, ready for chronicle generation"
        }), 200
        
    else:
        return jsonify({"error": "Invalid active round state"}), 400
