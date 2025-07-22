# PaperHub - Research Paper Management System

A modern web application for managing research papers with automatic metadata extraction, categorization, and search functionality. Built with Flask following a modular architecture.

## Features

- 📚 **Paper Management**: Upload and organize PDF research papers
- 🔐 **User Authentication**: Secure login and registration system
- 📁 **Categorization**: Create custom categories with colors
- 🔍 **Search**: Find papers by title, authors, or abstract
- 🤖 **AI Metadata Extraction**: Automatic extraction using OpenRouter API
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Project Structure

```
paper-hub/
├── app/                    # Application package
│   ├── __init__.py        # Application factory
│   ├── models.py          # Database models
│   ├── auth/              # Authentication blueprint
│   │   ├── __init__.py
│   │   └── routes.py      # Login, register, logout routes
│   ├── main/              # Main blueprint
│   │   ├── __init__.py
│   │   ├── routes.py      # Dashboard, upload, paper routes
│   │   └── utils.py       # Helper functions
│   ├── templates/         # HTML templates
│   │   ├── base.html      # Base template
│   │   ├── auth/          # Authentication templates
│   │   └── main/          # Main app templates
│   └── static/            # CSS, JS, images
├── config.py              # Configuration classes
├── requirements.txt       # Python dependencies
├── run.py                 # Application entry point
└── uploads/              # Uploaded PDF files
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd paper-hub
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables (optional)**
   ```bash
   export FLASK_CONFIG=development
   export SECRET_KEY=your-secret-key-here
   export OPENROUTER_API_KEY=your-api-key-here
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## Configuration

The application supports multiple configuration environments:

- **Development**: Debug mode enabled, SQLite database
- **Production**: Debug disabled, optimized for deployment
- **Testing**: In-memory database for unit tests

Configuration is managed in `config.py` and can be selected via the `FLASK_CONFIG` environment variable.

## API Integration

### OpenRouter API

To enable automatic metadata extraction from PDFs:

1. Get an API key from [OpenRouter](https://openrouter.ai/keys)
2. Set the environment variable:
   ```bash
   export OPENROUTER_API_KEY=your-api-key-here
   ```

Without an API key, the application will use basic text extraction methods.

## Architecture

### Blueprints

The application uses Flask blueprints for modular organization:

- **auth**: Handles user authentication (login, register, logout)
- **main**: Core functionality (dashboard, paper management, categories)

### Database Models

- **User**: User accounts with email/password authentication
- **Paper**: Research papers with metadata
- **Category**: Custom categories for organizing papers

### Application Factory Pattern

The app uses the application factory pattern (`create_app()`) which:
- Allows easy testing with different configurations
- Prevents circular imports
- Makes the app more modular and scalable

## Usage

1. **Register an account** with your email and password
2. **Create categories** to organize your papers
3. **Upload PDF files** - metadata will be extracted automatically
4. **Search and filter** papers by category or text
5. **View PDFs** directly in the browser

## Development

### Adding New Features

1. Create a new blueprint in `app/` if needed
2. Add routes in the blueprint's `routes.py`
3. Create templates in the appropriate subdirectory
4. Register the blueprint in `app/__init__.py`

### Database Changes

After modifying models, create and apply migrations:
```python
from app import create_app
from app.models import db

app = create_app()
with app.app_context():
    db.create_all()
```

## Security Notes

- Change the `SECRET_KEY` in production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Regularly update dependencies

## License

This project is open source and available under the MIT License. 