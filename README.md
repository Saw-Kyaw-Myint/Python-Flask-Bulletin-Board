# FLASK PROJECT CONFIGURATION

## Packages

```
- python-dotenv
- Flask-SQLAlchemy
- Flask-Migrate
- flask-marshmallow
- Flask-Pydantic
- Flask-cors
- Flask-Limiter
- Flask-JWT-Extended
- Flask-Bcrypt
- Flask-Socketio
- Black
- Isort
```

## Support

Support Minimum feature for small `Api` project.<br>
No need to configure following basic requirement and support example code.

- Similar Laravel Folder Structure
- JWT
- Rate Limitation
- System Log File
- Api Error Handling
- MySQl
- Route
- Middleware
- Validation
- Controller
- Object-Relational Mapping
- Migration version
- Json Response Format
- Python File Formatting
- Soft delete
- Fake Data (Factories)

## Setup Instructions

### 1. Clone the repository

```bash
$ git clone https://github.com/Saw-Kyaw-Myint/python-Bulletin-Board.git

$ cd python-Bulletin-Board
```

### 2. Install dependencies

```
// if  had installed poetry, can skip this command
$ pip install poetry

$ poetry install --no-root
```

### 3. Activate the virtual environment

```
$ poetry self add poetry-plugin-shell
$ poetry shell

$ poetry env list
```

### 4. Copy .env.example to .env

```
$ cp .env.example .env
```

### 5. Configure Setting in .env

```
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=python_bulletin

# JWT configuration
JWT_SECRET_KEY=your_super_secret_key
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=86400
```

### 6. Run Database Migration

If fail use `poetry run flask db upgrade`

```
flask db upgrade
```

### 7. Run The Flask application Development

```
$ flask run --debug
```

### Run Format Before Commit

```
$ py format
```
