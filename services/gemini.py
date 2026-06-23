import os
import json 
from google import genai # type: ignore
from google.genai import types # type: ignore
from pydantic import BaseModel, Field

class ChronicleResponse(BaseModel):
    headline: str = Field(..., description="Main headline for the sports article.")
    chronicle: str = Field(..., description="Full sports article text.")


# 1. Configuração do SDK do Gemini & Variáveis de Ambiente
mock_gemini_env = os.getenv("MOCK_GEMINI", "false").lower() == "true"
api_key = os.getenv("GEMINI_API_KEY")
gemini_model_env = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

client = None
if not mock_gemini_env:
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
    if mock_gemini_env:
        return "Coach, thank you for taking the stage. Looking at the post-match stats on the screen, your squad seemed to struggle with defensive transitions. How do you plan to address these tactical errors in training?"

    img_part = get_image_part(image_path)
    
    # Prompt instruindo a IA a agir como repórter e validar a imagem
    prompt = (
        "You are a tough, professional sports reporter in a press conference. "
        "First, verify if the attached image is a gameplay or post-match stats screenshot of a football game (like EA FC). "
        "If the image is completely unrelated to a football game (such as a tree, a person, an animal, a generic object, or a landscape), you must reply with exactly: 'ERROR: INVALID_IMAGE'. "
        "Otherwise, if it is a valid game screenshot, analyze this EA FC post-match screenshot and the following notes from the coach:\n"
        f"'{context}'\n\n"
        "Ask an engaging, sharp, and realistic first question to the coach about the game. "
        "The question must be direct and in character. Do not include any intro, outro, or meta-commentary."
    )
    
    response = client.models.generate_content(
        model=gemini_model_env,
        contents=[img_part, prompt]
    )
    return response.text.strip()

def generate_next_question(image_path: str, context: str, history: list) -> str:
    """
    Envia a imagem, as notas iniciais e o histórico de perguntas/respostas anteriores
    para o Gemini formular a pergunta lógica seguinte.
    """
    if mock_gemini_env:
        round_count = len(history)
        if round_count == 1:
            return "Interesting perspective, coach. However, statistics indicate that your midfield was frequently bypassed, leading to high-pressure situations. How do you respond to critics claiming your strategy was too passive?"
        elif round_count == 2:
            return "To wrap up, supporters are demanding changes in the starting eleven for the upcoming derby. Will we see any tactical adjustments or roster rotations in the next match?"
        else:
            return "Coach, could you elaborate on how your team's tactical positioning influenced this performance?"

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
        model=gemini_model_env,
        contents=[img_part, prompt]
    )
    return response.text.strip()

def generate_chronicle(image_path: str, context: str, history: list) -> dict:
    """
    Envia a imagem, as notas e o histórico para o Gemini gerar
    a manchete e a crônica, retornando um dicionário (dict).
    """
    if mock_gemini_env:
        return {
            "headline": "COACH PROMISES TACTICAL REVOLUTION AFTER CHALLENGING FIXTURE!",
            "chronicle": (
                "In a highly anticipated post-match press conference, the manager faced tough questioning from sports correspondents. "
                "Following a match that highlighted glaring transition issues, the coach was asked to address the squad's defensive vulnerability and lack of midfield control.\n\n"
                "In response, the manager acknowledged the difficulties but stood by the team's effort, promising immediate tactical adjustments. "
                "With a crucial derby match scheduled for next week, supporters are eager to see if these adjustments will yield a more cohesive performance on the pitch."
            )
        }

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
        model=gemini_model_env,
        contents=[img_part, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ChronicleResponse,
        )
    )
    
    # Com response_mime_type="application/json", response.text vem como JSON puro
    return json.loads(response.text.strip())
