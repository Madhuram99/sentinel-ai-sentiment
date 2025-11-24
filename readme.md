# 🤖 Sentiment AI Assistant (Django + Groq + VADER)

A voice-enabled, context-aware chatbot that performs real-time sentiment analysis on conversation flows. Built for the LiaPlus Assignment.

## 🚀 Key Features (Innovations)
- **Hybrid Intelligence:** Combines VADER (Rule-based) for speed with Llama 3 (LLM) for conversational capability.
- **Voice Interface:** Full Speech-to-Text and Text-to-Speech support using Web Speech API.
- **Structured Output:** AI strictly adheres to JSON format to provide "Smart Suggestions" (clickable chips).
- **Dynamic UI:** Interface colors morph (Green/Red/Blue) based on the user's emotional state.
- **Reporting:** One-click generation of PDF transcripts with sentiment graphs.

## 🛠️ Chosen Technologies
- [cite_start]**Backend:** Django 5.0 (Session management, API routing) [cite: 25]
- **AI Engine:** LangChain + Groq (Llama-3.1-8b-instant)
- [cite_start]**Sentiment Logic:** NLTK VADER (Valence Aware Dictionary and sEntiment Reasoner) [cite: 26]
- **Frontend:** HTML5, CSS3, JavaScript (Fetch API, Chart.js, jsPDF)

## 🧠 Explanation of Sentiment Logic
[cite_start]The application uses a dual-layer approach[cite: 26]:
1. **Statement-Level (Tier 2):** Every incoming message is scored by VADER. The `compound` score determines if the text is Positive (>0.05), Negative (<-0.05), or Neutral. This score is injected into the System Prompt, instructing Llama 3 to adapt its tone (e.g., "De-escalate" if negative).
2. **Conversation-Level (Tier 1):** We track the running average of all compound scores. At the end of the session, this average determines the "Overall Conversation Sentiment" and generates the mood trend graph.

## ✅ Status of Tier 2 Implementation
[cite_start]**Completed and Exceeded.** - Each message displays its individual sentiment score in real-time[cite: 27].
- [cite_start]The UI provides an optional "Mood Trend" graph upon ending the chat[cite: 14].

---

## 🔮 Future Architecture & Scalability Roadmap
*While the current prototype runs on a development server, the following architecture is designed for scaling to 10,000+ concurrent users.*



### Phase 1: App Server (Concurrency)
* **Current:** `python manage.py runserver` (Single-threaded, blocking).
* **Future Implementation:** Migrate to **Gunicorn** (WSGI) behind an **Nginx** reverse proxy to handle concurrent request forking.

### Phase 2: Data Layer (Throughput)
* **Current:** SQLite (File-based locking).
* **Future Implementation:** Migrate to **PostgreSQL**. This enables **Row-Level Locking**, allowing thousands of users to write messages simultaneously without "Database Locked" errors.

### Phase 3: Asynchronous Task Queue
* **Current:** Synchronous API calls (User waits for Llama 3 generation).
* **Future Implementation:** Implement **Celery + Redis**.
    * *Flow:* User sends message -> Server accepts (202 Accepted) -> **Celery Worker** processes LLM request in background -> Server pushes result via WebSockets.



---

## 🏃‍♂️ How to Run

### [cite_start]Option 1: Standard [cite: 24]
1. Clone the repo.
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with `GROQ_API_KEY=your_key`.
4. Run migrations: `python manage.py migrate`
5. Start server: `python manage.py runserver`

### Option 2: Docker
1. `docker build -t sentiment-bot .`
2. `docker run -p 8000:8000 --env-file .env sentiment-bot`

## 🧪 Tests
Unit tests are included for API endpoints and sentiment logic.
Run via: `python manage.py test`