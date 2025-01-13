import os

def flush_data():
    """
    Flushes the database by dropping all tables.
    """
    os.system("python manage.py flush --noinput")
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
    Starts the development server using the certificates in the generated certificates folder.
    """
    print("Starting development server...")
    os.system("python manage.py runserver_plus --cert-file ../certificates/localhost.crt --key-file ../certificates/localhost.key")
    print("Server started.")

if __name__ == "__main__":
    flush_data()  # Default to "yes" for flushing data-> remove --noinput for removing the default option
    makemigrations()
    migrate()
    runserver()