# 🚀 Complete Setup & Running Guide

## ✅ Installation Status

All dependencies have been installed and configured. Here's what's ready:

### Frontend Dependencies

- ✅ Next.js 16.1.6
- ✅ React 19.2.3
- ✅ TypeScript 5.9.3
- ✅ Tailwind CSS 4.2.1
- ✅ Framer Motion (animations)
- ✅ Lucide React (icons)
- ✅ LiveKit Client & Components
- ✅ PDF processing (pdf-lib, qrcode)

### Backend Dependencies

- ✅ FastAPI 0.135.1
- ✅ Uvicorn 0.41.0
- ✅ LiveKit Agents 1.4.5
- ✅ LiveKit Plugins:
  - OpenAI (STT/TTS/LLM)
  - Silero (VAD - Voice Activity Detection)
  - Google Cloud (backup)
- ✅ OpenAI SDK 2.28.0
- ✅ Python 3.11+ with uv package manager

### Files Organized

```
backend/
├── server.py              (FastAPI token generator)
├── Vision.py              (LiveKit AI Agent) ✨
├── pdf_generate.py        (PDF filling engine)
├── 心身障碍者福祉手当認定申請書.json          (Form schema)
├── 心身障碍者福祉手当認定申請書Mapping.json   (PDF coordinates)
├── blank_form.pdf         (Template form)
├── .env.local             (Environment variables)
└── .venv/                 (Python virtual environment)
```

---

## 🎯 Quick Start (3 Options)

### Option 1️⃣: Run Everything (Recommended)

**One command to start the entire system:**

```bash
cd /Users/y4l1/Documents/GDGJP-Hackathon/ai-privacy-amanuensis
./start-all.sh
```

This starts:

- 📡 Backend API (port 8000)
- 🧠 Vision Agent (LiveKit)
- 🎨 Frontend (port 3001)

Then visit: **http://localhost:3001/form**

---

### Option 2️⃣: Backend + Agent Only (Without Frontend)

**If you already have frontend running:**

```bash
cd /Users/y4l1/Documents/GDGJP-Hackathon/ai-privacy-amanuensis
./start-backend-agent.sh
```

Starts the API and Vision Agent in the background.

---

### Option 3️⃣: Manual Control (Separate Terminals)

**Terminal 1 - Start Backend API:**

```bash
cd /Users/y4l1/Documents/GDGJP-Hackathon/ai-privacy-amanuensis/backend
uv run uvicorn server:app --reload
```

Wait for: `Uvicorn running on http://0.0.0.0:8000`

**Terminal 2 - Start Vision Agent:**

```bash
cd /Users/y4l1/Documents/GDGJP-Hackathon/ai-privacy-amanuensis/backend
uv run python Vision.py dev
```

Wait for: `✅ AI connected`

**Terminal 3 - Start Frontend:**

```bash
cd /Users/y4l1/Documents/GDGJP-Hackathon/ai-privacy-amanuensis
npm run dev
```

Wait for: Local: http://localhost:3001

---

## 🔑 Environment Variables

### Frontend (`.env.local`)

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_LIVEKIT_URL=wss://jing-139sv34p.livekit.cloud
LIVEKIT_API_KEY=APIDEhbphUuktPc
LIVEKIT_API_SECRET=QHhPj1sA9t2bBQZJysHwCezpHyMEAC6ilqHTUj9cAGM
```

### Backend (`.env.local`)

```env
LIVEKIT_URL=wss://jing-139sv34p.livekit.cloud
LIVEKIT_API_KEY=APIDEhbphUuktPc
LIVEKIT_API_SECRET=QHhPj1sA9t2bBQZJysHwCezpHyMEAC6ilqHTUj9cAGM
OPENAI_API_KEY=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
```

✅ Both files already created and configured!

---

## 🧠 System Architecture

```
┌─────────────────────────────────────────────────────┐
│         🎨 Frontend (Next.js)                       │
│         http://localhost:3001                       │
│  - FormPage component                               │
│  - Conversation UI                                  │
│  - Form data collection                             │
└────────────────┬────────────────────────────────────┘
                 │
                 │ HTTP + WebSocket
                 │
┌────────────────▼────────────────────────────────────┐
│         📡 Backend API (FastAPI)                    │
│         http://localhost:8000                       │
│  - Token generation (/get_token)                    │
│  - CORS handling                                    │
└────────────────┬────────────────────────────────────┘
                 │
                 │ LiveKit WebSocket
                 │
┌────────────────▼────────────────────────────────────┐
│    🧠 Vision Agent (LiveKit + OpenAI)               │
│    Working Flow:                                    │
│  1. Listen to user (Speech-to-Text)                │
│  2. Understand intent (OpenAI GPT-4)               │
│  3. Fill form fields intelligently                 │
│  4. Respond naturally (Text-to-Speech)             │
│  5. Generate PDF with collected data               │
└─────────────────────────────────────────────────────┘
```

---

## 🔍 What Each Component Does

### Frontend (Next.js)

- ✅ Renders form UI
- ✅ Gets JWT token from backend
- ✅ Connects to LiveKit room
- ✅ Shows conversation history
- ✅ Allows JSON download
- ✅ Shows connection status

### Backend (FastAPI)

- ✅ Generates JWT tokens for LiveKit
- ✅ Handles CORS for frontend
- ✅ Provides `/get_token` endpoint
- ✅ Ready for future endpoints

### Vision Agent (LiveKit)

- ✅ **Listens** - Converts speech to text (OpenAI STT)
- ✅ **Understands** - Processes with GPT-4o-mini
- ✅ **Fills** - Collects form data intelligently
- ✅ **Responds** - Converts responses to speech (OpenAI TTS)
- ✅ **Saves** - Generates JSON with answers
- ✅ **Renders** - Can fill PDF forms with data

### Available Tools (called by Agent)

1. `start_form_filling(form_type)` - Load form schema
2. `open_my_files()` - Navigate to past submissions
3. `submit_form_data(json_string)` - Save completed form

---

## 🌐 Access Endpoints

### Frontend

- **Home**: http://localhost:3001
- **Form Page**: http://localhost:3001/form
- **Success**: http://localhost:3001/success

### Backend API

- **Token Endpoint**: http://localhost:8000/get_token
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health (if added)

### LiveKit

- **Cloud URL**: wss://jing-139sv34p.livekit.cloud
- **Room**: Automatically created on first connection

---

## 🧪 Testing the System

### Test 1: Backend Token Generation

```bash
curl "http://localhost:8000/get_token?room_name=test&participant_name=demo"
```

Should return a JWT token.

### Test 2: Frontend Form Page

Visit: http://localhost:3001/form

- Header should show ✅ Ready
- Token shown as: eyJhbGc...

### Test 3: Voice Conversation

1. Click "音声入力" (Voice Input) button
2. Speak to the AI agent
3. See responses appear on screen
4. Watch form data collect in preview

### Test 4: Download JSON

1. Have a conversation
2. Click "JSONをダウンロード"
3. Check downloaded file contains your data

---

## 🐛 Troubleshooting

| Issue                    | Solution                                         |
| ------------------------ | ------------------------------------------------ |
| Port 3001 already in use | `pkill -f "npm\|next"` then retry                |
| Port 8000 already in use | `pkill -f "uvicorn"` then retry                  |
| Agent won't connect      | Check LIVEKIT_URL and API keys in .env           |
| No voice output          | Ensure speakers are connected and unmuted        |
| OpenAI errors            | Verify OPENAI_API_KEY is valid (starts with sk-) |
| PDF not saving           | Check file permissions on backend folder         |
| Dark theme not working   | Hard refresh browser (Cmd+Shift+R)               |

---

## 📊 System Requirements

**Minimum Hardware:**

- RAM: 4GB
- CPU: 2+ cores
- Storage: 500MB free

**Network:**

- Internet connection required (for LiveKit cloud)
- WebSocket support (for real-time communication)
- Microphone access (for voice)

**Software:**

- macOS/Linux/Windows
- Node.js 18+
- Python 3.11+
- uv package manager

---

## 📈 Performance Tuning

**For Better Performance:**

Frontend:

```bash
npm run build  # Optimize for production
npm run start  # Run production build
```

Agent Response Time:

- Faster: Use `gpt-4-turbo` (cheaper)
- Slower but smarter: Use `gpt-4` (more accurate)

---

## 🔄 Development Workflow

### Making Changes to Frontend

```bash
npm run dev  # Auto-reloads on save
# Edit src/components/FormPage.tsx
```

### Making Changes to Agent

```bash
cd backend
uv run python Vision.py dev  # Auto-reloads
# Edit Vision.py
```

### Making Changes to Backend API

```bash
uv run uvicorn server:app --reload  # Auto-reloads
# Edit server.py
```

---

## 📚 Key Files Reference

| File              | Purpose           | Location                       |
| ----------------- | ----------------- | ------------------------------ |
| `FormPage.tsx`    | Form UI component | `src/components/`              |
| `server.py`       | FastAPI server    | `backend/`                     |
| `Vision.py`       | AI Agent logic    | `backend/`                     |
| `pdf_generate.py` | PDF rendering     | `backend/`                     |
| `.env.local`      | Configuration     | Frontend root & backend folder |

---

## 🚀 Production Deployment

To deploy live:

1. **Frontend**: Push to Vercel
2. **Backend**: Deploy to Railway/Render
3. **Agent**: Run on VPS with Live Kit
4. **Update URLs in .env**

---

## ✨ You're All Set!

All dependencies installed ✅
All files organized ✅
All environments configured ✅

**Run this to start everything:**

```bash
cd /Users/y4l1/Documents/GDGJP-Hackathon/ai-privacy-amanuensis
./start-all.sh
```

Then visit: **http://localhost:3001/form** 🎉

---

**Questions?** Check the README.md or INTEGRATION_DEMO.md
