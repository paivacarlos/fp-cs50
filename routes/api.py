import os
from flask import Blueprint, request, jsonify, session
from utils.security import login_required
from utils.upload import save_upload_file
from services.db import get_db
from services.gemini import generate_first_question

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
