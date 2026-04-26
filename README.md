# 🛡️ AI Digital Safety Shield

> Protecting women and children from online threats in real-time using AI.

**EliteHer Hackathon Submission**

---

## 🔗 Submission Links

| 🔗 Link Type | URL |
|-------------|-----|
| 🌐 Live Demo | https://clever-torte-52c285.netlify.app/ |
| 🧠 GitHub Repo | https://github.com/vaishnavitrathod/safety-shield-backend |
| ⚙️ Backend API | https://safety-shield-backend.onrender.com |

---
## 📸 Demo Preview
![App Screenshot](your-image-link)

## 💡 Idea Title
**AI Digital Safety Shield** — Real-time threat detection and emergency response for women's online safety.

---

## 📋 Idea Description

Every day, millions of women and children face grooming, manipulation, stalking, blackmail and physical threats through online messaging platforms. Most victims don't recognise the danger until it's too late — this is the **Awareness Gap**.

AI Digital Safety Shield is a real-time AI-powered safety layer that:
- **Detects threats** in chat messages as they arrive
- **Classifies the threat type** (grooming, stalking, blackmail, physical threat, etc.)
- **Alerts the user immediately** with a risk score and recommended actions
- **Connects to emergency services** (Police 100, Women's Helpline 1091, Ambulance 108) with one tap
- **Educates users** on why a message is dangerous and what tactic is being used

---

## ⚙️ Technical Details

### Technologies Used
- **Frontend:** HTML5, CSS3, Vanilla JavaScript, Chart.js
- **Backend:** Python, Flask, Flask-CORS, Gunicorn
- **AI / ML:** Anthropic Claude API (claude-sonnet-4-20250514) for intent analysis
- **Pattern Matching:** Custom regex engine for instant local threat detection (no API cost)
- **Deployment:** Netlify (frontend) + Render (backend)

### Architecture Overview

```
User types message
       ↓
[Frontend - index.html]
       ↓
Stage 1: Regex pre-check (instant, local)
       ↓ (if not HIGH confidence)
Stage 2: Flask API → Claude AI (deep intent analysis)
       ↓
Result: level (HIGH/MEDIUM/LOW) + threat_type + score + reasons
       ↓
UI updates: threat alert, risk score ring, dashboard stats
       ↓ (if HIGH)
Emergency Modal → One-tap call to Police/Helpline/Ambulance
```

### Database Used
- Stateless architecture for fast, scalable threat analysis
- No persistent storage → ensures user privacy

### Third-Party Integrations
| Service | Purpose |
|---|---|
| Anthropic Claude API | AI-powered threat intent classification |
| Render.com | Flask backend hosting |
| Netlify | Frontend hosting |
| Chart.js | Risk trend visualisation |

---

## 🚀 Key Features

1. **Real-time threat detection** — Regex + AI two-stage pipeline
2. **Threat classification** — 7 categories: grooming, manipulation, stalking, physical threat, location extraction, blackmail, SOS distress
3. **Risk scoring** — Dynamic 0–100% fake/threat score with visual ring
4. **Emergency response** — One-tap calls to Police (100), Women's Helpline (1091), Ambulance (108) with auto-call countdown
5. **AI Simulation Mode** — Toggle to send last 4 messages as context for behavioural pattern detection
6. **"Why was this flagged?"** — Explains the specific tactic used, educating the user
7. **Unified Intel** — Fake profile analysis with IP mismatch, account age, AI-generated photo detection
8. **Cross-platform** — Shield active indicator for WhatsApp, Instagram, Telegram, SMS
9. **Select-to-scan** — Highlight any text on screen to instantly analyze it with AI

---

## 🎯 Real Use-Case Scenario

> A 16-year-old receives: *"Don't tell your parents about us, send me some pics"*

1. Shield detects **grooming pattern** instantly
2. Risk score jumps to **82%**
3. Alert appears: *"Grooming behaviour detected"*
4. User taps **"Why was this flagged?"** → learns about isolation + photo-request tactics
5. Emergency modal offers **Women's Helpline 1091** with one tap
6. Dashboard logs the threat for pattern tracking

---

## 👩‍💻 Running Locally

```bash
# Backend
pip install -r requirements.txt
cp .env.example .env   # add ANTHROPIC_API_KEY
python app.py          # starts on http://localhost:5000

# Frontend
# Just open index.html in your browser
```

---

## 👥 Team
**Zenith Crew — EliteHer Hackathon 2026**

- Vaishnavi T (Team Lead)
- Fiona Diya D'Souza
- Nitya D Naik
