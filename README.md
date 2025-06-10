# AI Commerce Agent – Backend

This is the backend service for an AI-powered shopping assistant that leverages Google's Gemini API. It accepts both text and image inputs from users and responds with context-aware product information based on a predefined catalog.

---

## 🚀 Tech Stack

- **FastAPI** – Chosen for its speed, ease of use, and native async support, allowing efficient handling of multiple concurrent requests.
- **Google Gemini (`google-genai`)** – Provides powerful multimodal AI capabilities to process both text and images.
- **Pillow** – Lightweight image processing library for decoding and validating uploads.
- **python-dotenv** – Simplifies environment variable management for local development.
- **Uvicorn** – High-performance ASGI server to run FastAPI applications.
- **python-multipart** – Required for parsing file uploads in FastAPI.

---

## 🛠️ Setup Instructions

1. **Clone the repo**  
   ```bash
   git clone https://github.com/Yash294/ai-commerce-agent-backend.git
   cd ai-commerce-agent-backend
   ```
2. **Create a `.env` file**  
   ```env
   GEMINI_API_KEY=your_google_api_key
   ```
3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the server locally**  
   ```bash
   uvicorn main:app --reload
   ```

---

## 📦 API Endpoint

### `POST /chat`

**Accepts:**  
- `user_id` (string): unique user session ID  
- `message` (string, optional): text query  
- `file` (image, optional): image upload of a product  

**Returns:**  
- JSON  
  ```json
  {
    "response": "<ai reply>"
  }
  ```

---

## 🌐 Deployment

Hosted on [Railway](https://railway.app).

**Railway Environment Variables:**  
- `GEMINI_API_KEY=your_google_api_key_here`

**Start Command:**  
```bash
bash start.sh
```

---

## 💡 Design Decisions

- **In-Memory Sessions**  
  Used for simplicity in a take-home demo. Easily tracks conversational context per user without external infrastructure. For production, a shared store like Redis would be implemented.
- **Single Image Response**  
  Limits AI responses to one image to keep the UI clean and avoid overwhelming the user.
- **File-Size Guard & Timeout**  
  Protects backend resources by rejecting large uploads and timing out slow AI calls, enhancing reliability.
- **Environment Variables**  
  `python-dotenv` simplifies local secret management, and deployment platforms handle production variables.
- **Componentized Code**  
  Separation of concerns (e.g., utility functions, message rendering) ensures maintainability and readability.

---

## 🔐 Notes

- This service is designed for demo purposes. It demonstrates core AI integration and API design but is not optimized for production scale.
- Error handling and guards ensure robust behavior under common failure scenarios.
