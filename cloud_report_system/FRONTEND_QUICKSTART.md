# 🛡️ CyberGuard AI - Quick Reference

## 🚀 Start in 5 Seconds

### Windows
```bash
python startup.py
# or
start.bat
```

### Linux/macOS
```bash
python3 startup.py
# or
bash start.sh
```

**Browser opens automatically to:** `http://localhost:8501`

---

## 📱 What You Get

### ChatGPT-Like Agent Interface
- 💬 Natural conversation with AI agent
- 🤖 Shows thinking animation while processing
- 📊 Real-time classification results
- ❓ Intelligent follow-up questions
- 📋 Professional JSON reports
- 📥 Download reports as files

### Multi-Layer Architecture
```
User Chat Interface (Streamlit)
       ↓
Crime Classification (AI)
       ↓
Smart Question Generation
       ↓
Report Generation + Correlation
```

---

## ⚡ Quick Workflow

1. **Describe** → "I got a suspicious email asking for banking credentials"
2. **Agent Identifies** → "PHISHING (95% confidence)"
3. **Agent Asks** → 5-7 targeted clarifying questions
4. **You Answer** → Respond to all questions
5. **Report Generated** → Professional crime report with recommendations
6. **Export** → Download as JSON or copy to clipboard

---

## 🎯 Supported Crime Types

Phishing | Ransomware | Data Breach | Identity Theft | Fraud | Malware | DDoS | Hacking | Extortion | Spam

---

## 🔗 Key URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:8501 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## 📚 Documentation

- **Getting Started**: FRONTEND_DEPLOYMENT_GUIDE.md
- **User Guide**: FRONTEND_USER_GUIDE.md
- **Architecture**: ARCHITECTURE.md
- **API Testing**: API_TESTING_GUIDE.md
- **Quick Start**: QUICKSTART.md

---

## ⚙️ Manual Startup (If Needed)

### Terminal 1: Backend
```bash
python main.py
```

### Terminal 2: Frontend
```bash
streamlit run ui.py
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Port already in use | Kill existing process using port 8000/8501 |
| Dependencies missing | `pip install -r requirements.txt` |
| API won't connect | Ensure backend is running on port 8000 |
| Browser won't open | Manually visit http://localhost:8501 |

---

## ✅ Features Overview

✅ Agent-driven chat interface (ChatGPT-like)  
✅ Real-time crime classification  
✅ Smart question generation (crime-specific)  
✅ Professional report generation  
✅ Case correlation analysis  
✅ Report export (JSON)  
✅ Session management with case IDs  
✅ Progress tracking  
✅ Multi-layer architecture visualization  
✅ Cross-platform (Windows/Linux/macOS)  

---

## 🎓 Example Incident to Try

### Phishing Example
```
"I received an email from my bank asking me to verify my account. 
The email had the correct logo and looked official, but when I clicked 
the link, it took me to a fake website that looked like my bank. 
I entered my username and password before realizing it wasn't real. 
Now I'm worried they might have my credentials."
```

**Expected System Response:**
1. ✅ Classified as PHISHING (95%+ confidence)
2. 💭 Asks about: Email sender, link details, credentials used, date received
3. 📋 Generates report with: Impact assessment, recommendations, related cases
4. 💾 Allows download for authorities

---

## 📱 What's Running

### Backend (Port 8000)
- FastAPI server
- Crime classification engine
- Question generation
- Report generation with correlation
- Case database

### Frontend (Port 8501)
- Streamlit web interface
- Chat-based user interaction
- Multi-stage workflow
- Progress tracking
- Report display & export

---

## 🔒 Data Security

- ✅ All processing on local machine
- ✅ No cloud storage by default
- ✅ HTTPS recommended for production
- ✅ Authentication can be added
- ✅ Reports can be encrypted

---

## 📊 Report Contents

Each generated report includes:
- **Case Details**: ID, timestamp, crime type
- **Incident Information**: All user-provided details
- **Classification Data**: Confidence scores, reasoning
- **Correlated Cases**: Similar previous incidents
- **Recommendations**: Investigation steps, preventive measures
- **Evidence**: Contact info, file patterns, amounts involved

---

## 💡 Pro Tips

1. **Be Detailed** → More info = Better classification & questions
2. **Answer All** → Answer every question for complete report
3. **Check Correlation** → Review correlated cases for patterns
4. **Save Reports** → Download JSON for your records
5. **Share Case ID** → Use case ID when contacting authorities

---

## 🆘 Need Help?

1. **Check Logs**: Look at terminal output from `python startup.py`
2. **API Status**: Visit http://localhost:8000/docs
3. **Read Docs**: Open FRONTEND_USER_GUIDE.md
4. **Test API**: Use Swagger UI at /docs endpoint

---

## 📞 Supported Scenarios

✅ Personal account compromises  
✅ Business data breaches  
✅ Ransomware attacks  
✅ Network intrusions  
✅ Financial fraud  
✅ Identity theft  
✅ DDoS attacks  
✅ Malware infections  
✅ Extortion threats  
✅ Email compromises  

---

## 🎯 Next Steps

1. **Start the system** → `python startup.py`
2. **Open browser** → http://localhost:8501 (auto-opens)
3. **Describe your incident** → Be as detailed as possible
4. **Follow the agent** → Answer all questions
5. **Review report** → Check generated crime report
6. **Export data** → Download JSON for authorities/records

---

**Status**: 🟢 Ready to Use  
**Version**: CyberGuard AI 1.0  
**Last Updated**: 2026-03-09

Enjoy secure crime reporting! 🛡️
