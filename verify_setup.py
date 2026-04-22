#!/usr/bin/env python3
"""
Quick validation script to check if the AI Scheduler project is properly set up.
Run from the backend directory: python verify_setup.py
"""

import os
import sys
from pathlib import Path

def check_file_exists(path, description):
    """Check if a file exists and print result"""
    exists = Path(path).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def check_directory_exists(path, description):
    """Check if a directory exists and print result"""
    exists = Path(path).is_dir()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def main():
    print("\n" + "="*60)
    print("AI SCHEDULER - PROJECT VERIFICATION")
    print("="*60 + "\n")
    
    all_good = True
    
    # Check backend structure
    print("📁 Checking Backend Structure...")
    checks = [
        ("backend/main.py", "Main FastAPI app"),
        ("backend/models.py", "Data models"),
        ("backend/requirements.txt", "Python dependencies"),
        ("backend/.env.example", "Environment template"),
        ("backend/services/pdf_parser.py", "PDF parser"),
        ("backend/services/gemini_scheduler.py", "Gemini scheduler"),
        ("backend/services/calendar_service.py", "Calendar service"),
        ("backend/services/exporters.py", "Export service"),
        ("backend/services/__init__.py", "Services package init"),
    ]
    
    for path, desc in checks:
        if not check_file_exists(path, desc):
            all_good = False
    
    print("\n📁 Checking Frontend Structure...")
    checks = [
        ("frontend/package.json", "NPM package config"),
        ("frontend/vite.config.js", "Vite config"),
        ("frontend/index.html", "HTML entry point"),
        ("frontend/src/main.jsx", "React entry point"),
        ("frontend/src/App.jsx", "App component"),
        ("frontend/src/index.css", "Global styles"),
        ("frontend/src/api/client.js", "API client"),
        ("frontend/src/pages/Upload.jsx", "Upload page"),
        ("frontend/src/pages/Calendar.jsx", "Calendar page"),
        ("frontend/src/pages/Schedule.jsx", "Schedule page"),
        ("frontend/src/pages/Export.jsx", "Export page"),
    ]
    
    for path, desc in checks:
        if not check_file_exists(path, desc):
            all_good = False
    
    print("\n📁 Checking Documentation...")
    checks = [
        ("README.md", "Main documentation"),
        ("QUICKSTART.md", "Quick start guide"),
        ("ARCHITECTURE.md", "Architecture docs"),
        ("PROJECT_OVERVIEW.md", "Project overview"),
    ]
    
    for path, desc in checks:
        if not check_file_exists(path, desc):
            all_good = False
    
    print("\n📁 Checking Root Files...")
    checks = [
        (".gitignore", "Git ignore file"),
    ]
    
    for path, desc in checks:
        if not check_file_exists(path, desc):
            all_good = False
    
    # Check environment
    print("\n🔧 Checking Environment...")
    
    # Check if .env exists
    env_exists = Path("backend/.env").exists()
    if env_exists:
        print("✅ backend/.env exists (good)")
    else:
        print("⚠️  backend/.env not found")
        print("   👉 Run: copy backend/.env.example backend/.env")
        print("   👉 Then add your GOOGLE_API_KEY")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f"✅ Python version: {python_version.major}.{python_version.minor} (good)")
    else:
        print(f"❌ Python version: {python_version.major}.{python_version.minor} (needs 3.8+)")
        all_good = False
    
    # Check if venv exists
    venv_exists = Path("backend/venv").exists() or Path("backend/.venv").exists()
    if venv_exists:
        print("✅ Python virtual environment detected")
    else:
        print("⚠️  No virtual environment detected")
        print("   👉 Run: python -m venv backend/venv")
        print("   👉 Then: venv\\Scripts\\activate (Windows)")
    
    print("\n" + "="*60)
    if all_good:
        print("✅ ALL CHECKS PASSED!")
        print("\n🚀 Next Steps:")
        print("   1. Set up .env with your API keys")
        print("   2. cd backend && pip install -r requirements.txt")
        print("   3. python main.py  # Start backend")
        print("   4. cd frontend && npm install")
        print("   5. npm run dev  # Start frontend")
        print("   6. Open http://localhost:5173 in your browser")
    else:
        print("⚠️  Some checks failed. Please review above.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
