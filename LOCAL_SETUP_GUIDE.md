# 🏥 Local Setup Guide - AI Health Monitoring System

## What This Project Is
This is an AI-powered health monitoring platform that allows users to:
- Track daily symptoms and get AI-powered health predictions
- Monitor vitals and receive risk assessments
- Access environmental health data
- Contribute to public health surveillance (privacy-preserving)

## 📋 Prerequisites

### 1. System Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Python**: Version 3.8 or higher
- **RAM**: Minimum 4GB (8GB recommended for ML models)
- **Storage**: At least 2GB free space
- **Internet**: Required for initial setup and environmental data

### 2. Required Software
- **Python 3.8+**: Download from [python.org](https://python.org)
- **Git**: Download from [git-scm.com](https://git-scm.com)
- **Web Browser**: Chrome, Firefox, Safari, or Edge

### 3. Optional (for enhanced performance)
- **Redis**: For caching (improves performance)
- **PostgreSQL**: For production database (SQLite used by default)

## 🚀 Step-by-Step Setup

### Step 1: Clone the Repository
```bash
# If you have the repository URL
git clone <repository-url>
cd ai-health-monitor

# If you're already in the project directory, skip this step
```

### Step 2: Create Python Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Download spaCy language model (required for NLP)
python -m spacy download en_core_web_sm
```

### Step 4: Environment Configuration
```bash
# The system will create a .env file automatically
# Or you can create it manually with these contents:
echo "FLASK_ENV=development
SECRET_KEY=development-key-change-in-production
JWT_SECRET_KEY=jwt-development-key" > .env
```

### Step 5: Run the Application
```bash
# Simple method - use the startup script
python run.py

# This will:
# ✅ Check dependencies
# ✅ Setup environment
# ✅ Train AI models
# ✅ Start backend server
# ✅ Open frontend in browser
```

### Alternative: Manual Startup
```bash
# Start backend server manually
cd backend
python app.py

# In another terminal, serve frontend
cd frontend/public
python -m http.server 8000
```

## 🌐 Accessing the Application

Once running, you can access:
- **Frontend**: http://localhost:8000 (or opens automatically)
- **Backend API**: http://localhost:5000/api
- **Health Check**: http://localhost:5000/health
- **API Documentation**: http://localhost:5000/api

## 👤 Getting Started

### Default Admin Account
- **Email**: admin@healthmonitor.com
- **Password**: admin123

### First-Time Setup
1. **Register**: Create your personal health account
2. **Profile**: Complete your health profile
3. **Symptoms**: Report symptoms using natural language
4. **Vitals**: Record blood pressure, weight, etc.
5. **Analysis**: Get AI-powered health predictions

## 🔧 Common Issues & Solutions

### Issue 1: Python Version
```bash
# Check Python version
python --version

# If less than 3.8, install newer Python
# Then use specific version:
python3.8 -m venv venv
```

### Issue 2: Missing Dependencies
```bash
# If pip install fails, try:
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir

# For specific packages:
pip install flask scikit-learn pandas numpy
```

### Issue 3: spaCy Model Not Found
```bash
# Download the language model
python -m spacy download en_core_web_sm

# If still fails, try:
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.6.0/en_core_web_sm-3.6.0.tar.gz
```

### Issue 4: Port Already in Use
```bash
# If port 5000 is busy, change it in backend/app.py:
# app.run(host='0.0.0.0', port=5001, debug=True)

# Or kill existing process:
# Windows: netstat -ano | findstr :5000
# macOS/Linux: lsof -ti:5000 | xargs kill
```

### Issue 5: ML Models Not Training
```bash
# If models fail to train automatically:
cd backend
python -c "
from ml_models.nlp.symptom_classifier import SymptomClassifier
from ml_models.numerical.risk_predictor import HealthRiskPredictor
classifier = SymptomClassifier()
classifier.train()
predictor = HealthRiskPredictor()
predictor.train()
"
```

## 📱 Usage Features

### Personal Health Tracking
- **Symptom Reporting**: "I have a headache and feel nauseous"
- **Vital Signs**: Blood pressure, heart rate, weight tracking
- **Risk Assessment**: AI-powered health risk predictions
- **Environmental Data**: Air quality and weather impacts

### AI Features
- **Natural Language Processing**: Understands symptom descriptions
- **Predictive Analytics**: Risk assessment for various conditions
- **Personalized Recommendations**: Health advice based on your data
- **Trend Analysis**: Track health patterns over time

### Public Health (Admin)
- **Dashboard**: Aggregated health trends
- **Outbreak Detection**: Early warning systems
- **Environmental Correlations**: Health-environment relationships

## 🔒 Privacy & Security

- **Local Data**: All personal data stored locally by default
- **Encryption**: Data encrypted at rest and in transit
- **Privacy-First**: No personal data shared without consent
- **GDPR/HIPAA**: Compliant with health data regulations

## 📊 System Architecture

```
Frontend (HTML/CSS/JS) → Backend (Flask API) → ML Models (Scikit-learn/spaCy)
                                            ↓
                                      Database (SQLite)
```

## 🚀 Production Deployment

For production use:
1. **Change Environment**: Set `FLASK_ENV=production`
2. **Use PostgreSQL**: Replace SQLite with PostgreSQL
3. **Add Redis**: For caching and performance
4. **SSL/TLS**: Use HTTPS with proper certificates
5. **Reverse Proxy**: Use Nginx or Apache

## 🆘 Getting Help

### Check Logs
```bash
# Backend logs appear in terminal
# Check for error messages during startup

# Database issues:
cd backend
python -c "from app import db; db.create_all(); print('Database created')"
```

### Test API
```bash
# Test if backend is running
curl http://localhost:5000/health

# Test registration
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123","first_name":"Test","last_name":"User"}'
```

### Verify Dependencies
```bash
# Check critical packages
python -c "
import flask, sklearn, pandas, numpy, spacy
print('All dependencies OK')
"
```

## 📈 Performance Tips

1. **Use SSD**: Store project on SSD for faster model loading
2. **RAM**: 8GB+ recommended for ML model training
3. **Redis**: Install Redis for caching (optional but recommended)
4. **GPU**: CUDA-compatible GPU for faster deep learning (optional)

## 🔮 Next Steps

After successful setup:
1. **Explore API**: Test different endpoints
2. **Customize Models**: Retrain with your data
3. **Add Features**: Extend functionality
4. **Deploy**: Move to production environment
5. **Integrate**: Connect with wearables/IoT devices

## 📞 Support

If you encounter issues:
1. Check the error messages in terminal
2. Verify all dependencies are installed
3. Ensure Python 3.8+ is being used
4. Check if ports 5000 and 8000 are available
5. Review the requirements.txt for any missing packages

---

**Author**: Tafirenyika Shoniwa  
**Email**: tafirenyika.shoniwa@icloud.com  
**Project**: AI-Powered Health Monitoring System

*Built with ❤️ for better health outcomes through AI innovation*