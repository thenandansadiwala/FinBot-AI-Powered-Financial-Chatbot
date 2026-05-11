# FinBot: AI-Powered Financial Chatbot

FinBot is a production-grade full-stack financial assistant that uses **LangGraph**, **FastAPI**, and **Next.js** to provide real-time data retrieval and qualitative analysis of ETFs and Mutual Funds.

## 🚀 Features

- **Intent-Based Routing:** Uses an LLM classifier to route queries between SQL data filtering and Vector semantic search.
- **Dynamic Context:** Automatically tracks mentioned fund tickers in a real-time "Active Context" sidebar.
- **SQL Agent:** Executes complex financial queries against a PostgreSQL database for hard metrics (Expense ratios, NAV, Assets).
- **Vector Search:** Performs semantic similarity searches on fund strategies and qualitative descriptions using Azure OpenAI embeddings.
- **Premium UI:** A modern, Gemini-inspired dark mode interface with auto-resizing inputs and full Markdown/Table support.
- **Deep Logging:** Detailed execution tracing in `activity.log` and `error.log`.

## 🏗️ Architecture Overview

![System Flow Design](System%20Design/System%20Flow%20Design.png)

---

## 🛠️ Tech Stack

- **Backend:** Python 3.12, FastAPI, LangGraph, SQLAlchemy (Async), PostgreSQL (pgvector).
- **AI/LLM:** Azure OpenAI (GPT-4o, text-embedding-ada-002).
- **Frontend:** Next.js 15, TypeScript, Tailwind CSS v4, React Markdown.

---

## ⚙️ Setup Instructions

### 1. Backend Configuration

1. **Navigate to backend:**
   ```bash
   cd backend
   ```
2. **Environment Variables:** Create a `.env` file in the `backend/` folder:
   ```env
   AZURE_OPENAI_API_KEY=your_key
   AZURE_OPENAI_ENDPOINT=your_endpoint
   LLM_MODEL=gpt-4o
   EMBEDDING_MODEL=text-embedding-ada-002
   DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname
   SYNC_DB_URL=postgresql://user:pass@localhost:5432/dbname
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Database Seeding (Optional):**
   ```bash
   python -m app.db.seed_db
   ```
5. **Run FastAPI:**
   ```bash
   python app/main.py
   ```

### 2. Frontend Configuration

1. **Navigate to frontend:**
   ```bash
   cd frontend
   ```
2. **Install Packages:**
   ```bash
   npm install
   ```
3. **Run Dev Server:**
   ```bash
   npm run dev
   ```

---

## 📂 Project Structure

```text
├── backend/
│   ├── app/
│   │   ├── agent/       # LangGraph nodes, tools, and state
│   │   ├── core/        # Config and Logger
│   │   ├── db/          # Models and Database initialization
│   │   └── main.py      # FastAPI Entry point
│   ├── logs/            # activity.log & error.log
│   └── requirements.txt
├── frontend/
│   ├── src/app/         # Next.js Chat interface and styles
│   └── package.json
└── README.md
```

## 📝 Usage Examples

- **SQL Filter:** "Show me funds with an expense ratio lower than 0.1%."
- **Vector Search:** "Which funds are focused on sustainable energy and tech growth?"
- **Comparison:** "Compare the total assets of SPY and QQQ in a table."

---

*Built with ❤️ by Antigravity AI*
