#!/usr/bin/env python3
"""
Setup script for SMS Webhook Django project
This script helps you get the project up and running quickly
"""

import os
import sys
import subprocess
import getpass
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e}")
        if e.stdout:
            print(f"   Output: {e.stdout}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['django', 'djangorestframework', 'django-cors-headers']
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is not installed")
            return False
    return True

def create_env_file():
    """Create .env file from template"""
    env_file = Path('.env')
    env_example = Path('env.example')
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return False
    
    # Generate a random secret key
    import secrets
    secret_key = ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50))
    
    # Read template and replace placeholder
    with open(env_example, 'r') as f:
        content = f.read()
    
    content = content.replace('your-secret-key-here', secret_key)
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ .env file created with generated secret key")
    return True

def setup_database():
    """Set up the database with migrations"""
    commands = [
        ("python manage.py makemigrations", "Creating database migrations"),
        ("python manage.py migrate", "Applying database migrations"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True

def create_superuser():
    """Create a superuser account"""
    print("\n👤 Superuser Account Creation")
    print("=" * 30)
    
    try:
        username = input("Username (default: admin): ").strip() or "admin"
        email = input("Email (optional): ").strip() or ""
        
        # Use getpass for secure password input
        password = getpass.getpass("Password: ")
        if not password:
            print("❌ Password cannot be empty")
            return False
        
        # Create superuser using Django management command
        command = f"echo 'from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser(\"{username}\", \"{email}\", \"{password}\")' | python manage.py shell"
        
        if run_command(command, "Creating superuser account"):
            print(f"✅ Superuser '{username}' created successfully")
            return True
        else:
            return False
            
    except KeyboardInterrupt:
        print("\n❌ Superuser creation cancelled")
        return False
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        return False

def collect_static():
    """Collect static files"""
    return run_command("python manage.py collectstatic --noinput", "Collecting static files")

def main():
    """Main setup function"""
    print("🚀 SMS Webhook Django Project Setup")
    print("=" * 40)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ manage.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    print("\n📋 Prerequisites check completed")
    
    # Create environment file
    if not create_env_file():
        print("❌ Failed to create .env file")
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print("❌ Database setup failed")
        sys.exit(1)
    
    # Collect static files
    if not collect_static():
        print("❌ Static files collection failed")
        sys.exit(1)
    
    # Ask about superuser creation
    print("\n🤔 Superuser Account")
    print("A superuser account is required to access the Django admin interface.")
    
    create_super = input("Create superuser account now? (y/n, default: y): ").strip().lower()
    if create_super in ['', 'y', 'yes']:
        if not create_superuser():
            print("⚠️  Superuser creation failed. You can create one later with:")
            print("   python manage.py createsuperuser")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📱 Next steps:")
    print("1. Start the development server:")
    print("   python manage.py runserver")
    print("\n2. Open your browser and navigate to:")
    print("   Dashboard: http://localhost:8000/")
    print("   Admin: http://localhost:8000/admin/")
    print("   API: http://localhost:8000/api/")
    print("\n3. Configure your SMSMobileAPI webhook URL:")
    print("   http://localhost:8000/webhook/sms/")
    print("\n4. Test the webhook with:")
    print("   python test_webhook.py")
    
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()
