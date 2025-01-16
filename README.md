# secure-file-share
# Abnormal Security Project


A secure file sharing system built with Django REST Framework that supports encrypted file storage and secure download links.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- OpenSSL for generating certificates

## Setup Instructions

### 1. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# For Windows:
venv\Scripts\activate
# For Unix or MacOS:
source venv/bin/activate
```

### 2. Create Environment Variables

Create a `.env` file in the root directory with the following variables:

```plaintext
# .env
PASSWORD=your_encryption_password_here
EMAIL_HOST_PASSWORD=your_email_host_password_here
SECRET_KEY=your_django_secret_key_here
```

Replace the placeholder values with your actual secure values.

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Generate SSL Certificates

For development HTTPS, generate self-signed certificates:

```bash
# For Windows:
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# For Unix/MacOS:
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

When prompted, fill in the certificate details. For local development, you can use defaults, but make sure to set "Common Name" to "localhost".

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Start the Development Server

For HTTP (standard):
```bash
python run_dev.py
```

For HTTPS (secure):
```bash
python run_dev_secure.py
```

The server will start on:
- HTTP: http://localhost:8000
- HTTPS: https://127.0.0.1:8000

## API Endpoints

### Authentication
- `POST /user/register/` - Register new user
- `POST /user/verify-otp/` - Verify OTP
- `POST /user/login/` - Login user
- `POST /user/logout/` - Logout user

### File Operations
- `POST /file/upload/` - Upload file
- `GET /file/download/<file_id>/` - Download file
- `GET /secure-link/<file_id>/` - Generate secure download link
- `GET /file/download/<token>/` - Download file using secure link
- `GET /user/files/` - List user's files

## Security Notes

1. The development server with SSL is not suitable for production use.
2. Self-signed certificates will show security warnings in browsers.
3. Use strong passwords for all environment variables.
4. Keep your `.env` file secure and never commit it to version control in this case, I have added it to the .gitignore file.

## Browser Security Warning

When accessing the HTTPS development server, you'll see a security warning because we're using a self-signed certificate. This is normal for development. In a production environment, you should use properly signed certificates.

To bypass the warning in development:
1. Click "Advanced" or "More Information"
2. Click "Proceed to localhost (unsafe)" or "Accept the Risk and Continue"


## TO run the Dockerized version of the application:

1. Get into the secure-file-share directory (root directory).
2. Create the image by running the command:  docker build -t secure-file-share .
3. Run the container by : docker run -p 8000:8000 secure-file-share

## Troubleshooting

### Common Issues:

1. **Certificate Issues**
   ```bash
   # Regenerate certificates if you have issues
   rm cert.pem key.pem
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
   ```

2. **Environment Variables**
   ```bash
   # Check if environment variables are loaded
   python
   >>> import os
   >>> print(os.getenv('SECRET_KEY'))
   ```

3. **Port Already in Use**
   ```bash
   # Kill process using the port (Windows)
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F

   # Kill process using the port (Unix/MacOS)
   lsof -i :8000
   kill -9 <PID>
   ```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
NIL