import os
import uuid


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename: str) -> bool:
    return ("." in filename and
            filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS)

def validate_image_content(file_stream) -> bool:
    """
    Verifica os primeiros 12 bytes do arquivo (magic bytes) para validar a assinatura
    de formatos de imagem suportados (PNG, JPEG, GIF). Restaura o ponteiro do fluxo ao final.
    """
    header = file_stream.read(12)
    file_stream.seek(0)
    
    # PNG: 89 50 4E 47 0D 0A 1A 0A
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return True
    
    # JPEG: FF D8 FF
    if header.startswith(b"\xff\xd8\xff"):
        return True
    
    # GIF: GIF87a ou GIF89a
    if header.startswith(b"GIF87a") or header.startswith(b"GIF89a"):
        return True
        
    return False

def save_upload_file(file, upload_folder: str) -> str:
    # 1. arquivo foi enviado e tem nome?
    if not file or file.filename == "":
        raise ValueError("No file selected or empyt filename")

    # 2. tipo de arquivo permitido?
    if not allowed_file(file.filename):
        raise ValueError("File type not allowed")

    #3. garante que a pasta existe
    os.makedirs(upload_folder, exist_ok=True)

    # 4. Extrai a extensão original em minúsculas (ex: 'png')
    ext = file.filename.rsplit(".", 1)[1].lower()

    # 5. Cria um nome único
    unique_filename = f"{uuid.uuid4()}.{ext}"

    # 6. Criar o caminho absoluto/completo para onde o arquivo será gravado
    # Exemplo: 'static/uploads/f47ac10b-58cc-4372-a567-0e02b2c3d479.png'
    filepath = os.path.join(upload_folder, unique_filename)

    # 7. Salvar o arquivo
    file.save(filepath)

    # 8. Retornar apenas o nome único do arquivo gerado
    # (Ou o caminho relativo, dependendo de como você quer armazenar no banco)
    return f"/{upload_folder}/{unique_filename}".replace('//', '/')


