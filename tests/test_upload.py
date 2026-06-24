import pytest
import os
from io import BytesIO
from utils.upload import save_upload_file, allowed_file

# Mock para simular o comportamento de um arquivo enviado no Flask
class MockFile:
    def __init__(self, filename, content=b""):
        self.filename = filename
        self.content = content
        self.stream = BytesIO(content)

    def save(self, filepath):
        with open(filepath, "wb") as f:
            f.write(self.content)

def test_allowed_file():
    assert allowed_file("test.png") is True
    assert allowed_file("test.jpg") is True
    assert allowed_file("test.TXT") is False
    assert allowed_file("no_extension") is False

def test_save_upload_file_success(tmp_path):
    # Usando o diretório temporário gerado pelo pytest
    upload_dir = str(tmp_path / "uploads")
    
    mock_file = MockFile("screenshot.png", b"\x89PNG\r\n\x1a\nimage data")
    
    relative_path = save_upload_file(mock_file, upload_dir)
    
    # 1. Verifica se o arquivo físico foi criado
    absolute_path = os.path.join(upload_dir, os.path.basename(relative_path))
    assert os.path.exists(absolute_path)
    
    # 2. Verifica se o retorno contém o caminho relativo correto com barras normais
    assert "uploads/" in relative_path
    assert relative_path.endswith(".png")

def test_save_upload_file_invalid_extension(tmp_path):
    upload_dir = str(tmp_path / "uploads")
    mock_file = MockFile("virus.exe", b"bad code")
    
    with pytest.raises(ValueError, match="File type not allowed"):
        save_upload_file(mock_file, upload_dir)

def test_save_upload_file_empty_filename(tmp_path):
    upload_dir = str(tmp_path / "uploads")
    mock_file = MockFile("", b"")
    
    with pytest.raises(ValueError, match="No file selected or empyt filename"):
        save_upload_file(mock_file, upload_dir)

def test_save_upload_file_invalid_magic_bytes(tmp_path):
    upload_dir = str(tmp_path / "uploads")
    # Arquivo com extensão png válida, mas cabeçalho binário inválido (de texto)
    mock_file = MockFile("test.png", b"fake text content here")
    
    with pytest.raises(ValueError, match="Invalid image content"):
        save_upload_file(mock_file, upload_dir)
