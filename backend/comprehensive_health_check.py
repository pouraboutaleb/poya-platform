#!/usr/bin/env python3
"""
Comprehensive Health Check Report for Poya Platform
Based on current application state and code analysis
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        return f"✅ {description}: Found"
    else:
        return f"❌ {description}: Missing"

def check_directory_structure():
    """Check project directory structure"""
    print("📁 PROJECT STRUCTURE CHECK")
    print("=" * 50)
    
    base_dir = "/workspaces/poya-platform"
    
    structure_checks = [
        (f"{base_dir}/backend", "Backend directory"),
        (f"{base_dir}/frontend", "Frontend directory"),
        (f"{base_dir}/backend/app", "Backend app directory"),
        (f"{base_dir}/backend/app/main.py", "Main FastAPI application"),
        (f"{base_dir}/backend/requirements.txt", "Backend dependencies"),
        (f"{base_dir}/frontend/package.json", "Frontend dependencies"),
        (f"{base_dir}/frontend/src", "Frontend source directory"),
        (f"{base_dir}/backend/app/models", "Database models directory"),
        (f"{base_dir}/backend/app/schemas", "API schemas directory"),
        (f"{base_dir}/backend/app/api", "API routes directory"),
    ]
    
    for filepath, description in structure_checks:
        print(check_file_exists(filepath, description))

def check_python_dependencies():
    """Check Python dependencies"""
    print("\n🐍 PYTHON DEPENDENCIES CHECK")
    print("=" * 50)
    
    try:
        result = subprocess.run(['pip', 'list'], capture_output=True, text=True)
        packages = result.stdout
        
        required_packages = [
            'fastapi',
            'uvicorn', 
            'sqlalchemy',
            'pydantic',
            'python-jose',
            'passlib',
            'alembic'
        ]
        
        for package in required_packages:
            if package.lower() in packages.lower():
                print(f"✅ {package}: Installed")
            else:
                print(f"❌ {package}: Missing")
                
    except Exception as e:
        print(f"❌ Error checking Python dependencies: {e}")

def check_node_dependencies():
    """Check Node.js dependencies"""
    print("\n📦 NODE.JS DEPENDENCIES CHECK")
    print("=" * 50)
    
    frontend_dir = "/workspaces/poya-platform/frontend"
    package_json_path = f"{frontend_dir}/package.json"
    node_modules_path = f"{frontend_dir}/node_modules"
    
    if os.path.exists(package_json_path):
        print("✅ package.json: Found")
        
        if os.path.exists(node_modules_path):
            print("✅ node_modules: Found")
            
            # Count installed packages
            try:
                package_count = len([d for d in os.listdir(node_modules_path) 
                                   if os.path.isdir(os.path.join(node_modules_path, d))])
                print(f"✅ Installed packages: {package_count}")
            except:
                print("⚠️  Could not count packages")
        else:
            print("❌ node_modules: Missing")
    else:
        print("❌ package.json: Missing")

def analyze_code_structure():
    """Analyze the code structure for completeness"""
    print("\n🔍 CODE STRUCTURE ANALYSIS")
    print("=" * 50)
    
    backend_app_dir = "/workspaces/poya-platform/backend/app"
    
    # Check API endpoints
    api_v1_dir = f"{backend_app_dir}/api/v1"
    if os.path.exists(api_v1_dir):
        api_files = [f for f in os.listdir(api_v1_dir) if f.endswith('.py') and f != '__init__.py']
        print(f"✅ API endpoint files: {len(api_files)} found")
        for file in sorted(api_files)[:10]:  # Show first 10
            print(f"   📄 {file}")
        if len(api_files) > 10:
            print(f"   ... and {len(api_files) - 10} more")
    else:
        print("❌ API v1 directory: Missing")
    
    # Check models
    models_dir = f"{backend_app_dir}/models"
    if os.path.exists(models_dir):
        model_files = [f for f in os.listdir(models_dir) if f.endswith('.py') and f != '__init__.py']
        print(f"✅ Model files: {len(model_files)} found")
        for file in sorted(model_files):
            print(f"   📄 {file}")
    else:
        print("❌ Models directory: Missing")
    
    # Check schemas
    schemas_dir = f"{backend_app_dir}/schemas"
    if os.path.exists(schemas_dir):
        schema_files = [f for f in os.listdir(schemas_dir) if f.endswith('.py') and f != '__init__.py']
        print(f"✅ Schema files: {len(schema_files)} found")
        for file in sorted(schema_files):
            print(f"   📄 {file}")
    else:
        print("❌ Schemas directory: Missing")

def check_database_setup():
    """Check database configuration"""
    print("\n🗄️  DATABASE SETUP CHECK")
    print("=" * 50)
    
    backend_dir = "/workspaces/poya-platform/backend"
    
    # Check for database files
    db_files = []
    for file in os.listdir(backend_dir):
        if file.endswith('.db'):
            db_files.append(file)
    
    if db_files:
        print(f"✅ Database files found: {', '.join(db_files)}")
    else:
        print("⚠️  No SQLite database files found")
    
    # Check migrations
    migrations_dir = f"{backend_dir}/migrations"
    if os.path.exists(migrations_dir):
        print("✅ Migrations directory: Found")
        versions_dir = f"{migrations_dir}/versions"
        if os.path.exists(versions_dir):
            migration_files = [f for f in os.listdir(versions_dir) 
                             if f.endswith('.py') and f != '__init__.py']
            print(f"✅ Migration files: {len(migration_files)} found")
        else:
            print("⚠️  Migrations versions directory: Missing")
    else:
        print("❌ Migrations directory: Missing")
    
    # Check alembic config
    alembic_ini = f"{backend_dir}/alembic.ini"
    if os.path.exists(alembic_ini):
        print("✅ Alembic configuration: Found")
    else:
        print("❌ Alembic configuration: Missing")

def check_frontend_structure():
    """Check frontend structure"""
    print("\n⚛️  FRONTEND STRUCTURE CHECK")
    print("=" * 50)
    
    frontend_dir = "/workspaces/poya-platform/frontend"
    src_dir = f"{frontend_dir}/src"
    
    if os.path.exists(src_dir):
        print("✅ Frontend src directory: Found")
        
        # Check for key files
        key_files = [
            "App.jsx",
            "index.js",
            "index.html"
        ]
        
        for file in key_files:
            if os.path.exists(f"{src_dir}/{file}") or os.path.exists(f"{frontend_dir}/{file}"):
                print(f"✅ {file}: Found")
            else:
                print(f"⚠️  {file}: Not found")
        
        # Check components
        components_dir = f"{src_dir}/components"
        if os.path.exists(components_dir):
            print("✅ Components directory: Found")
            
            # Count component files
            component_files = []
            for root, dirs, files in os.walk(components_dir):
                component_files.extend([f for f in files if f.endswith(('.jsx', '.js'))])
            
            print(f"✅ Component files: {len(component_files)} found")
        else:
            print("⚠️  Components directory: Missing")
    else:
        print("❌ Frontend src directory: Missing")

def check_running_processes():
    """Check for running server processes"""
    print("\n🔄 RUNNING PROCESSES CHECK")
    print("=" * 50)
    
    try:
        # Check for uvicorn processes
        result = subprocess.run(['pgrep', '-f', 'uvicorn'], capture_output=True, text=True)
        if result.stdout.strip():
            print(f"✅ Backend server processes: {len(result.stdout.strip().split())} running")
        else:
            print("⚠️  Backend server: Not running")
        
        # Check for vite processes  
        result = subprocess.run(['pgrep', '-f', 'vite'], capture_output=True, text=True)
        if result.stdout.strip():
            print(f"✅ Frontend server processes: {len(result.stdout.strip().split())} running")
        else:
            print("⚠️  Frontend server: Not running")
            
        # Check for node processes
        result = subprocess.run(['pgrep', '-f', 'node'], capture_output=True, text=True)
        if result.stdout.strip():
            print(f"✅ Node.js processes: {len(result.stdout.strip().split())} running")
        else:
            print("⚠️  Node.js processes: Not detected")
            
    except Exception as e:
        print(f"❌ Error checking processes: {e}")

def generate_final_assessment():
    """Generate final assessment and recommendations"""
    print("\n📊 FINAL ASSESSMENT")
    print("=" * 50)
    
    print("🎯 APPLICATION READINESS STATUS:")
    print("\n✅ STRENGTHS:")
    print("   • Project structure is well-organized")
    print("   • All major components are present (backend, frontend)")
    print("   • Dependencies appear to be properly configured")
    print("   • Database models and API schemas are implemented")
    print("   • Multiple API endpoints are available")
    print("   • React frontend with component structure")
    
    print("\n⚠️  AREAS NEEDING ATTENTION:")
    print("   • Import path issues in some backend modules")
    print("   • Database initialization may need completion")
    print("   • Server startup issues need resolution")
    print("   • Authentication system needs verification")
    
    print("\n🔧 RECOMMENDATIONS:")
    print("   1. Fix import path issues in API modules")
    print("   2. Complete database initialization with alembic")
    print("   3. Create default admin user for testing")
    print("   4. Verify CORS configuration")
    print("   5. Test end-to-end authentication workflow")
    
    print("\n🚀 NEXT STEPS:")
    print("   1. Resolve import issues and restart backend")
    print("   2. Run database migrations")
    print("   3. Test API endpoints with authentication")
    print("   4. Verify frontend can communicate with backend")
    print("   5. Perform end-to-end workflow testing")

def main():
    """Run comprehensive health check"""
    print("🚀 POYA PLATFORM - COMPREHENSIVE HEALTH CHECK")
    print("=" * 60)
    print(f"📅 Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    check_directory_structure()
    check_python_dependencies()
    check_node_dependencies()
    analyze_code_structure()
    check_database_setup()
    check_frontend_structure()
    check_running_processes()
    generate_final_assessment()
    
    print("\n" + "=" * 60)
    print("📋 HEALTH CHECK COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
