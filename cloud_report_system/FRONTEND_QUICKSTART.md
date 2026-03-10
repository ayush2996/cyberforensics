# 🛡️ CYBERCRIME REPORT GENERATION SYSTEM - Quick Start

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

### Professional Law Enforcement Interface
- 📋 Structured incident documentation
- ✅ Real-time field validation
- 🔍 Crime type automatic classification
- ❓ Systematic questioning for evidence collection
- 📄 Professional complaint form generation
- 📥 Export as TXT (print-ready) or JSON (database storage)

### System Workflow
```
Officer Describes Incident
       ↓
System Classifies Crime Type
       ↓
Systematic Data Collection with Validation
       ↓
Professional Complaint Form Generation
       ↓
Export & Case Linking
```

---

## ⚡ Quick Workflow

1. **Enter Incident** → Describe the cybercrime incident
2. **System Classifies** → Determines crime type automatically
3. **Answer Questions** → Respond to crime-specific data collection
4. **System Validates** → Confirms all data in correct format
5. **Report Generated** → Professional official complaint form
6. **Export** → Download as TXT (print) or JSON (database)

---

## 🎯 Supported Crime Types

**Phishing** • **Ransomware** • **Data Breach** • **Identity Theft** • **Fraud** 
**Malware** • **DDoS** • **Hacking** • **Extortion** • **Spam**

---

## ✅ Field Validation

System validates all fields in real-time:

| Field Type | Example Valid | Example Invalid |
|-----------|---------------|-----------------|
| Email | ayush@gmail.com | ayush |
| Phone | +91-9876543210 | 123 |
| Date | 2024-03-10 | tomorrow |
| Amount | 50000 or $50,000 | lots |
| URL | https://example.com | example.com |

---

## 🔗 Key URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:8501 |
| Backend API | http://localhost:8000 |
| API Documentation | http://localhost:8000/docs |

---

## 📚 Documentation

- **Detailed Guide**: FRONTEND_USER_GUIDE.md
- **Deployment**: FRONTEND_DEPLOYMENT_GUIDE.md
- **Architecture**: ARCHITECTURE.md
- **Field Validation**: VALIDATION_GUIDE.md
- **Implementation**: IMPLEMENTATION_GUIDE.md

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
