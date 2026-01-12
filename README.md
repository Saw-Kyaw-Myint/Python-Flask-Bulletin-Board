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
$ git clone https://github.com/Saw-Kyaw-Myint/python-flask-folder-structure-configuration.git

$ cd python-flask-folder-structure-configuration
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

### 5. Run the Flask application

```
$ flask run
```

### Run Format

```
$ py format
```

## <u>Reference</u>

https://www.digitalocean.com/community/tutorials/how-to-perform-flask-sqlalchemy-migrations-using-flask-migrate

---

## <u>Project Reference</u>

https://github.com/demoskp/flask-marshmallow-tutorial/blob/master/poetry.lock
