import os
import threading
import time
import pytest
from app import app
from services.db import init_db

@pytest.fixture(scope="session")
def live_server():
    # Configura o banco de dados de testes da UI antes de importar/inicializar o app
    os.environ["DATABASE_PATH"] = "test_ui_conference_data.db"
    
    # Inicializa as tabelas no banco de dados temporário
    init_db()
    
    # Define a porta do servidor de testes
    port = 5002
    
    # Executa o Flask em uma thread separada em segundo plano
    server_thread = threading.Thread(
        target=lambda: app.run(port=port, debug=False, use_reloader=False)
    )
    server_thread.daemon = True
    server_thread.start()
    
    # Aguarda 1.5 segundos para garantir que o Flask subiu e está ouvindo requisições
    time.sleep(1.5)
    
    yield f"http://127.0.0.1:{port}"
    
    # Limpeza após todos os testes de UI rodarem
    if os.path.exists("test_ui_conference_data.db"):
        try:
            os.remove("test_ui_conference_data.db")
        except Exception:
            pass
