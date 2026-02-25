---
name: flask-development
description: Flask web development covering blueprints, SQLAlchemy models, Flask-Login authentication, WTForms validation, REST APIs with Flask-RESTX, Celery task queues, testing with pytest, and production deployment.
---

# Flask Development

This skill should be used when building web applications with Flask. It covers blueprints, database models, authentication, forms, REST APIs, async tasks, and testing.

## When to Use This Skill

Use this skill when you need to:

- Build web applications or REST APIs with Flask
- Structure large Flask applications with blueprints
- Implement authentication with Flask-Login
- Set up SQLAlchemy models and migrations
- Add background tasks with Celery

## Application Factory

```python
# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    return app
```

## Configuration

```python
# config.py
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://localhost/myapp"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
```

## Models

```python
# app/models.py
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    posts = db.relationship("Post", backref="author", lazy="dynamic")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    published = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))
```

## Blueprint with Authentication

```python
# app/auth/__init__.py
from flask import Blueprint
bp = Blueprint("auth", __name__)
from app.auth import routes

# app/auth/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm
from app.models import User
from app import db

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))
        flash("Invalid email or password", "error")

    return render_template("auth/login.html", form=form)

@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
```

## REST API

```python
# app/api/routes.py
from flask import jsonify, request, abort
from flask_login import login_required, current_user
from app.api import bp
from app.models import Post
from app import db

@bp.route("/posts", methods=["GET"])
def get_posts():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pagination = Post.query.filter_by(published=True).order_by(
        Post.created_at.desc()
    ).paginate(page=page, per_page=per_page)

    return jsonify({
        "items": [post_to_dict(p) for p in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
    })

@bp.route("/posts", methods=["POST"])
@login_required
def create_post():
    data = request.get_json()
    if not data or not data.get("title"):
        abort(400, description="Title is required")

    post = Post(
        title=data["title"],
        body=data.get("body", ""),
        author_id=current_user.id,
    )
    db.session.add(post)
    db.session.commit()
    return jsonify(post_to_dict(post)), 201

@bp.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e.description)), 400

@bp.errorhandler(404)
def not_found(e):
    return jsonify(error="Resource not found"), 404

def post_to_dict(post: Post) -> dict:
    return {
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "author": post.author.username,
        "created_at": post.created_at.isoformat(),
    }
```

## Testing

```python
# tests/conftest.py
import pytest
from app import create_app, db as _db
from config import TestConfig

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    return _db

# tests/test_api.py
def test_get_posts(client, db):
    from app.models import User, Post
    user = User(email="test@test.com", username="tester")
    user.set_password("password")
    db.session.add(user)
    post = Post(title="Test", body="Content", published=True, author=user)
    db.session.add(post)
    db.session.commit()

    response = client.get("/api/v1/posts")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Test"

def test_create_post_unauthenticated(client):
    response = client.post("/api/v1/posts", json={"title": "New"})
    assert response.status_code == 401
```

## Celery Tasks

```python
# app/tasks.py
from celery import Celery

celery = Celery(__name__)

@celery.task
def send_email_async(to: str, subject: str, body: str):
    from app.email import send_email
    send_email(to=to, subject=subject, body=body)

# Usage in route
@bp.route("/contact", methods=["POST"])
def contact():
    send_email_async.delay(
        to="admin@example.com",
        subject="New contact",
        body=request.form["message"],
    )
    return jsonify(message="Sent"), 202
```

## CLI Commands

```bash
flask db init              # Initialize migrations
flask db migrate -m "msg"  # Generate migration
flask db upgrade           # Apply migrations
flask run --debug          # Development server
flask shell                # Interactive shell
```

## Additional Resources

- Flask docs: https://flask.palletsprojects.com/
- Flask-SQLAlchemy: https://flask-sqlalchemy.readthedocs.io/
- Flask-Login: https://flask-login.readthedocs.io/
