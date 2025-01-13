import os
import subprocess

def flush_data():
    """
    Flushes the database by dropping all tables.
    """
    os.system("python manage.py flush")
    print("Data flushed.")
    
def makemigrations():
    """
    Creates new migration files for changes in models.
    """
    print("Creating migrations...")
    os.system("python manage.py makemigrations")
    print("Migrations created.")

def migrate():
    """
    Applies migrations to the database.
    """
    print("Applying migrations...")
    os.system("python manage.py migrate")
    print("Migrations applied.")

def runserver():
    """
    Starts the development server.
    """
    print("Starting development server...")
    os.system("python manage.py runserver")
    print("Server started.")

if __name__ == "__main__":
    flush_data()  # Default to "yes" for flushing data
    makemigrations()
    migrate()
    runserver()