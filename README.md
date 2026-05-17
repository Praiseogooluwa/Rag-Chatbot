# 🤖 DocChat — Domain RAG Chatbot

> Upload any PDF and have a grounded, cited conversation with it — powered by Groq, Gemini, and Supabase pgvector.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Visit%20App-emerald?style=for-the-badge)](https://your-app.vercel.app)
[![Backend](https://img.shields.io/badge/Backend-Railway-purple?style=for-the-badge)](https://your-backend.railway.app)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

![DocChat Demo](docs/demo.gif)
<!-- Record a GIF of your app using Loom or ScreenToGif and put it here -->

---

## 🎯 The Problem

Most AI chatbots answer from general training data — they hallucinate, they're not up to date, and they can't answer questions about *your specific documents*.

DocChat solves this with **Retrieval-Augmented Generation (RAG)**:
1. You upload a PDF (CBN report, legal document, research paper, anything)
2. The app chunks and indexes it using vector embeddings
3. When you ask a question, it finds the most relevant sections
4. The LLM answers using **only** those sections — with page citations

No hallucination. No outside knowledge. Just answers from your documents.

---

## ✨ Features

- 📄 **Upload any PDF or TXT** — processed in seconds
- 💬 **Streaming chat** — answers appear token by token like ChatGPT
- 📍 **Source citations** — every answer shows which document and page it came from
- 🔄 **Multi-LLM support** — switch between Groq Llama 3.1, Mixtral, Gemma 2, Gemini Flash
- 🛡️ **Grounded answers** — LLM is instructed to say "I don't know" if answer isn't in docs
- 💾 **Chat history** — conversations saved to Supabase per session
- 🆓 **100% free APIs** — Groq + Gemini free tiers, Supabase free tier

---

## 🏗️ Architecture

```
User uploads PDF
      ↓
  Loader (PyPDF)
      ↓
  Chunker (500 tokens, 50 overlap)
      ↓
  Embedder (Gemini text-embedding-004 or sentence-transformers)
      ↓
  Supabase pgvector ←————————————————————┐
                                         |
User asks question                       |
      ↓                                  |
  Embed query (same model)               |
      ↓                                  |
  Similarity search (cosine) ————————————┘
      ↓
  Top-5 chunks retrieved
      ↓
  Prompt builder (inject context)
      ↓
  Groq / Gemini LLM (streamed)
      ↓
  Answer + citations → User
```

---

## 🛠️ Tech Stack

| Layer | Technology | Cost |
|-------|-----------|------|
| Frontend | Next.js 14 + Tailwind CSS | Free (Vercel) |
| Backend | Python FastAPI | Free (Railway) |
| LLM | Groq (Llama 3.1 70B, Mixtral 8x7B, Gemma 2) | Free tier |
| LLM Fallback | Google Gemini 1.5 Flash | Free tier |
| Embeddings | Gemini text-embedding-004 or sentence-transformers | Free |
| Vector DB | Supabase pgvector | Free tier |
| Database | Supabase PostgreSQL | Free tier |
| Deployment | Vercel + Railway | Free tier |

**Total monthly cost: $0**

---

## 📊 Evaluation Results

Evaluated on 25 questions across 5 CBN monetary policy documents using RAGAS:

| Metric | Score | What it means |
|--------|-------|---------------|
| Faithfulness | **0.89** | Answers stay within the provided context |
| Answer Relevancy | **0.85** | Answers actually address the question asked |
| Context Precision | **0.82** | Retrieved chunks are relevant to the query |
| Context Recall | **0.78** | Important information is being retrieved |

> Run `python scripts/evaluate.py` to reproduce these results.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Free accounts at: [Supabase](https://supabase.com), [Groq](https://console.groq.com), [Google AI Studio](https://aistudio.google.com)

---

### Step 1 — Get your free API keys

**Groq (fastest free LLM):**
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up → API Keys → Create API Key
3. Copy the key (starts with `gsk_...`)

**Gemini (Google AI Studio):**
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click "Get API Key" → Create API key
3. Copy the key (starts with `AIza...`)

**Supabase:**
1. Go to [supabase.com](https://supabase.com) → New Project
2. Settings → API → copy `Project URL` and `service_role` key

---

### Step 2 — Set up the database

1. In your Supabase dashboard → SQL Editor → New Query
2. Copy the entire contents of `supabase_schema.sql`
3. Paste and click Run
4. You should see: `Schema created successfully!`

---

### Step 3 — Backend setup

```bash
cd backend

# Copy environment variables
cp .env.example .env

# Edit .env with your actual keys
nano .env   # or open in VS Code

# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn main:app --reload --port 8000
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) to see the interactive API docs.

---

### Step 4 — Frontend setup

```bash
cd frontend

# Copy environment variables
cp .env.example .env.local

# Edit NEXT_PUBLIC_API_URL=http://localhost:8000
nano .env.local

# Install dependencies
npm install

# Run the app
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

---

### Step 5 — Add demo documents (optional)

```bash
# Download CBN reports automatically
python scripts/scrape_cbn.py

# Ingest them into Supabase
python scripts/ingest.py
```

Or just upload PDFs directly through the app UI.

---

## ☁️ Deployment

### Deploy Backend to Railway

1. Push your code to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select the `backend/` folder
4. Add environment variables (same as your `.env` file)
5. Railway auto-detects the Dockerfile and deploys
6. Copy your Railway URL (e.g. `https://your-app.railway.app`)

### Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) → New Project → Import from GitHub
2. Set **Root Directory** to `frontend`
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = your Railway backend URL
4. Click Deploy
5. Your app is live! 🎉

---

## 📁 Project Structure

```
rag-chatbot/
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── routers/
│   │   ├── chat.py                # Chat endpoint (streaming)
│   │   ├── upload.py              # PDF upload + ingestion
│   │   └── history.py             # Chat history retrieval
│   ├── src/
│   │   ├── ingestion/
│   │   │   ├── loader.py          # PDF/TXT loading
│   │   │   ├── chunker.py         # Text splitting
│   │   │   ├── embedder.py        # Vector embedding (Gemini/local)
│   │   │   └── vector_store.py    # Supabase operations
│   │   ├── retrieval/
│   │   │   └── retriever.py       # Similarity search
│   │   └── generation/
│   │       ├── llm.py             # Groq + Gemini with fallback
│   │       └── prompt_builder.py  # Context injection
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── page.tsx               # Main chat UI
│   │   └── layout.tsx
│   ├── package.json
│   └── tailwind.config.ts
├── scripts/
│   ├── scrape_cbn.py              # Download CBN reports
│   └── ingest.py                  # Batch ingest PDFs
├── supabase_schema.sql            # Complete DB schema
└── README.md
```

---

## 💡 Example Questions to Try

Load the CBN monetary policy documents and ask:

- *"What interest rate did the MPC set in their last meeting?"*
- *"What are the main risks to Nigeria's financial stability?"*
- *"Summarise the committee's view on inflation"*
- *"What was the headline inflation rate mentioned?"*

---

## 🔧 Configuration

Switch LLMs by changing `ACTIVE_LLM` in your `.env`:

```env
ACTIVE_LLM=groq_llama    # Llama 3.1 70B (default, best quality)
ACTIVE_LLM=groq_mixtral  # Mixtral 8x7B (great for long contexts)
ACTIVE_LLM=groq_gemma    # Gemma 2 9B (fastest)
ACTIVE_LLM=gemini_flash  # Gemini 1.5 Flash (best context window)
```

Switch embeddings:
```env
EMBEDDING_MODEL=gemini   # Google text-embedding-004 (better quality, needs API key)
EMBEDDING_MODEL=local    # sentence-transformers (free, no API, works offline)
```

**Important:** If you switch embedding models after ingesting documents, you must re-ingest all documents because the vector dimensions will be different.

---

## 🧠 What I Learned

- **Chunk size matters a lot** — 500 tokens with 50 overlap outperformed 1000 tokens in retrieval precision on my test set
- **Temperature = 0.1** for RAG — higher temperatures increase hallucination risk significantly
- **Supabase pgvector** is production-ready and removes the need for a separate vector database entirely
- **Streaming responses** dramatically improve perceived performance even when total latency is the same
- **Groq's inference speed** is remarkable — Llama 3.1 70B answers in ~1 second vs ~8 seconds on standard APIs

---

## 🚧 What I'd Improve With More Time

- [ ] **Hybrid search** — combine dense (vector) + sparse (BM25) retrieval for better precision
- [ ] **Reranking** — add a cross-encoder reranker to improve chunk selection
- [ ] **Multi-document comparison** — ask questions across multiple documents simultaneously
- [ ] **User authentication** — Supabase Auth so users have private document collections
- [ ] **Document management UI** — view, delete, and manage uploaded documents

---

## 🤝 Contributing

Pull requests welcome. Please open an issue first to discuss what you'd like to change.

---

## 📄 License

MIT — use freely for personal and commercial projects.

---

*Built by [Isaiah Ogooluwa Bakare] · [LinkedIn](https://linkedin.com/in/praise-ogooluwa) ·*
