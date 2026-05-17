# Windows Setup Guide
## Everything you need to run this project on Windows

---

## Step 1 — Install the tools you need (do this once ever)

### Python 3.11
1. Go to https://python.org/downloads
2. Click the big yellow "Download Python 3.11.x" button
3. Run the installer
4. **VERY IMPORTANT** — on the first screen, tick the box that says:
   ✅ "Add Python to PATH"
   (it is NOT ticked by default — if you miss this, nothing will work)
5. Click "Install Now"

To verify it worked, open Command Prompt and type:
```
python --version
```
You should see: Python 3.11.x

---

### Node.js
1. Go to https://nodejs.org
2. Download the LTS version (the left button, says "Recommended For Most Users")
3. Run the installer — just keep clicking Next, no special options needed
4. Restart your computer after installing

To verify:
```
node --version
npm --version
```

---

### VS Code (code editor)
1. Go to https://code.visualstudio.com
2. Download and install
3. Open it, then install these extensions:
   - Python (by Microsoft)
   - ES7+ React/Redux/React-Native snippets
   - Tailwind CSS IntelliSense

---

## Step 2 — Unzip and open the project

1. Right-click `rag-chatbot.zip` → Extract All → choose where you want it (e.g. Desktop)
2. Open VS Code
3. File → Open Folder → select the `rag-chatbot-final` folder
4. You should see all the files in the left panel

---

## Step 3 — Fill in your API keys

1. Inside VS Code, open `backend\.env.example`
2. In the Explorer panel (left side), right-click the `backend` folder → New File → name it `.env`
3. Copy everything from `.env.example` into `.env`
4. Replace the placeholder values with your real keys:

```
SUPABASE_URL=https://xyzxyzxyz.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
GROQ_API_KEY=gsk_aBcDeFgHiJkLmNoPqRsTuV...
GEMINI_API_KEY=AIzaSyAbCdEfGhIjKlMnOpQr...
ACTIVE_LLM=groq_llama
EMBEDDING_MODEL=local
```

⚠️ Never share your .env file or push it to GitHub. The .gitignore already protects you.

---

## Step 4 — Run the project

Double-click `run_local.bat`

OR open Command Prompt in the project folder and type:
```
run_local.bat
```

It will:
- Create a Python virtual environment automatically
- Install all Python packages
- Install all Node packages (first time takes ~1 minute)
- Open two terminal windows (one backend, one frontend)
- Print the URLs to visit

---

## Step 5 — Set up your Supabase database

Before using the app you need to run the SQL schema once:

1. Go to https://supabase.com and log in
2. Open your project
3. Click "SQL Editor" in the left sidebar
4. Click "New Query"
5. Open `supabase_schema.sql` from the project folder
6. Copy ALL the text inside it
7. Paste it into the Supabase SQL Editor
8. Click the green "Run" button
9. You should see: "Schema created successfully!"

---

## Step 6 — Test it works

1. Open http://localhost:3000 in your browser
2. Click "Upload PDF" and upload any PDF
3. Wait for it to process
4. Type a question and press Enter
5. You should see a streamed answer with page citations ✅

---

## Useful Windows terminal commands

Open the project folder in Command Prompt:
```
cd C:\Users\YourName\Desktop\rag-chatbot-final
```

Activate the Python virtual environment manually:
```
cd backend
venv\Scripts\activate
```

Run the backend manually:
```
cd backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

Run the frontend manually:
```
cd frontend
npm run dev
```

Ingest PDFs into Supabase:
```
cd backend
venv\Scripts\activate
cd ..
python scripts\ingest.py
```

---

## Common Windows errors and fixes

**"python is not recognized as a command"**
→ You forgot to tick "Add Python to PATH" during install
→ Fix: Uninstall Python, reinstall, tick the box this time

**"pip is not recognized"**
→ Same issue — reinstall Python with PATH option ticked

**"npm is not recognized"**
→ Node.js not installed or you didn't restart after installing
→ Fix: Restart your computer

**"EACCES permission denied" on npm install**
→ Run Command Prompt as Administrator (right-click → Run as administrator)

**"uvicorn is not recognized"**
→ You forgot to activate the virtual environment
→ Fix: run `venv\Scripts\activate` first, then uvicorn again

**Port 8000 already in use**
→ Something else is using that port
→ Fix: `uvicorn main:app --reload --port 8001` and update .env.local to http://localhost:8001

**App loads but upload fails**
→ Check that your .env file has the correct Supabase keys
→ Check that you ran supabase_schema.sql successfully
