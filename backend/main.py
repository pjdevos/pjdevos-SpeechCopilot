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

        # Parse the response (we'll improve this later)
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

    # Language-specific instructions
    language_instructions = {
        "english": "Generate the speech in English.",
        "dutch": "Generate the speech in Dutch (Nederlands). Use proper Dutch grammar, vocabulary, and cultural references appropriate for a Dutch-speaking audience.",
        "french": "Generate the speech in French (Français). Use proper French grammar, vocabulary, and cultural references appropriate for a French-speaking audience."
    }

    language_instruction = language_instructions.get(
        request.language, language_instructions["english"])

    prompt = f"""You are an expert speechwriter. Generate a {request.length}-minute speech with the following specifications:

LANGUAGE REQUIREMENT:
{language_instruction}

CONTEXT:
- Occasion: {request.occasion}
- Audience: {request.audience}
- Tone: {request.tone}
- Template/Style: {request.template}
- Topic: {request.topic}
- Additional Context: {request.additional_context}

REQUIREMENTS:
1. Structure the speech with clear introduction, body, and conclusion
2. Match the specified tone throughout
3. Use language appropriate for the audience and cultural context
4. Include rhetorical devices suitable for the occasion
5. Ensure the speech fits the specified length
6. If generating in Dutch or French, use natural, fluent language that sounds native

DELIVERABLES:
Please provide:
1. The complete speech text in {request.language}
2. Mark sections clearly: [INTRODUCTION], [BODY], [CONCLUSION]
3. Include suggested emphasis points with *emphasis*
4. Add timing notes in parentheses (pause here)

Generate a compelling, well-structured speech that meets these requirements."""

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
