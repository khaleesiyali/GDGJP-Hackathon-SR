# 🚀 QUICK START CARD

## 🎯 RUN THE SYSTEM IN 3 SECONDS

```bash
cd /Users/y4l1/Documents/GDGJP-Hackathon/ai-privacy-amanuensis
./start-all.sh
```

Then visit: **http://localhost:3001/form**

---

## ✅ What's Installed

| Component | Status | Version   |
| --------- | ------ | --------- |
| Node.js   | ✅     | v22.15.0  |
| npm       | ✅     | 10.9.2    |
| Python    | ✅     | 3.9.6     |
| uv        | ✅     | Installed |
| Next.js   | ✅     | 16.1.6    |
| React     | ✅     | 19.2.3    |
| FastAPI   | ✅     | 0.135.1   |
| LiveKit   | ✅     | 1.1.2     |
| OpenAI    | ✅     | 2.28.0    |
| Vision.py | ✅     | Ready     |

---

## 📍 3 Ways to Start

### Option 1: Everything

```bash
./start-all.sh
```

### Option 2: Manual (3 terminals)

```bash
# Terminal 1
uv run uvicorn server:app --reload

# Terminal 2
uv run python Vision.py dev

# Terminal 3
npm run dev
```

### Option 3: Backend Only

```bash
./start-backend-agent.sh
```

---

## 🌐 Access Points

| Service  | URL                        |
| -------- | -------------------------- |
| **Form** | http://localhost:3001/form |
| **Home** | http://localhost:3001      |
| **API**  | http://localhost:8000      |
| **Docs** | http://localhost:8000/docs |

---

## 🎨 Components Running

```
🎨 Frontend      → http://localhost:3001
📡 Backend API   → http://localhost:8000
🧠 Vision Agent  → Connected to LiveKit
```

---

## 🧪 Quick Tests

```bash
# Test backend
curl http://localhost:8000/get_token?room_name=test&participant_name=demo

# Test frontend
curl http://localhost:3001/form

# Verify setup
./verify-setup.sh
```

---

## 🛑 Stop Everything

```bash
pkill -f "npm|next|uvicorn|Vision"
```

---

## 🔑 Key Files

```
Frontend:      src/components/FormPage.tsx
Backend API:   backend/server.py
AI Agent:      backend/Vision.py
Configuration: .env.local (both locations)
```

---

## 🐛 Common Issues

| Problem              | Fix                         |
| -------------------- | --------------------------- |
| Port 3001 in use     | `pkill -f npm`              |
| Port 8000 in use     | `pkill -f uvicorn`          |
| Agent not connecting | Check .env.local in backend |
| No voice             | Check microphone/speakers   |

---

## 📊 System Status

✅ **ALL INSTALLED**
✅ **ALL CONFIGURED**  
✅ **ALL READY**

---

## 🎬 Get Started Now!

```bash
./start-all.sh
```

Visit: **http://localhost:3001/form** 🚀

---

For detailed info, see:

- **SETUP_AND_RUN.md** - Full guide
- **READY_TO_RUN.md** - Detailed summary
- **INSTALLATION_COMPLETE.md** - This installation
