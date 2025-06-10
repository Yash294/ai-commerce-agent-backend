import logging
import asyncio
import io
import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from google import genai
from PIL import Image

# Basic logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MAX_BYTES = 5 * 1024 * 1024  # 5 MB
TIMEOUT_SECONDS = 10.0       # Gemini call timeout

# FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment and Gemini client
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not set")
client = genai.Client(api_key=GEMINI_API_KEY)

# Load and format catalog once on startup
def format_catalog(items):
    return "\n".join(
        f"- {item['name']}: {item['description']} | Price: ${item['price']} | "
        f"Material: {item['material']} | Colors: {', '.join(item['colour'])} | "
        f"Stock: {item['stock']} | Image: {item['image_url']}"
        for item in items
    )

with open("product_catalog.json") as f:
    CATALOG = json.load(f)
catalog_str = format_catalog(CATALOG)

# In-memory session storage (demo only)
user_sessions = {}

@app.post("/chat")
async def chat(
    user_id: str = Form(...),
    message: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")

    # Initialize chat session
    if user_id not in user_sessions:
        session = client.chats.create(model="gemini-2.0-flash")
        prompt = (
            "You are a helpful AI shopping assistant named ShopperAI. "
            "Answer customer questions based only on the following product catalog and any clothing images they send. "
            "Provide details such as price, material, color options, stock availability, or general descriptions. If an image or images is requested, provide only one and state that only one is allowed at a time.\n\n"
            f"{catalog_str}"
        )
        session.send_message(prompt)
        user_sessions[user_id] = session

    contents = []

    # Handle uploaded image with size guard
    if file:
        try:
            img_bytes = await file.read()
            if len(img_bytes) > MAX_BYTES:
                raise HTTPException(status_code=400, detail="File too large")
            image = Image.open(io.BytesIO(img_bytes))
            contents.append(image)
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to read image for user %s", user_id)
            raise HTTPException(status_code=400, detail=f"Image read failed: {str(e)}")

    # Handle text
    if message and message.strip():
        contents.append(message.strip())

    if not contents:
        raise HTTPException(status_code=400, detail="No image or message provided")

    # Send to Gemini with timeout
    session = user_sessions[user_id]
    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(session.send_message, contents),
            timeout=TIMEOUT_SECONDS
        )
        return {"response": response.text}
    except asyncio.TimeoutError:
        logger.error("Gemini timeout for user %s", user_id)
        raise HTTPException(status_code=504, detail="Upstream service timed out")
    except Exception as e:
        logger.exception("Chat processing failed for user %s", user_id)
        raise HTTPException(status_code=500, detail="Internal error")