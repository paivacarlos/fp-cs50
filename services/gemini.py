import os
import json 
from google import genai # type: ignore
from google.genai import types # type: ignore
from pydantic import BaseModel, Field

class ChronicleResponse(BaseModel):
    headline: str = Field(..., description="Main headline for the sports article.")
    chronicle: str = Field(..., description="Full sports article text.")


# 1. Configuração do SDK do Gemini

# Validando a chave do gemini
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from environment variables. Please check your .env file")

client = genai.Client(api_key=api_key)

def get_image_part(image_path: str) -> types.Part:
    """
    Lê a imagem do disco e a converte no formato de Part binário
    que o SDK do Gemini espera para payloads multimodais.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")
        
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        
    # Descobre o MIME type baseado na extensão do arquivo
    ext = image_path.rsplit(".", 1)[-1].lower()
    mime_type = f"image/{ext}"
    if ext == "jpg":
        mime_type = "image/jpeg"
        
    return types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type
    )

def generate_first_question(image_path: str, context: str) -> str:
    """
    Envia a imagem e as notas iniciais do técnico para o Gemini
    e retorna a primeira pergunta formulada pelo 'repórter'.
    """
    img_part = get_image_part(image_path)
    
    # Prompt instruindo a IA a agir como repórter
    prompt = (
        "You are a tough, professional sports reporter in a press conference. "
        "Analyze this EA FC post-match screenshot and the following notes from the coach:\n"
        f"'{context}'\n\n"
        "Ask an engaging, sharp, and realistic first question to the coach about the game. "
        "The question must be direct and in character. Do not include any intro, outro, or meta-commentary."
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[img_part, prompt]
    )
    return response.text.strip()

def generate_next_question(image_path: str, context: str, history: list) -> str:
    """
    Envia a imagem, as notas iniciais e o histórico de perguntas/respostas anteriores
    para o Gemini formular a pergunta lógica seguinte.
    """
    img_part = get_image_part(image_path)
    
    # Formata o histórico do diálogo para a IA entender o fluxo da conversa
    history_str = ""
    for round_data in history:
        history_str += f"Reporter: {round_data['question']}\nCoach: {round_data['answer']}\n\n"
        
    prompt = (
        "You are a tough, professional sports reporter in a press conference. "
        "Analyze this EA FC post-match screenshot, the coach's initial notes:\n"
        f"'{context}'\n\n"
        "And the previous dialogue transcript:\n"
        f"{history_str}"
        "Based on the coach's last answer and the match context, ask the next logical, sharp question. "
        "Do not repeat topics already discussed. Ask only one question. Do not include any intro or metadata."
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[img_part, prompt]
    )
    return response.text.strip()

def generate_chronicle(image_path: str, context: str, history: list) -> dict:
    """
    Envia a imagem, as notas e o histórico para o Gemini gerar
    a manchete e a crônica, retornando um dicionário (dict).
    """
    img_part = get_image_part(image_path)
    
    # Formata o histórico do diálogo
    history_str = ""
    for round_data in history:
        history_str += f"Reporter: {round_data['question']}\nCoach: {round_data['answer']}\n\n"
        
    prompt = (
        "You are a tough, professional sports reporter covering EA FC. "
        "Based on the coach's notes and the transcript of the interview:\n\n"
        f"Notes: {context}\n"
        f"Transcript: {history_str}\n\n"
        "Generate ONE complete JSON object with two keys:\n"
        "- 'headline': A catchy, punchy headline for the match review.\n"
        "- 'chronicle': The full, detailed sports article (around 200-300 words)."        
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[img_part, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ChronicleResponse,
        )
    )
    
    # Com response_mime_type="application/json", response.text vem como JSON puro
    return json.loads(response.text.strip())
