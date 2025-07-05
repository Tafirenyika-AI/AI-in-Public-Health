#!/usr/bin/env python3
"""
AI Health Monitoring System - Startup Script
Author: Tafirenyika Shoniwa

This script initializes and runs the AI-powered health monitoring system.
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import flask
        import sklearn
        import pandas
        import numpy
        print("✅ Core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def setup_environment():
    """Set up environment variables."""
    if not os.path.exists('.env'):
        print("📝 Creating .env file from template...")
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("✅ .env file created. Please edit it with your configuration.")
        else:
            # Create basic .env file
            with open('.env', 'w') as f:
                f.write("FLASK_ENV=development\n")
                f.write("SECRET_KEY=development-key-change-in-production\n")
                f.write("JWT_SECRET_KEY=jwt-development-key\n")
            print("✅ Basic .env file created.")

def initialize_ml_models():
    """Initialize and train ML models if needed."""
    print("🤖 Initializing AI models...")
    try:
        # Import and initialize models
        sys.path.append('backend')
        from ml_models.nlp.symptom_classifier import SymptomClassifier
        from ml_models.numerical.risk_predictor import HealthRiskPredictor
        
        # Initialize symptom classifier
        print("Training symptom classifier...")
        classifier = SymptomClassifier()
        if not classifier.is_trained:
            classifier.train()
            classifier.save_model("ml_models/nlp/trained_symptom_classifier.pkl")
        
        # Initialize risk predictor
        print("Training risk predictor...")
        predictor = HealthRiskPredictor()
        if not predictor.is_trained:
            predictor.train()
            predictor.save_model("ml_models/numerical/trained_risk_predictor.pkl")
        
        print("✅ AI models initialized successfully")
        return True
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize models: {e}")
        print("Models will be trained on first API call.")
        return False

def start_backend():
    """Start the Flask backend server."""
    print("🚀 Starting backend server...")
    os.chdir('backend')
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_APP'] = 'app.py'
    
    try:
        # Import and run the Flask app
        from app import app
        print("✅ Backend server starting on http://localhost:5000")
        print("📊 API documentation available at http://localhost:5000/api")
        print("🏥 Health check: http://localhost:5000/health")
        
        # Start the Flask app
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
        
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return False

def open_frontend():
    """Open the frontend in the default web browser."""
    frontend_path = Path("frontend/public/index.html").absolute()
    if frontend_path.exists():
        frontend_url = f"file://{frontend_path}"
        print(f"🌐 Opening frontend: {frontend_url}")
        webbrowser.open(frontend_url)
    else:
        print("❌ Frontend file not found")

def main():
    """Main function to run the health monitoring system."""
    print("🏥 AI-Powered Health Monitoring System")
    print("=====================================")
    print("Author: Tafirenyika Shoniwa")
    print()
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Setup environment
    setup_environment()
    
    # Initialize ML models
    initialize_ml_models()
    
    # Open frontend
    open_frontend()
    
    print()
    print("🔧 System Configuration:")
    print("   - Backend: Flask REST API on port 5000")
    print("   - Frontend: Static HTML/CSS/JS")
    print("   - Database: SQLite (development)")
    print("   - ML Models: Scikit-learn + spaCy")
    print()
    
    print("📱 Usage Instructions:")
    print("   1. Register a new account or login")
    print("   2. Complete your health profile")
    print("   3. Report symptoms and record vitals")
    print("   4. Get AI-powered health predictions")
    print("   5. View environmental health data")
    print()
    
    print("🔑 Default Admin Account:")
    print("   Email: admin@healthmonitor.com")
    print("   Password: admin123")
    print()
    
    # Start backend server
    print("Press Ctrl+C to stop the server")
    print("="*50)
    
    try:
        start_backend()
    except KeyboardInterrupt:
        print("\n👋 Shutting down health monitoring system...")
        print("Thank you for using AI Health Monitor!")

if __name__ == "__main__":
    main()