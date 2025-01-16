import os
import subprocess
import sys

def flush_data():
    """
    Flushes the database by dropping all tables.
    """
    print("Starting database flush...")
    result = os.system("python manage.py flush --noinput")
    print(f"Data flush completed with status: {result}")
    
def makemigrations():
    """
    Creates new migration files for changes in models.
    """
    print("Starting makemigrations...")
    result = os.system("python manage.py makemigrations")
    print(f"Makemigrations completed with status: {result}")

def migrate():
    """
    Applies migrations to the database.
    """
    print("Starting migrations...")
    result = os.system("python manage.py migrate")
    print(f"Migrations completed with status: {result}")

def runserver():
    """
    Starts the development server with Docker-specific settings.
    """
    print("Starting development server...")
    print("Current working directory:", os.getcwd())
    print("Files in current directory:", os.listdir())
    
    # Use subprocess to get more detailed output
    try:
        subprocess.run([
             "python", 
            "manage.py", 
            "runserver_plus", 
            "0.0.0.0:8000",
            "--cert-file", 
            "../certificates/localhost.crt",
            "--key-file",
            "../certificates/localhost.key",
            "--verbosity=2",
            "--noreload"  # Disable auto-reload to see clearer logs
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Starting run_dev.py")
    print("Python version:", sys.version)
    
    flush_data()
    makemigrations()
    migrate()
    runserver()