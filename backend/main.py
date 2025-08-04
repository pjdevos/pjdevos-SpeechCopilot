# main.py - The main application file

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from anthropic import Anthropic

# Load environment variables from .env file
load_dotenv()

# Create FastAPI app
app = FastAPI(title="Speech Copilot API",
              description="AI-powered speech generation")

# Enable CORS so your React frontend can talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://pjdevos-speech-copilot-a9iu.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Claude client
claude_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Data models for API requests


class SpeechRequest(BaseModel):
    occasion: str
    audience: str
    tone: str
    length: str
    template: str
    topic: str = ""
    additional_context: str = ""
    language: str = "english"


class SpeechResponse(BaseModel):
    speech: str
    structure: dict
    suggestions: list

# Basic health check endpoint


@app.get("/")
async def root():
    return {"message": "Speech Copilot API is running!"}

# Health check endpoint


@app.get("/health")
async def health_check():
    return {"status": "healthy", "claude_api": "connected" if os.getenv("ANTHROPIC_API_KEY") else "not configured"}

# Main speech generation endpoint


@app.post("/api/generate-speech", response_model=SpeechResponse)
async def generate_speech(request: SpeechRequest):
    """
    Generate a speech based on the provided parameters
    """
    try:
        # Build the prompt for Claude
        prompt = build_speech_prompt(request)

        # Log the prompt for debugging
        print(f"Generating speech in {request.language}")
        print(f"Prompt being sent to Claude: {prompt[:200]}...")

        # Call Claude API
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the speech from Claude's response
        speech_content = response.content[0].text

        # Log the response for debugging
        print(f"Claude response language check: {speech_content[:100]}...")

        # Parse the response
        return SpeechResponse(
            speech=speech_content,
            structure={
                "intro": "Generated introduction",
                "body": "Generated body",
                "conclusion": "Generated conclusion"
            },
            suggestions=[
                "Consider adding a personal anecdote",
                "The conclusion could be more actionable"
            ]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Speech generation failed: {str(e)}")


def build_speech_prompt(request: SpeechRequest) -> str:
    """
    Build a detailed prompt for Claude based on the user's requirements
    """

    if request.language == "dutch":
        language_instruction = """
ABSOLUUT KRITIEK: Schrijf deze GEHELE toespraak UITSLUITEND in het Nederlands. 
Elk woord, elke zin en elke paragraaf moet in het Nederlands zijn.
Gebruik GEEN Engelse woorden of zinnen.
Schrijf alsof je een Nederlandse moedertaalspreker bent.
Gebruik Nederlandse grammatica, Nederlandse woordenschat en Nederlandse culturele referenties.
Als je ook maar één woord in het Engels schrijft, dan heb je gefaald in deze taak.
"""

        prompt = f"""{language_instruction}

Je bent een expert speechschrijver. Maak een toespraak van {request.length} minuten met de volgende specificaties:

CONTEXT:
- Gelegenheid: {request.occasion}
- Publiek: {request.audience}
- Toon: {request.tone}
- Sjabloon/Stijl: {request.template}
- Onderwerp: {request.topic}
- Aanvullende context: {request.additional_context}

STRUCTUURVEREISTEN:
1. Duidelijke inleiding, hoofdgedeelte en conclusie
2. Behoud de gespecificeerde toon tijdens de hele toespraak
3. Gebruik taal die geschikt is voor het publiek
4. Gebruik retorische middelen die passen bij de gelegenheid
5. Zorg ervoor dat de toespraak past bij de gespecificeerde lengte

HERINNERING: De GEHELE toespraak moet in het Nederlands worden geschreven.

Genereer nu een overtuigende, goed gestructureerde Nederlandse toespraak."""

    elif request.language == "french":
        language_instruction = """
ABSOLUMENT CRITIQUE : Écrivez ENTIÈREMENT ce discours EXCLUSIVEMENT en français.
Chaque mot, chaque phrase et chaque paragraphe doit être en français.
N'utilisez AUCUN mot ou phrase en anglais.
Écrivez comme si vous étiez un locuteur natif français.
Utilisez la grammaire française, le vocabulaire français et les références culturelles françaises.
Si vous écrivez ne serait-ce qu'un mot en anglais, vous avez échoué dans cette tâche.
"""

        prompt = f"""{language_instruction}

Vous êtes un expert rédacteur de discours. Créez un discours de {request.length} minutes avec les spécifications suivantes :

CONTEXTE :
- Occasion : {request.occasion}
- Public : {request.audience}
- Ton : {request.tone}
- Modèle/Style : {request.template}
- Sujet : {request.topic}
- Contexte supplémentaire : {request.additional_context}

EXIGENCES STRUCTURELLES :
1. Introduction, corps et conclusion clairs
2. Maintenir le ton spécifié tout au long du discours
3. Utiliser un langage approprié pour le public
4. Inclure des dispositifs rhétoriques adaptés à l'occasion
5. S'assurer que le discours correspond à la durée spécifiée

RAPPEL : L'ENTIER discours doit être écrit en français.

Générez maintenant un discours français convaincant et bien structuré."""

    else:  # English
        language_instruction = "Write this speech in English."

        prompt = f"""{language_instruction}

You are an expert speechwriter. Create a {request.length}-minute speech with these specifications:

CONTEXT:
- Occasion: {request.occasion}
- Audience: {request.audience}
- Tone: {request.tone}
- Template/Style: {request.template}
- Topic: {request.topic}
- Additional Context: {request.additional_context}

STRUCTURE REQUIREMENTS:
1. Clear introduction, body, and conclusion
2. Match the specified tone throughout
3. Use language appropriate for the audience
4. Include rhetorical devices suitable for the occasion
5. Ensure the speech fits the specified length

Generate a compelling, well-structured speech now."""

    return prompt

# Test endpoint for debugging


@app.get("/api/test-claude")
async def test_claude():
    """
    Simple test to verify Claude API is working
    """
    try:
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Say hello and confirm you're working!"}
            ]
        )
        return {"claude_response": response.content[0].text}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Claude API test failed: {str(e)}")

# Test multilingual endpoint


@app.get("/api/test-multilingual/{language}")
async def test_multilingual(language: str):
    """
    Test multilingual generation for debugging
    """
    try:
        if language == "dutch":
            test_prompt = """
ABSOLUUT KRITIEK: Schrijf deze GEHELE respons UITSLUITEND in het Nederlands.

Schrijf een korte toespraak van 2 zinnen over het weer in Nederland.
Gebruik ALLEEN Nederlandse woorden.
"""
        elif language == "french":
            test_prompt = """
ABSOLUMENT CRITIQUE : Écrivez cette réponse ENTIÈRE EXCLUSIVEMENT en français.

Écrivez un court discours de 2 phrases sur la météo en France.
Utilisez UNIQUEMENT des mots français.
"""
        else:
            test_prompt = "Write a 2-sentence speech about the weather in English."

        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            messages=[
                {"role": "user", "content": test_prompt}
            ]
        )
        return {
            "language": language,
            "test_response": response.content[0].text,
            "prompt_used": test_prompt
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Multilingual test failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
